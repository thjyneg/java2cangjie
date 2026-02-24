#!/usr/bin/env python3
"""
J2CJ Runner - Execute j2cj tool for Java to Cangjie translation.
"""
import subprocess
import sys
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# Default j2cj location (relative to skill directory)
DEFAULT_J2CJ_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "j2cj_tool", "j2cj.jar")


class J2CJResult:
    """Result of j2cj execution."""

    def __init__(self, success: bool, errors: List[str], warnings: List[str]):
        self.success = success
        self.errors = errors
        self.warnings = warnings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "errors": self.errors,
            "warnings": self.warnings
        }


def run_j2cj(
    source_path: str,
    output_dir: str,
    j2cj_path: Optional[str] = None,
    classpath: Optional[str] = None,
    sourcepath: Optional[str] = None,
    module_path: Optional[str] = None,
    mode: str = "codestyle",
    verbose: bool = False,
    encoding: Optional[str] = None,
) -> J2CJResult:
    """
    Run j2cj to translate Java to Cangjie.

    Args:
        source_path: Path to Java source files or directory
        output_dir: Output directory for generated Cangjie files
        j2cj_path: Path to j2cj.jar (default: DEFAULT_J2CJ_PATH)
        classpath: Classpath for Java compilation
        sourcepath: Source path for Java files
        module_path: Module path for Java modules
        mode: Translation mode - 'codestyle' or 'semantic'
        verbose: Enable verbose output
        encoding: Character encoding for source files

    Returns:
        J2CJResult containing success status, errors, and warnings
    """
    j2cj_jar = j2cj_path or DEFAULT_J2CJ_PATH

    if not os.path.exists(j2cj_jar):
        return J2CJResult(
            success=False,
            errors=[f"j2cj.jar not found at: {j2cj_jar}"],
            warnings=[]
        )

    # Build command
    cmd = [
        "java",
        "--patch-module", f"jdk.compiler={j2cj_jar}",
        "-m", "jdk.compiler/com.excelsior.j2cj.main.Main"
    ]

    # Add options
    cmd.extend(["-s", output_dir])
    cmd.extend(["-sourcepath", source_path])

    if classpath:
        cmd.extend(["-classpath", classpath])
    if sourcepath:
        cmd.extend(["-sourcepath", sourcepath])
    if module_path:
        cmd.extend(["-module-path", module_path])
    if mode in ("codestyle", "semantic"):
        cmd.extend(["-mode", mode])
    if verbose:
        cmd.append("-verbose")
    if encoding:
        cmd.extend(["-encoding", encoding])

    # Add source files (expand directory if needed)
    source_files = _get_java_files(source_path)
    cmd.extend(source_files)

    # Execute
    errors = []
    warnings = []

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(j2cj_jar)
        )

        # Parse output
        output = result.stdout + result.stderr

        # Collect errors (j2cj reports errors with specific patterns)
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            if 'error:' in line.lower() or 'Error:' in line:
                errors.append(line)
            elif 'warning:' in line.lower():
                warnings.append(line)
            elif 'fatal' in line.lower():
                errors.append(line)

        return J2CJResult(
            success=result.returncode == 0 or len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    except subprocess.SubprocessError as e:
        return J2CJResult(
            success=False,
            errors=[f"Subprocess error: {e}"],
            warnings=[]
        )
    except Exception as e:
        return J2CJResult(
            success=False,
            errors=[f"Unexpected error: {e}"],
            warnings=[]
        )


def _get_java_files(path: str) -> List[str]:
    """Get all .java files from a path."""
    path_obj = Path(path)
    if path_obj.is_file() and path_obj.suffix == '.java':
        return [str(path_obj)]
    if path_obj.is_dir():
        return [str(f) for f in path_obj.rglob('*.java')]
    return []


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run j2cj for Java to Cangjie translation")
    parser.add_argument("source_path", help="Path to Java source files or directory")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("--j2cj", help="Path to j2cj.jar")
    parser.add_argument("-cp", "--classpath", help="Classpath")
    parser.add_argument("-sp", "--sourcepath", help="Source path")
    parser.add_argument("-mp", "--module-path", help="Module path")
    parser.add_argument("--mode", choices=["codestyle", "semantic"], default="codestyle", help="Translation mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--encoding", help="Character encoding")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    result = run_j2cj(
        source_path=args.source_path,
        output_dir=args.output,
        j2cj_path=args.j2cj,
        classpath=args.classpath,
        sourcepath=args.sourcepath,
        module_path=args.module_path,
        mode=args.mode,
        verbose=args.verbose,
        encoding=args.encoding,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print("Translation completed successfully")
            if result.warnings:
                print(f"\nWarnings ({len(result.warnings)}):")
                for w in result.warnings:
                    print(f"  - {w}")
        else:
            print("Translation failed")
            print(f"\nErrors ({len(result.errors)}):")
            for e in result.errors:
                print(f"  - {e}")
        sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
