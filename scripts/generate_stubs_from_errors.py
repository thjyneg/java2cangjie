#!/usr/bin/env python3
"""
从j2cj错误标记自动生成Cangjie stub类和cjmap映射

功能:
1. 扫描j2cj输出中的错误标记
2. 解析缺失的Java类、方法、构造函数、字段
3. 生成Cangjie stub类/接口（空实现，可编译）
4. 生成对应的cjmap映射规则

用法:
    python generate_stubs_from_errors.py <output_dir> --stub-dir ./stubs --cjmap ./custom.cjmap

生成的文件结构:
    stubs/
    ├── cjpm.toml              # 项目配置
    ├── src/
    │   └── stubs/
    │       └── java/
    │           ├── io/
    │           │   ├── OutputStream.cj
    │           │   └── InputStream.cj
    │           └── lang/
    │               ├── String.cj
    │               └── System.cj
    └── custom.cjmap           # 映射规则
"""

import re
import os
import sys
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple


@dataclass
class JavaMethod:
    """Java方法信息"""
    name: str
    params: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    is_static: bool = False
    count: int = 1


@dataclass
class JavaField:
    """Java字段信息"""
    name: str
    type_: str
    is_static: bool = False
    count: int = 1


@dataclass
class JavaClass:
    """Java类信息"""
    full_name: str  # e.g., java.util.Collections
    methods: Dict[str, JavaMethod] = field(default_factory=dict)
    constructors: Dict[str, int] = field(default_factory=dict)  # 签名 -> 次数
    fields: Dict[str, JavaField] = field(default_factory=dict)
    is_interface: bool = False
    is_enum: bool = False

    @property
    def package(self) -> str:
        return ".".join(self.full_name.split(".")[:-1])

    @property
    def simple_name(self) -> str:
        return self.full_name.split(".")[-1]

    def to_stub_package(self) -> str:
        """转换为stub包名
        java.util.Collections -> stubs.java.util
        """
        parts = self.full_name.split(".")
        if len(parts) > 1:
            return "stubs." + ".".join(parts[:-1])
        return "stubs"

    def to_stub_class_name(self) -> str:
        """stub类名就是简单名"""
        return self.simple_name

    def to_stub_full_name(self) -> str:
        """完整的stub类名"""
        return f"{self.to_stub_package()}.{self.simple_name}"


