import os
import subprocess
import argparse
import glob
import time
import logging
import xml.etree.ElementTree as ET
import platform
import signal
from dataclasses import dataclass
from typing import List

SUCCESS_CODE = 0
SKIP_CODE = -1

# Maven POM XML namespace
MAVEN_NAMESPACE = "{http://maven.apache.org/POM/4.0.0}"

# Configure logging
class LogConfig:
    """全局日志配置"""
    global_output_dir = None

def setup_logging(output_dir=None):
    """配置日志系统，支持控制台和文件输出"""
    # 如果有输出目录，更新全局配置
    if output_dir:
        LogConfig.global_output_dir = output_dir
    
    log_level = os.getenv("J2CJ_LOG_LEVEL", "INFO").upper()
    log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

    # 创建日志目录
    if LogConfig.global_output_dir:
        log_dir = os.path.join(LogConfig.global_output_dir, "logs")
    else:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 配置日志处理器
    handlers = [
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler(
            os.path.join(log_dir, "j2cj_translation.log"),
            encoding='utf-8',
            mode='a'
        )  # 文件输出
    ]

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=handlers
    )
    
    logging.info(f"Logging initialized. Log directory: {log_dir}")

# 初始化日志配置（默认配置，会在main函数中根据命令行参数重新配置）
setup_logging(None)




@dataclass 
class ModuleResult:
    project_name: str
    module_name: str
    path: str
    status: int  # 0=success, -1=skip,other=failed
    error: str = ""

class ExecutionResults:
    def __init__(self):
        self.modules: List[ModuleResult] = []
    
    def add_module(self, module_result: ModuleResult):
        self.modules.append(module_result)
    
    def print_project_results(self, project_name: str):
        project_modules = [m for m in self.modules if m.project_name == project_name]
        if not project_modules:
            return
            
        logging.info(f"Modules Results:")
        
        skipped_count = 0
        for module in project_modules:
            if module.status == SUCCESS_CODE:
                skipped_count += 1
                status = "SUCCESS"
            elif module.status == SKIP_CODE:
                skipped_count += 1
                status = "SKIPPED"
            else:
                status = f"FAILED (Code: {module.status})"
            logging.info(f"* {module.module_name}: {status}")
    
    def print_domain_results(self):
        logging.info("=== Domain Execution Summary ===")
        project_names = {m.project_name for m in self.modules}
        
        total_skipped = 0
        total_success = 0
        total_processed = 0
        
        for project_name in project_names:
            project_modules = [m for m in self.modules if m.project_name == project_name]
            skipped = len([m for m in project_modules if m.status == SKIP_CODE])
            success = len([m for m in project_modules if m.status == SUCCESS_CODE])
            processed = len(project_modules) - skipped
            
            logging.info(f"Project: {project_name}")
            logging.info(f"Project: {project_name} Results: Modules: {success} succeeded, {skipped} skipped, {len(project_modules)-success-skipped} failed")
            
            total_skipped += skipped
            total_success += success
            total_processed += processed
        
        logging.info(f"Total Summary:")
        logging.info(f"- {total_success} modules succeeded")
        logging.info(f"- {total_skipped} modules skipped")
        logging.info(f"- {total_processed-total_success-total_skipped} modules failed")

class POMAnalyzer:
    @staticmethod
    def parse_pom_for_modules(pom_path):
        """Parse pom.xml to check if it's a pack type and get modules"""
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()

            packaging = root.find(f'{MAVEN_NAMESPACE}packaging')
            if packaging is None or packaging.text != 'pom':
                logging.warning(f"Not a pack type project: {pom_path}")
                return None

            modules = root.findall(f'{MAVEN_NAMESPACE}modules/{MAVEN_NAMESPACE}module')
            if not modules:
                logging.warning(f"No modules found in pack project: {pom_path}")
                return None

            project_dir = os.path.dirname(pom_path)
            return [os.path.join(project_dir, module.text) for module in modules]

        except Exception as e:
            logging.error(f"Failed to parse pom.xml: {str(e)}")
            return None

    @staticmethod
    def get_artifact_id_from_pom(pom_path):
        """Extract artifactId from pom.xml"""
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()

            artifact_id = root.find(f'{MAVEN_NAMESPACE}artifactId')
            if artifact_id is not None:
                return artifact_id.text
            else:
                logging.warning(f"No artifactId found in pom.xml: {pom_path}")
                return None

        except Exception as e:
            logging.error(f"Failed to parse artifactId from pom.xml: {str(e)}")
            return None

