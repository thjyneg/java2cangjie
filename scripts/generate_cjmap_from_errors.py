#!/usr/bin/env python3
"""
从j2cj转换错误标记生成cjmap映射规则

用法:
    python generate_cjmap_from_errors.py <output_dir> [--output cjmap_output.cjmap]

功能:
    1. 扫描输出目录中所有.cj文件
    2. 提取 <-- --> 错误标记
    3. 分析缺失的Java API映射
    4. 生成cjmap映射规则模板
"""

import re
import os
import sys
import argparse
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Set, Optional


@dataclass
class MissingMapping:
    """缺失的映射信息"""
    java_class: str
    member_type: str  # 'method', 'constructor', 'field'
    member_name: str
    signature: Optional[str] = None
    count: int = 1
    source_files: Set[str] = None

    def __post_init__(self):
        if self.source_files is None:
            self.source_files = set()


@dataclass
class InvalidSymbol:
    """无效符号"""
    symbol: str
    count: int = 1
    source_files: Set[str] = None

    def __post_init__(self):
        if self.source_files is None:
            self.source_files = set()


class CjmapGenerator:
    """cjmap生成器"""

    # 错误标记正则表达式
    PATTERNS = {
        'missing_method': re.compile(
            r'<-- Missing mapping for ([\w.]+) member: (\w+) -->'
        ),
        'missing_constructor': re.compile(
            r'<-- Missing mapping for ([\w.]+) constructor: (\w+) -->'
        ),
        'missing_static_field': re.compile(
            r'<-- Missing mapping for ([\w.]+) static field: (\w+) -->'
        ),
        'invalid_symbol': re.compile(
            r'<-- Invalid symbol: (.+?) -->'
        ),
        'unsupported_keyword': re.compile(
            r"<-- Java keyword '(\w+)' not supported -->"
        ),
        'generic_wildcard': re.compile(
            r"<-- Generic wildcard '[^']+' not supported -->"
        ),
    }

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.missing_mappings: Dict[str, MissingMapping] = {}
        self.invalid_symbols: Dict[str, InvalidSymbol] = {}
        self.unsupported_keywords: Set[str] = set()

    def scan_files(self) -> int:
        """扫描所有.cj文件"""
        file_count = 0
        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('.cj'):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)
                    file_count += 1
        return file_count

    def _process_file(self, file_path: str):
        """处理单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            rel_path = os.path.relpath(file_path, self.output_dir)

            # 查找所有错误标记
            for line in content.split('\n'):
                self._extract_errors(line, rel_path)
        except Exception as e:
            print(f"Warning: Failed to process {file_path}: {e}", file=sys.stderr)

    def _extract_errors(self, line: str, source_file: str):
        """从行中提取错误信息"""

        # 缺失的方法映射
        for match in self.PATTERNS['missing_method'].finditer(line):
            java_class = match.group(1)
            method_name = match.group(2)
            key = f"{java_class}.{method_name}"

            if key not in self.missing_mappings:
                self.missing_mappings[key] = MissingMapping(
                    java_class=java_class,
                    member_type='method',
                    member_name=method_name
                )
            self.missing_mappings[key].count += 1
            self.missing_mappings[key].source_files.add(source_file)

        # 缺失的构造函数映射
        for match in self.PATTERNS['missing_constructor'].finditer(line):
            java_class = match.group(1)
            constructor_name = match.group(2)
            key = f"{java_class}.<init>"

            if key not in self.missing_mappings:
                self.missing_mappings[key] = MissingMapping(
                    java_class=java_class,
                    member_type='constructor',
                    member_name='<init>'
                )
            self.missing_mappings[key].count += 1
            self.missing_mappings[key].source_files.add(source_file)

        # 无效符号
        for match in self.PATTERNS['invalid_symbol'].finditer(line):
            symbol = match.group(1)
            if symbol not in self.invalid_symbols:
                self.invalid_symbols[symbol] = InvalidSymbol(symbol=symbol)
            self.invalid_symbols[symbol].count += 1
            self.invalid_symbols[symbol].source_files.add(source_file)

        # 不支持的关键字
        for match in self.PATTERNS['unsupported_keyword'].finditer(line):
            self.unsupported_keywords.add(match.group(1))

    def group_by_class(self) -> Dict[str, List[MissingMapping]]:
        """按Java类分组"""
        grouped = defaultdict(list)
        for mapping in self.missing_mappings.values():
            grouped[mapping.java_class].append(mapping)
        return grouped

    def generate_cjmap(self) -> str:
        """生成cjmap内容"""
        lines = []
        lines.append("// Auto-generated cjmap mappings")
        lines.append(f"// Source: {self.output_dir}")
        lines.append(f"// Total missing mappings: {len(self.missing_mappings)}")
        lines.append("")
        lines.append("// ===============================")
        lines.append("// Missing Type Mappings")
        lines.append("// ===============================")
        lines.append("")

        grouped = self.group_by_class()

        for java_class in sorted(grouped.keys()):
            mappings = grouped[java_class]

            # 生成类映射头
            lines.append(f"// {java_class} ({sum(m.count for m in mappings)} occurrences)")
            lines.append(f"mapping {java_class} {{")

            # 按成员类型分组
            methods = [m for m in mappings if m.member_type == 'method']
            constructors = [m for m in mappings if m.member_type == 'constructor']

            # 构造函数
            if constructors:
                lines.append("    // Constructors")
                for c in constructors:
                    lines.append(f"    <init>  // TODO: add signature")
                lines.append("")

            # 方法
            if methods:
                lines.append("    // Methods")
                for m in sorted(methods, key=lambda x: x.member_name):
                    comment = f"  // used {m.count} times"
                    if len(m.source_files) <= 3:
                        comment += f" in: {', '.join(sorted(m.source_files))}"
                    lines.append(f"    {m.member_name}{comment}")

            lines.append("}")
            lines.append("")

        # 添加无效符号部分
        if self.invalid_symbols:
            lines.append("// ===============================")
            lines.append("// Invalid Symbols (may need mock implementations)")
            lines.append("// ===============================")
            lines.append("")
            lines.append("/*")
            for symbol, info in sorted(self.invalid_symbols.items(),
                                       key=lambda x: -x[1].count):
                lines.append(f"   {symbol}")
                lines.append(f"     Count: {info.count}")
                if len(info.source_files) <= 5:
                    lines.append(f"     Files: {', '.join(sorted(info.source_files))}")
                lines.append("")
            lines.append("*/")

        return '\n'.join(lines)

    def generate_report(self) -> str:
        """生成分析报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("j2cj Error Analysis Report")
        lines.append("=" * 60)
        lines.append("")

        # 统计信息
        lines.append("Summary:")
        lines.append(f"  Total missing mappings: {len(self.missing_mappings)}")
        lines.append(f"  Total invalid symbols: {len(self.invalid_symbols)}")
        lines.append(f"  Unsupported keywords: {len(self.unsupported_keywords)}")
        lines.append("")

        # 按频率排序的缺失映射
        lines.append("Top 20 Missing Mappings (by frequency):")
        lines.append("-" * 60)
        sorted_mappings = sorted(
            self.missing_mappings.values(),
            key=lambda x: -x.count
        )[:20]
        for m in sorted_mappings:
            lines.append(f"  {m.java_class}.{m.member_name}: {m.count} times")
        lines.append("")

        # 按类分组统计
        grouped = self.group_by_class()
        lines.append("Missing Mappings by Java Class:")
        lines.append("-" * 60)
        for java_class, mappings in sorted(grouped.items(),
                                           key=lambda x: -sum(m.count for m in x[1])):
            total = sum(m.count for m in mappings)
            methods = len([m for m in mappings if m.member_type == 'method'])
            ctors = len([m for m in mappings if m.member_type == 'constructor'])
            lines.append(f"  {java_class}: {total} uses ({methods} methods, {ctors} ctors)")

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate cjmap from j2cj error markers'
    )
    parser.add_argument('output_dir', help='j2cj output directory')
    parser.add_argument('--output', '-o', default=None,
                        help='Output cjmap file (default: print to stdout)')
    parser.add_argument('--report', '-r', action='store_true',
                        help='Also generate analysis report')

    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"Error: {args.output_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    generator = CjmapGenerator(args.output_dir)

    print(f"Scanning {args.output_dir}...")
    file_count = generator.scan_files()
    print(f"Processed {file_count} .cj files")
    print(f"Found {len(generator.missing_mappings)} missing mappings")
    print()

    cjmap_content = generator.generate_cjmap()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(cjmap_content)
        print(f"Generated cjmap: {args.output}")

        if args.report:
            report_path = args.output.replace('.cjmap', '_report.md')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(generator.generate_report())
            print(f"Generated report: {report_path}")
    else:
        print(cjmap_content)


if __name__ == '__main__':
    main()
