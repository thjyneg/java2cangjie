#!/usr/bin/env python3
"""
j2cj 工作流自动化工具

完整的Java到Cangjie翻译工作流：
1. 扫描Java源文件
2. 运行j2cj转换
3. 分析错误标记
4. 生成错误分析表
5. 生成Adapter stub类和cjmap映射

用法:
    python3 j2cj_workflow.py <java_source_dir> [options]

示例:
    python3 j2cj_workflow.py ./java/src --output ./cangjie_output --classpath ./lib/*
    python3 j2cj_workflow.py ./java/src -o ./output -cp ./deps/* --mode codestyle
"""

import os
import sys
import re
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple


@dataclass
class JavaFileInfo:
    """Java文件信息"""
    path: str
    package: str
    class_name: str
    imports: List[str] = field(default_factory=list)


@dataclass
class ErrorMarker:
    """错误标记"""
    java_class: str
    member_type: str  # 'method', 'constructor', 'field'
    member_name: str
    full_signature: str
    file: str
    line: int
    context: str = ""


@dataclass
class AnalysisResult:
    """分析结果"""
    java_files: List[str]
    output_dir: str
    error_markers: List[ErrorMarker]
    class_summary: Dict[str, Dict]  # 类名 -> {methods, constructors, fields, count}