class J2CJExecutor:
    def __init__(self):
        self.jdk_path_project = os.getenv("JDK_PATH_PROJECT", "/opt/buildtools/bisheng_jdk_enterprise-203.1.0.450.b003_jdk21/")
        self.jdk_path_j2cj = os.getenv("JDK_PATH_J2CJ", "/opt/buildtools/bisheng_jdk_enterprise-203.1.0.450.b003_jdk21/")
        self.j2cj_tool_path = os.getenv("J2CJ_TOOL_PATH", "/opt/j2cj_tools/tool/j2cj")
        self.timeout = "240m"
        self.is_windows = platform.system() == 'Windows'
        self.path_separator = ';' if self.is_windows else ':'
        
    def find_java_files(self, project_path):
        """Find all Java files in the project"""
        skip_dirs = ["test", "ApiTest", "_APP_TMP_DIR", "lombokgen"]
        java_files = []
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        
        return java_files

    def generate_classpath(self, module_path):
        """Generate project dependencies classpath using mvn dependency:build-classpath"""
        jdk_libs = [
            os.path.join(self.jdk_path_project, "jre", "lib", "rt.jar"),
            os.path.join(self.jdk_path_project, "jre", "lib", "ext", "jfxrt.jar"),
            os.path.join(self.jdk_path_project, "jre", "lib", "ext", "nashorn.jar")
        ]
        default_classpath = self.path_separator.join(jdk_libs)

        if not os.path.exists(os.path.join(module_path, "pom.xml")):
            logging.warning(f"Module ({module_path}) does not contain pom.xml, using default JDK classpath")
            return default_classpath

        cmd = f"mvn dependency:build-classpath -Dmdep.outputFile=target/classpath.txt -Dpackage.type=vm"

        try:
            subprocess.run(
                cmd,
                shell=True,
                cwd=module_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            classpath_file = os.path.join(module_path, "target/classpath.txt")
            if os.path.exists(classpath_file):
                with open(classpath_file, "r", encoding='utf-8') as f:
                    classpath = f.read().strip()
                    # 将Maven生成的classpath（使用系统分隔符）与JDK路径合并
                    return f"{classpath}{self.path_separator}{default_classpath}"
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get classpath: {e.stderr.decode('utf-8')}")

        return default_classpath

    def check_module_result(self, log_file, result_path):
        """Check j2cj conversion result"""
        if not os.path.exists(log_file):
            error_msg = f"J2CJ conversion failed, log file not generated: ({result_path})"
            logging.error(error_msg)
            return (1, error_msg)

        try:
            with open(log_file, "r", encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except IOError as e:
            error_msg = f"J2CJ conversion failed, cannot read log file: {str(e)}"
            logging.error(error_msg)
            return (1, error_msg)

        if "timeout. Exit code is 124." in content:
            error_msg = f"J2CJ conversion timeout: {result_path}"
            logging.error(error_msg)
            return (124, error_msg)
        elif "An exception has occurred in the compiler" in content:
            error_msg = f"J2CJ conversion exception: {result_path}"
            logging.error(error_msg)
            return (2, error_msg)
        elif "failed. Exit code is " in content:
            error_lines = [line for line in content.split('\n')
                         if 'error' in line.lower()]
            error_msg = f"J2CJ conversion error: {result_path}\n" + '\n'.join(error_lines[-5:])
            logging.error(error_msg)
            return (1, error_msg)
        elif "failed to run command" in content.lower():
            error_lines = [line for line in content.split('\n')
                         if 'error' in line.lower()]
            error_msg = f"J2CJ conversion error: {result_path}\n" + '\n'.join(error_lines[-5:])
            logging.error(error_msg)
            return (1, error_msg)
        else:
            logging.info(f"J2CJ conversion successful: {result_path}")
            return (0, "")

class J2CJTranslator:

    @staticmethod
    def _parse_timeout(timeout_str):
        """解析超时时间字符串，如'240m'转换为秒数"""
        timeout_str = timeout_str.strip().lower()
        if timeout_str.endswith('s'):
            return int(timeout_str[:-1])
        elif timeout_str.endswith('m'):
            return int(timeout_str[:-1]) * 60
        elif timeout_str.endswith('h'):
            return int(timeout_str[:-1]) * 3600
        else:
            # 默认为秒
            return int(timeout_str)

    @staticmethod
    def _make_safe_filename(filename):
        """将文件名中的特殊字符替换为下划线，使其在文件系统中安全"""
        return filename.replace('.', '_').replace('/', '_').replace('\\', '_')

    def __init__(self, output_dir=None):
        self.executor = J2CJExecutor()
        self.pom_analyzer = POMAnalyzer()
        self.results = ExecutionResults()
        self.output_dir = output_dir
        self.base_path = self._get_base_path()
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp") if output_dir else None

    def _get_base_path(self):
        """获取基础路径，用于计算相对路径"""
        if not self.output_dir:
            return None
        
        # 获取当前工作目录的绝对路径
        cwd = os.path.abspath(os.getcwd())
        # 返回当前工作目录作为基准路径
        return cwd

    def _build_output_path(self, source_path):
        """基于源路径构建输出路径"""
        if not self.output_dir:
            return None
            
        # 规范化源路径
        source_path = os.path.normpath(source_path)
        
        # 如果有基础路径，计算相对路径
        if self.base_path:
            try:
                relative_path = os.path.relpath(source_path, self.base_path)
                output_path = os.path.join(self.output_dir, relative_path)
                return os.path.normpath(output_path)
            except ValueError:
                # 如果无法计算相对路径，直接使用绝对路径的最后部分
                last_part = os.path.basename(source_path)
                return os.path.join(self.output_dir, last_part)
        else:
            # 没有基础路径时使用原始路径
            return source_path

    def _ensure_output_dir(self, output_path):
        """确保输出目录存在"""
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
            logging.debug(f"Created output directory: {output_path}")

    def execute_module(self, module_path, project_name):
        """Execute j2cj translation for a single module"""
        module_name = os.path.basename(module_path)
        
        if not os.path.exists(module_path):
            error_msg = f"Path does not exist: ({module_path})"
            logging.error(error_msg)
            self.results.add_module(
                ModuleResult(project_name=project_name, module_name=module_name, path=module_path, status=-1, error=error_msg)
            )
            return -1

        # 确定输出路径
        output_dir = self._build_output_path(module_path)
        if output_dir:
            self._ensure_output_dir(output_dir)
            local_temp_dir = self.temp_dir
            if local_temp_dir:
                self._ensure_output_dir(local_temp_dir)
        else:
            output_dir = os.path.normpath(os.path.join(module_path, "cangjie_output"))
            local_temp_dir = module_path

        java_files = self.executor.find_java_files(module_path)
        if not java_files:
            msg = f"Skip Processing module ( No Java files found ) : ({module_path})"
            logging.warning(msg)
            self.results.add_module(
                ModuleResult(
                    project_name=project_name,
                    module_name=module_name,
                    path=module_path,
                    status=SKIP_CODE,
                    error=msg
                )
            )
            return 0
        else:
            logging.info(f"Processing module: ({module_path})")
            sources_file_path = os.path.join(local_temp_dir, "sources.txt")
            try:
                with open(sources_file_path, "w", encoding='utf-8') as f:
                    f.write("\n".join(java_files))
                logging.debug(f"Wrote sources file: {sources_file_path}")
            except IOError as e:
                error_msg = f"Failed to write sources.txt: {str(e)}"
                logging.error(error_msg)
                self.results.add_module(
                    ModuleResult(
                        project_name=project_name,
                        module_name=module_name,
                        path=module_path,
                        status=-1,
                        error=error_msg
                    )
                )
                return -1

        classpath = self.executor.generate_classpath(module_path)
        jars_file_path = os.path.join(local_temp_dir, "j2cj_jars.txt")
        try:
            with open(jars_file_path, "w", encoding='utf-8') as f:
                f.write(classpath)
            logging.debug(f"Wrote jars file: {jars_file_path}")
        except IOError as e:
            error_msg = f"Failed to write j2cj_jars.txt: {str(e)}"
            logging.error(error_msg)
            self.results.add_module(
                ModuleResult(
                    project_name=project_name,
                    module_name=module_name,
                    path=module_path,
                    status=-1,
                    error=error_msg
                )
            )
            return -1
        
        # 设置日志文件路径
        if self.output_dir:
            logs_output_dir = os.path.join(self.output_dir, "logs")
            self._ensure_output_dir(logs_output_dir)
            module_log_dir = os.path.join(logs_output_dir, project_name)
            self._ensure_output_dir(module_log_dir)
            log_file = os.path.join(module_log_dir, f"{module_name}_j2cjoutput.log")
        else:
            log_file = os.path.join(module_path, "j2cjoutput.log")
        
        sources_file = sources_file_path
        java_cmd = os.path.join(self.executor.jdk_path_j2cj, "bin", "java")
        j2cj_jar_path = os.path.normpath(os.path.join(self.executor.j2cj_tool_path, "j2cj.jar"))

        # Get artifactId from pom.xml for mapping file naming
        pom_path = os.path.join(module_path, "pom.xml")
        artifact_id = None
        if os.path.exists(pom_path):
            artifact_id = self.pom_analyzer.get_artifact_id_from_pom(pom_path)
            if artifact_id:
                # Replace special characters for filename compatibility
                safe_artifact_id = self._make_safe_filename(artifact_id)
                mapping_filename = f"{safe_artifact_id}.cjmap"
                logging.info(f"Using artifactId '{artifact_id}' (as '{safe_artifact_id}') for mapping filename")
            else:
                logging.warning("Using default mapping filename (artifactId not found)")
                safe_project_name = self._make_safe_filename(project_name)
                safe_module_name = self._make_safe_filename(module_name)
                mapping_filename = f"{safe_project_name}.{safe_module_name}.cjmap"
        else:
            logging.warning("No pom.xml found, using default mapping filename")
            safe_project_name = self._make_safe_filename(project_name)
            safe_module_name = self._make_safe_filename(module_name)
            mapping_filename = f"{safe_project_name}.{safe_module_name}.cjmap"

        generate_mapping_file = os.path.normpath(os.path.join(output_dir, mapping_filename))

        # 解析超时时间（如"240m"转换为秒数）
        timeout_seconds = self._parse_timeout(self.executor.timeout)

        command = (
            f"{java_cmd} "
            f"-ea -Dextra.log=true -Dfile.encoding=UTF-8 "
            f"-Dgenerate.mapping.file={generate_mapping_file} "
            f"-Dmodule.name={module_name} "
            f"--patch-module jdk.compiler={j2cj_jar_path} "
            f"-m jdk.compiler/com.excelsior.j2cj.main.Main "
            f"-d {output_dir} "
            f"-classpath {classpath} "
            f"-source 21 -target 21 -sourcepath src "
            f"@{sources_file}"
        )

        logging.info(f"  Executing j2cj command: {command}")
        try:
            # 打开日志文件用于重定向输出
            with open(log_file, 'w', encoding='utf-8') as log_f:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd="/opt/j2cj_tools/pack/cjmap",
                    env=os.environ,
                    stdout=log_f,
                    stderr=subprocess.STDOUT
                )
                try:
                    process.wait(timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    # 超时后终止进程
                    process.kill()
                    process.wait()
                    logging.error(f"J2CJ conversion timeout after {timeout_seconds} seconds")
                    # 写入超时信息到日志文件
                    with open(log_file, 'a', encoding='utf-8') as log_f_append:
                        log_f_append.write(f"\nTimeout. Exit code is 124.\n")

            result, error_msg = self.executor.check_module_result(log_file, module_path)
            self.results.add_module(
                ModuleResult(
                    project_name=project_name,
                    module_name=module_name,
                    path=module_path,
                    status=result,
                    error=error_msg
                )
            )
            return result
        except subprocess.TimeoutExpired as e:
            error_msg = f"J2CJ command timeout: {str(e)}"
            logging.error(error_msg)
            self.results.add_module(
                ModuleResult(
                    project_name=project_name,
                    module_name=module_name,
                    path=module_path,
                    status=124,
                    error=error_msg
                )
            )
            return 124
        except FileNotFoundError as e:
            error_msg = f"J2CJ command not found: {str(e)}"
            logging.error(error_msg)
            self.results.add_module(
                ModuleResult(
                    project_name=project_name,
                    module_name=module_name,
                    path=module_path,
                    status=-1,
                    error=error_msg
                )
            )
            return -1
        except subprocess.CalledProcessError as e:
            error_msg = f"J2CJ command execution failed: {str(e)}"
            logging.error(error_msg)
            self.results.add_module(
                ModuleResult(
                    project_name=project_name,
                    module_name=module_name,
                    path=module_path,
                    status=e.returncode,
                    error=error_msg
                )
            )
            return e.returncode
        except Exception as e:
            error_msg = f"J2CJ command execution failed: {str(e)}"
            logging.error(error_msg)
            self.results.add_module(
                ModuleResult(
                    project_name=project_name,
                    module_name=module_name,
                    path=module_path,
                    status=-1,
                    error=error_msg
                )
            )
            return -1

    def execute_project(self, project_path):
        """Execute j2cj for all modules in a project (with recursive structure support)"""
        project_path = os.path.normpath(project_path)
        project_name = os.path.basename(project_path)
        logging.debug(f"Project path: {project_path}")
        logging.info(f"Starting batch processing for project: {project_name}")
        pom_path = os.path.join(project_path, "pom.xml")
        if not os.path.exists(pom_path):
            error_msg = f"No pom.xml found in {project_path}, skipping batch processing"
            logging.warning(error_msg)
            return -1
            
        # Recursively find all non-packing modules
        all_modules = self._find_all_modules(project_path, project_name)
        if not all_modules:
            logging.warning(f"No non-packing modules found in project: {project_name}")
            return -1
            
        logging.info(f"Found {len(all_modules)} non-packing modules in project:")
        for i, module in enumerate(all_modules, 1):
            logging.info(f"  {i}. {module}")
        
        results = []
        for module in all_modules:
            result = self.execute_module(module, project_name)
            results.append(result)
            
        self.results.print_project_results(project_name)
        return 0 if all(r == 0 for r in results) else 1

    def _find_all_modules(self, root_path, project_name):
        """Recursively find all non-packing modules starting from root_path"""
        modules = []
        
        def _find_modules_recursive(current_path):
            pom_file = os.path.join(current_path, "pom.xml")
            if not os.path.exists(pom_file):
                return
            
            # Check if this is a packing/pom type module
            is_packing_module = self._is_packing_type_module(pom_file)
            logging.debug(f"Checking {current_path}: packing={is_packing_module}")
            
            if is_packing_module:
                # This is a packing/pom type, recursively find its modules
                sub_modules = self.pom_analyzer.parse_pom_for_modules(pom_file)
                if sub_modules:
                    for sub_module in sub_modules:
                        if os.path.exists(sub_module):
                            _find_modules_recursive(sub_module)
            else:
                # This is a non-packing module, add it to the list
                modules.append(current_path)
        
        _find_modules_recursive(root_path)
        return modules

    def _is_packing_type_module(self, pom_file):
        """Check if a pom.xml represents a packing/pom type module"""
        try:
            tree = ET.parse(pom_file)
            root = tree.getroot()

            packaging = root.find(f'{MAVEN_NAMESPACE}packaging')
            if packaging is not None and packaging.text.strip().lower() in ['pom', 'pack']:
                return True

            # Also check if it has modules (indicates it's an aggregator)
            modules = root.findall(f'{MAVEN_NAMESPACE}modules/{MAVEN_NAMESPACE}module')
            return len(modules) > 0

        except Exception as e:
            logging.debug(f"Error checking packing type for {pom_file}: {str(e)}")
            return False

    def execute_domain(self, domain_path):
        """Execute j2cj for all projects in a domain"""
        logging.info(f"Starting domain processing for: {domain_path}")
        if not os.path.exists(domain_path):
            logging.error(f"Domain path does not exist: {domain_path}")
            return -1
            
        projects = [d for d in os.listdir(domain_path) 
                   if os.path.isdir(os.path.join(domain_path, d))]
        
        if not projects:
            logging.warning(f"No projects found in domain: {domain_path}")
            return -1
            
        logging.info(f"Found {len(projects)} projects in domain ( show list in debug ):")
        for i, project in enumerate(projects, 1):
            logging.debug(f"  {i}. {project}")
        
        results = []
        for project in projects:
            project_path = os.path.join(domain_path, project)
            logging.debug(f"Processing project {project} ({project_path})")
            result = self.execute_project(project_path)
            results.append(result)
        
        self.results.print_domain_results()
        
        if all(r == 0 for r in results):
            logging.info("All projects processed successfully")
            return 0
        else:
            logging.error(f"Some projects failed to process. Results: {results}")
            return 1

def main():
    """J2CJ Main Function"""
    parser = argparse.ArgumentParser(
        description='Execute j2cj conversion in domain, project or module mode'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-d', '--domain-path',
        type=str,
        help='Path to the domain directory containing multiple projects'
    )
    group.add_argument(
        '-p', '--project-path', 
        type=str,
        help='Path to the project directory (must contain pom.xml) for batch processing'
    )
    group.add_argument(
        '-m', '--module-path',
        type=str,
        help='Path to the module directory for single module processing'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for translated files, cjmap files and logs. If not specified, uses current behavior.'
    )
    
    args = parser.parse_args()
    
    # 重新配置日志，使用指定的输出目录
    setup_logging(args.output_dir)
    
    translator = J2CJTranslator(output_dir=args.output_dir)
    
    if args.domain_path:
        return translator.execute_domain(args.domain_path)
    elif args.module_path:
        parent_path = os.path.dirname(os.path.normpath(args.module_path))
        project_name = os.path.basename(parent_path)
        return translator.execute_module(args.module_path, project_name)
    elif args.project_path:
        return translator.execute_project(args.project_path)

if __name__ == "__main__":
    main()