class ErrorMarkerParser:
    """错误标记解析器"""

    # 各种错误标记模式
    PATTERNS = {
        # Missing mapping for java.xxx.ClassName member: methodName
        'method': re.compile(
            r'<-- Missing mapping for ([\w.$]+) member: (\w+) -->'
        ),
        # Missing mapping for java.xxx.ClassName constructor: ClassName
        'constructor': re.compile(
            r'<-- Missing mapping for ([\w.$]+) constructor: (\w+) -->'
        ),
        # Missing mapping for java.xxx.ClassName static field: fieldName
        'static_field': re.compile(
            r'<-- Missing mapping for ([\w.$]+) static field: (\w+) -->'
        ),
        # Invalid symbol: xxx
        'invalid_symbol': re.compile(
            r'<-- Invalid symbol: (.+?) -->'
        ),
    }

    def __init__(self):
        self.classes: Dict[str, JavaClass] = {}

    def parse_directory(self, directory: str) -> int:
        """解析目录下所有.cj文件"""
        file_count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.cj'):
                    file_path = os.path.join(root, file)
                    self._parse_file(file_path)
                    file_count += 1
        return file_count

    def _parse_file(self, file_path: str):
        """解析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for line in content.split('\n'):
                self._parse_line(line)
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}", file=sys.stderr)

    def _parse_line(self, line: str):
        """解析单行"""

        # 方法
        for match in self.PATTERNS['method'].finditer(line):
            class_name = match.group(1)
            method_name = match.group(2)
            self._add_method(class_name, method_name)

        # 构造函数
        for match in self.PATTERNS['constructor'].finditer(line):
            class_name = match.group(1)
            self._add_constructor(class_name)

        # 静态字段
        for match in self.PATTERNS['static_field'].finditer(line):
            class_name = match.group(1)
            field_name = match.group(2)
            self._add_field(class_name, field_name, is_static=True)

    def _get_or_create_class(self, class_name: str) -> JavaClass:
        """获取或创建类"""
        if class_name not in self.classes:
            self.classes[class_name] = JavaClass(full_name=class_name)
        return self.classes[class_name]

    def _add_method(self, class_name: str, method_name: str):
        """添加方法"""
        jc = self._get_or_create_class(class_name)
        if method_name not in jc.methods:
            jc.methods[method_name] = JavaMethod(name=method_name)
        else:
            jc.methods[method_name].count += 1

    def _add_constructor(self, class_name: str):
        """添加构造函数"""
        jc = self._get_or_create_class(class_name)
        sig = "default"
        jc.constructors[sig] = jc.constructors.get(sig, 0) + 1

    def _add_field(self, class_name: str, field_name: str, is_static: bool = False):
        """添加字段"""
        jc = self._get_or_create_class(class_name)
        if field_name not in jc.fields:
            jc.fields[field_name] = JavaField(name=field_name, type_="Unit", is_static=is_static)
        else:
            jc.fields[field_name].count += 1


class StubGenerator:
    """Stub类生成器"""

    # Java类型到Cangjie类型的映射
    TYPE_MAP = {
        'void': 'Unit',
        'int': 'Int32',
        'long': 'Int64',
        'short': 'Int16',
        'byte': 'Byte',
        'char': 'Rune',
        'float': 'Float32',
        'double': 'Float64',
        'boolean': 'Bool',
        'String': 'String',
        'Object': 'Any',
        'Class': 'TypeInfo',
        'T': 'T',
        'E': 'E',
        'K': 'K',
        'V': 'V',
    }

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.generated_files: List[str] = []

    def generate_all(self, classes: Dict[str, JavaClass]) -> List[str]:
        """生成所有stub类"""
        self.generated_files = []

        # 生成cjpm.toml
        self._generate_cjpm_toml()

        # 生成empty.cj文件确保目录被识别
        self._generate_empty_files(classes)

        # 生成各个stub类
        for jc in classes.values():
            file_path = self._generate_stub(jc)
            if file_path:
                self.generated_files.append(file_path)

        return self.generated_files

    def _generate_cjpm_toml(self):
        """生成cjpm.toml"""
        content = '''[package]
name = "stubs"
version = "1.0.0"
description = "Auto-generated stub classes for missing Java APIs"

[dependencies]
'''
        os.makedirs(self.output_dir, exist_ok=True)
        toml_path = os.path.join(self.output_dir, "cjpm.toml")
        with open(toml_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_empty_files(self, classes: Dict[str, JavaClass]):
        """生成empty.cj文件确保目录结构被编译器识别"""
        # 收集所有需要的包目录
        packages = set()
        for jc in classes.values():
            pkg = jc.to_stub_package()
            # 为每个层级添加包
            parts = pkg.split(".")
            for i in range(1, len(parts) + 1):
                packages.add(".".join(parts[:i]))

        for pkg in sorted(packages):
            pkg_path = pkg.replace(".", "/")
            dir_path = os.path.join(self.output_dir, "src", pkg_path)
            os.makedirs(dir_path, exist_ok=True)

            empty_file = os.path.join(dir_path, "empty.cj")
            with open(empty_file, 'w', encoding='utf-8') as f:
                f.write(f"package {pkg}\n")

    def _generate_stub(self, jc: JavaClass) -> Optional[str]:
        """生成单个stub类"""
        if not jc.methods and not jc.constructors and not jc.fields:
            return None

        # 确定输出路径
        package_path = jc.to_stub_package().replace(".", "/")
        dir_path = os.path.join(self.output_dir, "src", package_path)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f"{jc.simple_name}.cj")

        # 生成内容
        content = self._generate_class_content(jc)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    def _generate_class_content(self, jc: JavaClass) -> str:
        """生成类内容"""
        lines = []

        # 包声明
        lines.append(f"package {jc.to_stub_package()}")
        lines.append("")
        lines.append("/*")
        lines.append(" * Auto-generated stub class")
        lines.append(f" * Original Java class: {jc.full_name}")
        lines.append(f" * Methods: {len(jc.methods)}, Constructors: {len(jc.constructors)}, Fields: {len(jc.fields)}")
        lines.append(" *")
        lines.append(" * NOTE: This is a minimal stub implementation for compilation.")
        lines.append(" *       Real implementation may be needed for runtime.")
        lines.append(" */")
        lines.append("")

        # 类声明
        keyword = "interface" if jc.is_interface else "open class"
        extends = ""

        # 特殊处理某些类
        if "Exception" in jc.simple_name or "Error" in jc.simple_name:
            extends = " <: Exception"
        elif "Throwable" in jc.simple_name:
            extends = " <: Exception"

        lines.append(f"public {keyword} {jc.simple_name}{extends} {{")
        lines.append("")

        # 构造函数
        if jc.constructors and not jc.is_interface:
            lines.append("    // Constructors")
            for sig, count in jc.constructors.items():
                lines.append(f"    public init() {{ }}")
            lines.append("")

        # 字段
        if jc.fields:
            lines.append("    // Fields")
            for fname, f in jc.fields.items():
                ftype = self._map_type(f.type_)
                if f.is_static:
                    lines.append(f"    public static let {fname}: {ftype} = {self._default_value(ftype)}")
                else:
                    lines.append(f"    public mut prop {fname}: {ftype}")
            lines.append("")

        # 方法
        if jc.methods:
            lines.append("    // Methods")
            for method in sorted(jc.methods.values(), key=lambda x: x.name):
                lines.append(f"    // {method.name}() - used {method.count} times")
                ret_type = self._map_type(method.return_type)
                ret_default = self._default_value(ret_type)
                lines.append(f"    public func {method.name}(): {ret_type} {{")
                lines.append(f"        return {ret_default}")
                lines.append("    }")
                lines.append("")

        lines.append("}")
        lines.append("")

        return '\n'.join(lines)

    def _map_type(self, java_type: Optional[str]) -> str:
        """映射Java类型到Cangjie类型"""
        if not java_type:
            return "Unit"
        # 去除泛型
        base_type = java_type.split("<")[0].split("[")[0].strip()
        return self.TYPE_MAP.get(base_type, "Any")

    def _default_value(self, cj_type: str) -> str:
        """返回类型的默认值"""
        defaults = {
            'Unit': '',
            'Int32': '0i32',
            'Int64': '0i64',
            'Int16': '0i16',
            'Byte': "0'b0",
            'Float32': '0.0f32',
            'Float64': '0.0f64',
            'Bool': 'false',
            'Rune': "r'\\0'",
            'String': '""',
        }
        if cj_type in defaults:
            return defaults[cj_type]
        return 'None'  # 对于对象类型返回None


class CjmapGenerator:
    """cjmap生成器"""

    def generate(self, classes: Dict[str, JavaClass]) -> str:
        """生成cjmap内容"""
        lines = []
        lines.append("// Auto-generated cjmap mappings")
        lines.append("// Generated by generate_stubs_from_errors.py")
        lines.append("")
        lines.append("// =====================================================")
        lines.append("// Usage Instructions:")
        lines.append("// =====================================================")
        lines.append("// 1. Copy this file to your working directory as 'custom.cjmap'")
        lines.append("// 2. Or place it alongside j2cj.jar (will override built-in mappings)")
        lines.append("// 3. The stubs/ directory should be in your project's dependencies")
        lines.append("//")
        lines.append("// Note: Stub classes provide minimal implementations for compilation.")
        lines.append("//       You may need to implement real functionality for runtime.")
        lines.append("// =====================================================")
        lines.append("")

        for jc in sorted(classes.values(), key=lambda x: x.full_name):
            mapping = self._generate_class_mapping(jc)
            if mapping:
                lines.append(mapping)
                lines.append("")

        return '\n'.join(lines)

    def _generate_class_mapping(self, jc: JavaClass) -> str:
        """生成类映射"""
        if not jc.methods and not jc.constructors and not jc.fields:
            return ""

        lines = []

        stub_class = jc.to_stub_full_name()
        total_uses = sum(m.count for m in jc.methods.values())
        total_uses += sum(jc.constructors.values())
        total_uses += sum(f.count for f in jc.fields.values())

        lines.append(f"// {jc.full_name}")
        lines.append(f"// Maps to: {stub_class} (stub)")
        lines.append(f"// Total uses: {total_uses}")
        lines.append(f"mapping {jc.full_name} => {stub_class} {{")

        # 构造函数
        for sig, count in jc.constructors.items():
            lines.append(f"    <init>  // {count} uses")

        # 方法
        for method in sorted(jc.methods.values(), key=lambda x: x.name):
            lines.append(f"    {method.name}  // {method.count} uses")

        # 字段
        for fname, f in sorted(jc.fields.items(), key=lambda x: x[0]):
            keyword = "static field" if f.is_static else "field"
            lines.append(f"    {fname}  // {keyword}, {f.count} uses")

        lines.append("}")

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Cangjie stubs and cjmap from j2cj error markers'
    )
    parser.add_argument('output_dir', help='j2cj output directory (contains .cj files)')
    parser.add_argument('--stub-dir', '-s', required=True,
                        help='Output directory for stub project')
    parser.add_argument('--cjmap', '-c', default=None,
                        help='Output cjmap file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"Error: {args.output_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # 解析错误标记
    print(f"Scanning {args.output_dir}...")
    error_parser = ErrorMarkerParser()
    file_count = error_parser.parse_directory(args.output_dir)
    print(f"Processed {file_count} .cj files")
    print(f"Found {len(error_parser.classes)} classes with missing mappings")

    if not error_parser.classes:
        print("No missing mappings found. Nothing to generate.")
        sys.exit(0)

    # 生成stub类
    print(f"\nGenerating stubs in {args.stub_dir}...")
    stub_gen = StubGenerator(args.stub_dir)
    generated_files = stub_gen.generate_all(error_parser.classes)
    print(f"Generated {len(generated_files)} stub files")

    # 生成cjmap
    cjmap_gen = CjmapGenerator()
    cjmap_content = cjmap_gen.generate(error_parser.classes)

    if args.cjmap:
        with open(args.cjmap, 'w', encoding='utf-8') as f:
            f.write(cjmap_content)
        print(f"Generated cjmap: {args.cjmap}")
    else:
        # 默认保存到stub目录
        default_cjmap = os.path.join(args.stub_dir, "custom.cjmap")
        with open(default_cjmap, 'w', encoding='utf-8') as f:
            f.write(cjmap_content)
        print(f"Generated cjmap: {default_cjmap}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("Summary of Missing Mappings:")
    print("=" * 60)

    sorted_classes = sorted(
        error_parser.classes.values(),
        key=lambda x: -sum(m.count for m in x.methods.values()) - sum(x.constructors.values())
    )

    for jc in sorted_classes:
        method_count = len(jc.methods)
        ctor_count = len(jc.constructors)
        field_count = len(jc.fields)
        total_uses = sum(m.count for m in jc.methods.values())
        total_uses += sum(jc.constructors.values())
        total_uses += sum(f.count for f in jc.fields.values())

        print(f"  {jc.full_name}")
        print(f"    -> stub: {jc.to_stub_full_name()}")
        print(f"    -> {method_count} methods, {ctor_count} ctors, {field_count} fields ({total_uses} total uses)")

    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print(f"1. Review generated stubs in: {args.stub_dir}/src/")
    print(f"2. Add stubs as dependency to your cjpm.toml")
    print(f"3. Place cjmap file in working directory when running j2cj")
    print("=" * 60)


if __name__ == '__main__':
    main()