class JavaScanner:
    """Java源文件扫描器"""

    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.java_files: List[JavaFileInfo] = []

    def scan(self) -> List[str]:
        """扫描所有Java文件"""
        self.java_files = []

        for java_path in self.source_dir.rglob("*.java"):
            info = self._parse_java_file(java_path)
            if info:
                self.java_files.append(info)

        return [str(f.path) for f in self.java_files]

    def _parse_java_file(self, file_path: Path) -> Optional[JavaFileInfo]:
        """解析Java文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            package = ""
            for line in content.split('\n'):
                if line.startswith('package '):
                    package = line.split('package ')[1].split(';')[0].strip()
                    break

            class_name = file_path.stem

            imports = []
            for line in content.split('\n'):
                if line.startswith('import '):
                    imports.append(line.split('import ')[1].split(';')[0].strip())

            return JavaFileInfo(
                path=str(file_path),
                package=package,
                class_name=class_name,
                imports=imports
            )
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}", file=sys.stderr)
            return None

    def get_classpath_entries(self) -> List[str]:
        """获取需要的外部依赖（从import分析）"""
        external_deps = set()
        for info in self.java_files:
            for imp in info.imports:
                # 跳过java.*和javax.*（j2cj内置处理）
                if not imp.startswith('java.') and not imp.startswith('javax.'):
                    external_deps.add(imp.split('.')[0])
        return list(external_deps)


class J2cjRunner:
    """j2cj工具运行器"""

    def __init__(self, j2cj_jar: str, output_dir: str):
        self.j2cj_jar = j2cj_jar
        self.output_dir = output_dir
        self.log_file = os.path.join(output_dir, ".j2cj_log.txt")

    def run(self, java_files: List[str],
            classpath: Optional[str] = None,
            mode: str = "codestyle",
            verbose: bool = False) -> Tuple[bool, str]:
        """运行j2cj转换"""
        os.makedirs(self.output_dir, exist_ok=True)

        # 构建命令
        cmd = [
            "java",
            f"--patch-module=jdk.compiler={self.j2cj_jar}",
            "-m", "jdk.compiler/com.excelsior.j2cj.main.Main",
            "-d", self.output_dir,
            f"--mode={mode}",
        ]

        if classpath:
            cmd.extend(["-cp", classpath])

        cmd.extend(java_files)

        if verbose:
            print(f"Running: {' '.join(cmd[:10])}... ({len(java_files)} files)")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            # 保存日志
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"Command: {' '.join(cmd)}\n\n")
                f.write(f"Exit Code: {result.returncode}\n\n")
                f.write("=== STDOUT ===\n")
                f.write(result.stdout)
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr)

            return result.returncode == 0, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            return False, "Error: j2cj process timed out after 5 minutes"
        except FileNotFoundError:
            return False, f"Error: Java not found. Please ensure Java is installed."
        except Exception as e:
            return False, f"Error: {str(e)}"


class ErrorAnalyzer:
    """错误标记分析器"""

    PATTERNS = {
        'missing_method': re.compile(
            r'<-- Missing mapping for ([\w.$]+) member: (\w+) -->'
        ),
        'missing_constructor': re.compile(
            r'<-- Missing mapping for ([\w.$]+) constructor: (\w+) -->'
        ),
        'missing_field': re.compile(
            r'<-- Missing mapping for ([\w.$]+) (?:static )?field: (\w+) -->'
        ),
        'invalid_symbol': re.compile(
            r'<-- Invalid symbol: (.+?) -->'
        ),
        'unsupported': re.compile(
            r"<-- (Java keyword|Generic|.*not supported) -->"
        ),
    }

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.error_markers: List[ErrorMarker] = []
        self.class_summary: Dict[str, Dict] = defaultdict(
            lambda: {'methods': {}, 'constructors': {}, 'fields': {}, 'total': 0}
        )

    def analyze(self) -> Tuple[List[ErrorMarker], Dict[str, Dict]]:
        """分析所有.cj文件中的错误标记"""
        self.error_markers = []
        self.class_summary = defaultdict(
            lambda: {'methods': {}, 'constructors': {}, 'fields': {}, 'total': 0}
        )

        for cj_file in Path(self.output_dir).rglob("*.cj"):
            self._analyze_file(cj_file)

        return self.error_markers, dict(self.class_summary)

    def _analyze_file(self, file_path: Path):
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            rel_path = file_path.relative_to(self.output_dir)

            for line_no, line in enumerate(lines, 1):
                self._parse_line(line, str(rel_path), line_no)
        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}", file=sys.stderr)

    def _parse_line(self, line: str, file: str, line_no: int):
        """解析单行"""
        # 方法
        for match in self.PATTERNS['missing_method'].finditer(line):
            self._add_marker(
                java_class=match.group(1),
                member_type='method',
                member_name=match.group(2),
                file=file,
                line=line_no
            )

        # 构造函数
        for match in self.PATTERNS['missing_constructor'].finditer(line):
            self._add_marker(
                java_class=match.group(1),
                member_type='constructor',
                member_name='<init>',
                file=file,
                line=line_no
            )

        # 字段
        for match in self.PATTERNS['missing_field'].finditer(line):
            self._add_marker(
                java_class=match.group(1),
                member_type='field',
                member_name=match.group(2),
                file=file,
                line=line_no
            )

    def _add_marker(self, java_class: str, member_type: str, member_name: str,
                    file: str, line: int):
        """添加错误标记"""
        marker = ErrorMarker(
            java_class=java_class,
            member_type=member_type,
            member_name=member_name,
            full_signature=f"{java_class}.{member_name}",
            file=file,
            line=line
        )
        self.error_markers.append(marker)

        # 更新统计
        summary = self.class_summary[java_class]
        key = f"{member_type}s"
        if member_name not in summary[key]:
            summary[key][member_name] = {'count': 0, 'files': set()}
        summary[key][member_name]['count'] += 1
        summary[key][member_name]['files'].add(file)
        summary['total'] += 1


class ReportGenerator:
    """报告生成器"""

    def generate_error_table(self, class_summary: Dict[str, Dict],
                            output_dir: str) -> str:
        """生成错误分析表格"""
        lines = []

        lines.append("# j2cj 错误分析报告")
        lines.append("")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"输出目录: {output_dir}")
        lines.append(f"缺失映射的类: {len(class_summary)}")
        lines.append("")

        # 按总使用次数排序
        sorted_classes = sorted(
            class_summary.items(),
            key=lambda x: -x[1]['total']
        )

        # 汇总表
        lines.append("## 1. 错误汇总表")
        lines.append("")
        lines.append("| 序号 | Java类 | 方法数 | 构造函数数 | 字段数 | 总使用次数 |")
        lines.append("|------|--------|--------|------------|--------|------------|")

        for idx, (java_class, summary) in enumerate(sorted_classes, 1):
            method_count = len(summary['methods'])
            ctor_count = len(summary['constructors'])
            field_count = len(summary['fields'])
            total = summary['total']
            lines.append(f"| {idx} | `{java_class}` | {method_count} | {ctor_count} | {field_count} | {total} |")

        lines.append("")

        # 详细表
        lines.append("## 2. 详细错误列表")
        lines.append("")

        for java_class, summary in sorted_classes:
            lines.append(f"### {java_class}")
            lines.append("")
            lines.append("| 类型 | 成员名 | 使用次数 | 文件数 |")
            lines.append("|------|--------|----------|--------|")

            # 方法
            for name, info in sorted(summary['methods'].items(),
                                    key=lambda x: -x[1]['count']):
                lines.append(f"| 方法 | `{name}` | {info['count']} | {len(info['files'])} |")

            # 构造函数
            for name, info in sorted(summary['constructors'].items(),
                                    key=lambda x: -x[1]['count']):
                lines.append(f"| 构造函数 | `{name}` | {info['count']} | {len(info['files'])} |")

            # 字段
            for name, info in sorted(summary['fields'].items(),
                                    key=lambda x: -x[1]['count']):
                lines.append(f"| 字段 | `{name}` | {info['count']} | {len(info['files'])} |")

            lines.append("")

        return '\n'.join(lines)


class AdapterGenerator:
    """Adapter stub类和cjmap生成器"""

    TYPE_MAP = {
        'void': 'Unit',
        'int': 'Int32', 'long': 'Int64', 'short': 'Int16', 'byte': 'Int8',
        'char': 'Rune', 'float': 'Float32', 'double': 'Float64',
        'boolean': 'Bool', 'String': 'String', 'Object': 'Any',
    }

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        # Adapter放在输出目录下的adapters模块中
        self.adapter_module_dir = os.path.join(output_dir, "adapters")
        self.adapter_src_dir = os.path.join(self.adapter_module_dir, "src", "adapters")
        self.cjmap_file = os.path.join(output_dir, "adapters.cjmap")

    def generate(self, class_summary: Dict[str, Dict]) -> Tuple[List[str], str]:
        """生成Adapter类和cjmap"""
        os.makedirs(self.adapter_src_dir, exist_ok=True)

        # 生成模块cjpm.toml
        self._generate_cjpm_toml()

        # 生成empty.cj确保目录被识别
        self._generate_empty_files()

        generated_files = []

        for java_class, summary in class_summary.items():
            file_path = self._generate_adapter(java_class, summary)
            if file_path:
                generated_files.append(file_path)

        cjmap_content = self._generate_cjmap(class_summary)
        with open(self.cjmap_file, 'w', encoding='utf-8') as f:
            f.write(cjmap_content)

        return generated_files, self.cjmap_file

    def _generate_cjpm_toml(self):
        """生成adapters模块的cjpm.toml"""
        content = '''[package]
name = "adapters"
version = "1.0.0"
description = "Auto-generated adapter stubs for missing Java APIs"
cangjie-version = "0.53.4"

[dependencies]

[build]
output-type = "library"
'''
        toml_path = os.path.join(self.adapter_module_dir, "cjpm.toml")
        with open(toml_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_empty_files(self):
        """生成empty.cj确保目录结构被识别"""
        # adapters/src/adapters/empty.cj
        empty_content = "package adapters\n"
        empty_file = os.path.join(self.adapter_src_dir, "empty.cj")
        with open(empty_file, 'w', encoding='utf-8') as f:
            f.write(empty_content)

        # 为每个子包生成empty.cj
        packages = set()
        for java_class in self.class_summary if hasattr(self, 'class_summary') else []:
            parts = java_class.split('.')
            for i in range(len(parts)):
                packages.add('.'.join(parts[:i+1]))

        for pkg in sorted(packages):
            pkg_path = os.path.join(self.adapter_src_dir, *pkg.split('.'))
            os.makedirs(pkg_path, exist_ok=True)
            empty_file = os.path.join(pkg_path, "empty.cj")
            with open(empty_file, 'w', encoding='utf-8') as f:
                f.write(f"package adapters.{pkg}\n")

    def _generate_adapter(self, java_class: str, summary: Dict) -> Optional[str]:
        """生成单个Adapter类"""
        if not summary['methods'] and not summary['constructors'] and not summary['fields']:
            return None

        # 包名和类名
        parts = java_class.split('.')
        simple_name = parts[-1]
        package = "adapters." + ".".join(parts[:-1]) if len(parts) > 1 else "adapters"

        # 文件路径: adapters/src/adapters/java/io/OutputStream.cj
        file_dir = os.path.join(self.adapter_src_dir, *parts[:-1]) if len(parts) > 1 else self.adapter_src_dir
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, f"{simple_name}.cj")

        # 生成内容
        lines = []
        lines.append(f"package {package}")
        lines.append("")
        lines.append("/*")
        lines.append(f" * Auto-generated Adapter for {java_class}")
        lines.append(f" * 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(" *")
        lines.append(" * 这是一个最小化stub实现，仅用于编译通过。")
        lines.append(" * 如需运行时功能，请实现具体逻辑。")
        lines.append(" */")
        lines.append("")
        lines.append(f"public open class {simple_name} {{")
        lines.append("")

        # 构造函数
        if summary['constructors']:
            lines.append("    // Constructors")
            for name, info in summary['constructors'].items():
                lines.append("    public init() { }")
            lines.append("")

        # 字段
        if summary['fields']:
            lines.append("    // Fields")
            for name, info in summary['fields'].items():
                lines.append(f"    public mut prop {name}: Any = None")
            lines.append("")

        # 方法
        if summary['methods']:
            lines.append("    // Methods")
            for name, info in sorted(summary['methods'].items(),
                                    key=lambda x: -x[1]['count']):
                lines.append(f"    // {name}() - {info['count']} uses in {len(info['files'])} files")
                lines.append(f"    public func {name}(): Unit {{ }}")
                lines.append("")

        lines.append("}")
        lines.append("")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return file_path

    def _generate_cjmap(self, class_summary: Dict[str, Dict]) -> str:
        """生成cjmap映射"""
        lines = []
        lines.append("// Auto-generated cjmap mappings")
        lines.append(f"// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("// 使用说明:")
        lines.append("// 1. 将此文件放置在j2cj工作目录")
        lines.append("// 2. Adapter类会自动映射到对应的Java类")
        lines.append("")

        for java_class, summary in sorted(class_summary.items(),
                                          key=lambda x: -x[1]['total']):
            parts = java_class.split('.')
            simple_name = parts[-1]
            package = "adapters." + ".".join(parts[:-1]) if len(parts) > 1 else "adapters"
            adapter_class = f"{package}.{simple_name}"

            lines.append(f"// {java_class} ({summary['total']} uses)")
            lines.append(f"mapping {java_class} => {adapter_class} {{")

            for name in summary['constructors']:
                lines.append(f"    <init>")

            for name in summary['methods']:
                lines.append(f"    {name}")

            for name in summary['fields']:
                lines.append(f"    {name}")

            lines.append("}")
            lines.append("")

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='j2cj工作流自动化工具 - 完整的Java到Cangjie翻译流程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python3 j2cj_workflow.py ./java/src -o ./cangjie_output

  # 指定classpath
  python3 j2cj_workflow.py ./java/src -o ./output -cp "./lib/*:./deps/*"

  # 详细输出
  python3 j2cj_workflow.py ./java/src -o ./output -v
        """
    )

    parser.add_argument('java_source', help='Java源码目录')
    parser.add_argument('-o', '--output', required=True,
                        help='Cangjie输出目录')
    parser.add_argument('-cp', '--classpath', default=None,
                        help='Java classpath (用:或;分隔)')
    parser.add_argument('--mode', choices=['codestyle', 'semantic'],
                        default='codestyle',
                        help='翻译模式 (默认: codestyle)')
    parser.add_argument('--j2cj', default=None,
                        help='j2cj.jar路径 (默认: ./j2cj_tool/j2cj.jar)')
    parser.add_argument('--skip-translate', action='store_true',
                        help='跳过翻译步骤，仅分析错误')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细输出')

    args = parser.parse_args()

    # 确定j2cj.jar路径
    if args.j2cj:
        j2cj_jar = args.j2cj
    else:
        script_dir = Path(__file__).parent
        j2cj_jar = str(script_dir.parent / "j2cj_tool" / "j2cj.jar")

    if not os.path.exists(j2cj_jar):
        print(f"Error: j2cj.jar not found at {j2cj_jar}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.java_source):
        print(f"Error: {args.java_source} is not a directory", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("j2cj 工作流自动化")
    print("=" * 60)
    print()

    # Step 1: 扫描Java文件
    print("Step 1: 扫描Java源文件...")
    scanner = JavaScanner(args.java_source)
    java_files = scanner.scan()
    print(f"  找到 {len(java_files)} 个Java文件")

    if args.verbose:
        print(f"  外部依赖: {scanner.get_classpath_entries()}")

    # Step 2: 运行j2cj
    if not args.skip_translate:
        print()
        print("Step 2: 运行j2cj转换...")
        runner = J2cjRunner(j2cj_jar, args.output)
        success, output = runner.run(
            java_files=java_files,
            classpath=args.classpath,
            mode=args.mode,
            verbose=args.verbose
        )
        if success:
            print("  转换成功!")
        else:
            print(f"  转换完成 (有警告/错误)")
            if args.verbose:
                print(f"  日志: {runner.log_file}")
    else:
        print()
        print("Step 2: 跳过翻译 (使用现有输出)")
        # 确保输出目录存在
        os.makedirs(args.output, exist_ok=True)

    # Step 3: 分析错误
    print()
    print("Step 3: 分析错误标记...")
    analyzer = ErrorAnalyzer(args.output)
    error_markers, class_summary = analyzer.analyze()
    print(f"  找到 {len(error_markers)} 个错误标记")
    print(f"  涉及 {len(class_summary)} 个Java类")

    # Step 4: 生成报告
    print()
    print("Step 4: 生成错误分析报告...")
    report_gen = ReportGenerator()
    report_content = report_gen.generate_error_table(class_summary, args.output)
    report_file = os.path.join(args.output, "error_analysis_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"  报告: {report_file}")

    # Step 5: 生成Adapter
    print()
    print("Step 5: 生成Adapter stub和cjmap...")
    adapter_gen = AdapterGenerator(args.output)
    adapter_files, cjmap_file = adapter_gen.generate(class_summary)
    print(f"  生成 {len(adapter_files)} 个Adapter文件")
    print(f"  cjmap: {cjmap_file}")

    # 总结
    print()
    print("=" * 60)
    print("完成!")
    print("=" * 60)
    print()
    print("生成的文件:")
    print(f"  输出目录: {args.output}/")
    print(f"  错误报告: {report_file}")
    print(f"  Adapter目录: {args.output}/adapters/")
    print(f"  cjmap映射: {cjmap_file}")
    print()
    print("下一步:")
    print("  1. 查看错误报告了解缺失的映射")
    print("  2. 根据需要修改Adapter实现")
    print("  3. 运行 'cjpm build' 验证编译")


if __name__ == '__main__':
    main()
