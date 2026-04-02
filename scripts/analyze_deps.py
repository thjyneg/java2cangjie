#!/usr/bin/env python3
"""
Java Dependency Analyzer for Java-to-Cangjie Translation

Analyzes Java projects, builds dependency graph, generates translation batches.
Supports single-module and multi-module Maven/Gradle projects.

Usage:
    python analyze_deps.py --java-path /path/to/java/src
    python analyze_deps.py --java-path /path/to/module1,/path/to/module2 --output-dir ./j2cjgenerated
    python analyze_deps.py --java-path /path/to/java --max-batch-size 2
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def scan_java_files(java_roots: List[Path]) -> List[Dict]:
    """Scan Java source directories and collect file information."""
    java_files = []
    seen = set()

    for root in java_roots:
        if not root.exists():
            continue

        for java_file in root.rglob("*.java"):
            # Skip test files and generated sources
            if any(x in str(java_file) for x in ['/test/', '/generated/', '/target/']):
                continue

            class_name = java_file.stem
            if class_name in seen:
                continue
            seen.add(class_name)

            java_files.append({
                'path': str(java_file),
                'className': class_name,
                'lines': 0,  # Will count later
                'deps': []
            })

    return java_files


def detect_package(java_path: str) -> str:
    """Extract package declaration from Java file."""
    with open(java_path, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.match(r'^\s*package\s+([\w.]+)\s*;', content, re.MULTILINE)
        return match.group(1) if match else ''


def count_lines(java_path: str) -> int:
    """Count lines in Java file."""
    with open(java_path, 'r', encoding='utf-8') as f:
        return len(f.readlines())


def build_dependency_graph(java_files: List[Dict]) -> Tuple[Dict, Dict, Dict]:
    """
    Build dependency graph from Java files.

    Returns:
        - file_map: className -> {path, packageName}
        - package_to_classes: packageName -> [classNames]
        - dependencies: className -> [dependencyClassNames]
    """
    file_map = {}
    package_to_classes = {}
    dependencies = {}

    # First pass: extract packages
    for file_info in java_files:
        pkg = detect_package(file_info['path'])
        file_info['packageName'] = pkg

        file_map[file_info['className']] = {
            'path': file_info['path'],
            'packageName': pkg
        }

        if pkg and pkg not in package_to_classes:
            package_to_classes[pkg] = []
        if pkg:
            package_to_classes[pkg].append(file_info['className'])

    # Second pass: analyze imports
    for file_info in java_files:
        class_name = file_info['className']
        pkg = file_info['packageName']

        dep_set = set()

        with open(file_info['path'], 'r', encoding='utf-8') as f:
            content = f.read()
            normalized = content.replace('\r\n', '\n')

            # 1. Regular imports: import x.y.Z; or import x.y.*;
            regular_imports = re.findall(r'^import\s+(?!static\b)([\w.]+(?:\.\*)?)\s*;', normalized, re.MULTILINE)
            for imp in regular_imports:
                imported = imp.strip().rstrip(';')

                if imported.endswith('.*'):
                    # Wildcard import: resolve all classes in that package
                    pkg_name = imported[:-2]
                    classes = package_to_classes.get(pkg_name, [])
                    for cls in classes:
                        if cls != class_name:
                            dep_set.add(cls)
                else:
                    imported_class = imported.split('.')[-1]
                    if imported_class in file_map and imported_class != class_name:
                        dep_set.add(imported_class)

            # 2. Static imports: import static x.y.Z.method; or import static x.y.Z.*;
            static_imports = re.findall(r'^import\s+static\s+([\w.]+(?:\.\*)?)\s*;', normalized, re.MULTILINE)
            for imp in static_imports:
                imported = imp.strip().rstrip(';')

                if imported.endswith('.*'):
                    # Static wildcard: second-to-last segment is class
                    parts = imported.split('.')
                    if len(parts) >= 2:
                        class_name_from_imp = parts[-2]
                        if class_name_from_imp in file_map and class_name_from_imp != class_name:
                            dep_set.add(class_name_from_imp)
                else:
                    # Static method/field: second-to-last segment is class
                    parts = imported.split('.')
                    if len(parts) >= 2:
                        class_name_from_imp = parts[-2]
                        if class_name_from_imp in file_map and class_name_from_imp != class_name:
                            dep_set.add(class_name_from_imp)

            # 3. Same-package implicit dependencies
            # Java classes in same package can reference each other without imports
            if pkg and pkg in package_to_classes:
                same_pkg_classes = package_to_classes[pkg]
                for cls in same_pkg_classes:
                    if cls != class_name:
                        # Check if this class name actually appears in content
                        regex = r'\b' + re.escape(cls) + r'\b'
                        if re.search(regex, content):
                            dep_set.add(cls)

        dependencies[class_name] = list(dep_set)

    return file_map, package_to_classes, dependencies


def topological_sort(java_files: List[Dict], dependencies: Dict) -> List[str]:
    """
    Perform topological sort (Kahn's algorithm) with cycle handling.

    Returns ordered list of class names following dependency order.
    Leaf nodes (no dependencies) come first.
    """
    # Build adjacency list and in-degree count
    in_degree = {f['className']: 0 for f in java_files}
    adj_list = {f['className']: [] for f in java_files}

    for file_info in java_files:
        class_name = file_info['className']
        for dep in dependencies[class_name]:
            if dep in adj_list:
                adj_list[dep].append(class_name)
                in_degree[class_name] += 1

    # Start with nodes that have no dependencies
    queue = [cls for cls, deg in in_degree.items() if deg == 0]
    sorted_classes = []

    while queue:
        cls = queue.pop(0)
        sorted_classes.append(cls)

        for neighbor in adj_list[cls]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Handle remaining nodes (cycles): force-add remaining classes
    sorted_set = set(sorted_classes)
    remaining = [f for f in java_files if f['className'] not in sorted_set]
    remaining.sort(key=lambda f: in_degree[f['className']])

    for file_info in remaining:
        sorted_classes.append(file_info['className'])

    return sorted_classes


def create_batches(
    java_files: List[Dict],
    sorted_classes: List[str],
    max_batch_size: int = 3
) -> List[Dict]:
    """Create translation batches following dependency order."""
    batches = []
    remaining = sorted_classes.copy()
    file_map = {f['className']: f for f in java_files}
    batch_index = 0

    while remaining:
        batch_size = min(max_batch_size, len(remaining))
        batch_files = remaining[:batch_size]
        batch_id = f"batch-{batch_index + 1}"

        # Calculate dependencies (which previous batches this batch depends on)
        batch_deps = []
        for cls in batch_files:
            file_info = file_map[cls]
            for dep in dependencies[cls]:
                # Find which batch this dependency is in
                for i, batch in enumerate(batches):
                    if dep in [f['className'] for f in batch['files']]:
                        dep_id = f"batch-{i + 1}"
                        if dep_id not in batch_deps:
                            batch_deps.append(dep_id)

        batch = {
            'id': batch_id,
            'files': [],
            'dependencies': sorted(batch_deps)
        }

        for cls in batch_files:
            file_info = file_map[cls]
            batch['files'].append({
                'className': cls,
                'path': file_info['path'],
                'size': os.path.getsize(file_info['path']),
                'lines': count_lines(file_info['path'])
            })

        batches.append(batch)
        remaining = remaining[batch_size:]
        batch_index += 1

    return batches


def detect_project_type(java_path: str) -> Dict:
    """
    Detect project type and module structure.

    Returns:
        {
            'type': 'single' | 'multi',
            'modules': [{'name', 'javaPath', 'outputDir'}],
            'baseDir': str
        }
    """
    java_root = Path(java_path).resolve()

    # Check for multi-module indicators
    pom_xml = java_root / 'pom.xml'
    build_gradle = java_root / 'build.gradle'
    build_gradle_kts = java_root / 'build.gradle.kts'

    is_maven = pom_xml.exists()
    is_gradle = build_gradle.exists() or build_gradle_kts.exists()

    if not (is_maven or is_gradle):
        # Single module project
        return {
            'type': 'single',
            'modules': [{
                'name': java_root.name,
                'javaPath': str(java_root),
                'outputDir': f'{java_root.name}'
            }],
            'baseDir': str(java_root.parent)
        }

    # Maven multi-module detection
    if is_maven:
        with open(pom_xml, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for <modules> section
        modules_match = re.search(r'<modules>\s*(.*?)\s*</modules>', content, re.DOTALL)
        if modules_match:
            module_names = re.findall(r'<module>(.*?)</module>', modules_match.group(1))
            return {
                'type': 'multi',
                'modules': [{
                    'name': name.strip(),
                    'javaPath': str(java_root / name.strip() / 'src' / 'main' / 'java'),
                    'outputDir': name.strip()
                } for name in module_names],
                'baseDir': str(java_root.parent)
            }

    # Gradle multi-module detection (simplified)
    if is_gradle:
        # Scan for subdirectories with build files
        modules = []
        for item in java_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if (item / 'build.gradle').exists() or (item / 'build.gradle.kts').exists():
                    modules.append({
                        'name': item.name,
                        'javaPath': str(item / 'src' / 'main' / 'java'),
                        'outputDir': item.name
                    })

        if len(modules) > 1:
            return {
                'type': 'multi',
                'modules': modules,
                'baseDir': str(java_root.parent)
            }

    # Single module Maven/Gradle project
    return {
        'type': 'single',
        'modules': [{
            'name': java_root.name,
            'javaPath': str(java_root),
            'outputDir': java_root.name
        }],
        'baseDir': str(java_root.parent)
    }


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Java project dependencies for Cangjie translation'
    )
    parser.add_argument(
        '--java-path',
        required=True,
        help='Path(s) to Java source root directory. Use comma for multiple paths.'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for Cangjie files (default: ../j2cjgenerated)'
    )
    parser.add_argument(
        '--max-batch-size',
        type=int,
        default=3,
        help='Maximum files per batch (default: 3)'
    )

    args = parser.parse_args()

    # Parse Java paths
    java_paths = [Path(p.strip()).resolve() for p in args.java_path.split(',')]

    # Scan for Java files
    java_files = scan_java_files(java_paths)

    if len(java_files) == 0:
        print(json.dumps({
            'error': f'No Java files found in: {", ".join(str(p) for p in java_paths)}'
        }, indent=2))
        sys.exit(1)

    # Build dependency graph
    file_map, package_to_classes, dependencies = build_dependency_graph(java_files)

    # Topological sort
    sorted_classes = topological_sort(java_files, dependencies)

    # Create batches
    batches = create_batches(java_files, sorted_classes, args.max_batch_size)

    # Detect project type
    project_info = detect_project_type(str(java_paths[0]))
    output_dir = args.output_dir or project_info['baseDir'] + '/j2cjgenerated'

    # Count lines for all files
    for batch in batches:
        for file in batch['files']:
            file['lines'] = count_lines(file['path'])

    # Generate DAG summary
    dag_parts = []
    for batch in batches:
        file_names = ', '.join(f['className'] for f in batch['files'])
        if batch['dependencies']:
            deps = ' → '.join(batch['dependencies'])
            dag_parts.append(f'{deps} → [{file_names}]')
        else:
            dag_parts.append(f'[{file_names}]')
    dag_summary = '\n'.join(dag_parts)

    # Output JSON result
    result = {
        'projectInfo': project_info,
        'totalFiles': len(java_files),
        'totalBatches': len(batches),
        'batches': batches,
        'dagSummary': dag_summary,
        'outputDir': output_dir
    }

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
