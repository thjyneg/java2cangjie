import os
import sys
import subprocess
import argparse
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional

SUCCESS_CODE = 0
SKIP_CODE = -1


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)




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
            
            packaging = root.find('{http://maven.apache.org/POM/4.0.0}packaging')
            if packaging is None or packaging.text != 'pom':
                logging.warning(f"Not a pack type project: {pom_path}")
                return None
                
            modules = root.findall('{http://maven.apache.org/POM/4.0.0}modules/{http://maven.apache.org/POM/4.0.0}module')
            if not modules:
                logging.warning(f"No modules found in pack project: {pom_path}")
                return None
                
            project_dir = os.path.dirname(pom_path)
            return [os.path.join(project_dir, module.text) for module in modules]
            
        except Exception as e:
            logging.error(f"Failed to parse pom.xml: {str(e)}")
            return None

class J2CJExecutor:
    def __init__(self):
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录(脚本所在目录的父目录)
        project_root = os.path.dirname(script_dir)

        # J2CJ_TOOL_PATH: 按优先级查找
        # 1. 首先检查环境变量
        j2cj_tool_env = os.getenv("J2CJ_TOOL_PATH")
        if j2cj_tool_env and os.path.exists(os.path.join(j2cj_tool_env, "j2cj.jar")):
            self.j2cj_tool_path = j2cj_tool_env
            logging.info(f"Using J2CJ_TOOL_PATH from environment: {self.j2cj_tool_path}")
        # 2. 检查skill目录的 j2cj_tool (相对于脚本所在目录)
        elif os.path.exists(os.path.join(script_dir, "..", "j2cj_tool", "j2cj.jar")):
            self.j2cj_tool_path = os.path.join(script_dir, "..", "j2cj_tool")
            logging.info(f"Using j2cj_tool from skill directory: {self.j2cj_tool_path}")
        # 3. 检查项目根目录的 skills/java2cangjie-translate/j2cj_tool
        elif os.path.exists(os.path.join(project_root, "skills", "java2cangjie-translate", "j2cj_tool", "j2cj.jar")):
            self.j2cj_tool_path = os.path.join(project_root, "skills", "java2cangjie-translate", "j2cj_tool")
            logging.info(f"Using j2cj_tool from skills/java2cangjie-translate directory: {self.j2cj_tool_path}")
        # 4. 找不到则报错并退出
        else:
            logging.error("ERROR: j2cj tool not found!")
            logging.error("Please either:")
            logging.error("  1. Set J2CJ_TOOL_PATH environment variable")
            logging.error("  2. Place j2cj.jar in ./skills/java2cangjie-translate/j2cj_tool/ (relative to project root)")
            sys.exit(1)

        # JDK_PATH_PROJECT: 默认使用系统 java 命令
        self.jdk_path_project = os.getenv("JDK_PATH_PROJECT", "java")

        # JDK_PATH_J2CJ: 默认使用系统 java 命令
        self.jdk_path_j2cj = os.getenv("JDK_PATH_J2CJ", "java")

        self.timeout = "240m"
        
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
        if not os.path.exists(os.path.join(module_path, "pom.xml")):
            logging.warning(f"Module ({module_path}) does not contain pom.xml, using default JDK classpath")
            # 如果使用系统 java 命令，返回空 classpath（JDK 会自动处理）
            if self.jdk_path_project == "java":
                return "."
            return f"{self.jdk_path_project}/jre/lib/rt.jar:{self.jdk_path_project}/jre/lib/ext/jfxrt.jar:{self.jdk_path_project}/jre/lib/ext/nashorn.jar"

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
                with open(classpath_file, "r") as f:
                    classpath = f.read().strip()
                    # 如果使用系统 java 命令，只返回 Maven 依赖的 classpath
                    if self.jdk_path_project == "java":
                        return classpath
                    return f"{classpath}:{self.jdk_path_project}/jre/lib/rt.jar:{self.jdk_path_project}/jre/lib/ext/jfxrt.jar:{self.jdk_path_project}/jre/lib/ext/nashorn.jar"
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get classpath: {e.stderr.decode('utf-8')}")

        # 如果使用系统 java 命令，返回空 classpath
        if self.jdk_path_project == "java":
            return "."
        return f"{self.jdk_path_project}/jre/lib/rt.jar:{self.jdk_path_project}/jre/lib/ext/jfxrt.jar:{self.jdk_path_project}/jre/lib/ext/nashorn.jar"

    def check_module_result(self, log_file, result_path):
        """Check j2cj conversion result"""
        if not os.path.exists(log_file):
            error_msg = f" * J2CJ conversion failed, log file not generated: ({result_path})"
            logging.error(error_msg)
            return (1, error_msg)
        
        with open(log_file, "r") as f:
            content = f.read()
            
            if "timeout. Exit code is 124." in content:
                error_msg = f" * J2CJ conversion timeout: {result_path}"
                logging.error(error_msg)
                return (124, error_msg)
            elif "An exception has occurred in the compiler" in content:
                error_msg = f" * J2CJ conversion exception: {result_path}"
                logging.error(error_msg)
                return (2, error_msg)
            elif "failed. Exit code is " in content:
                error_msg = f" * J2CJ conversion failed: {result_path}"
                logging.error(error_msg)
                return (1, error_msg)
            elif "errors" in content.lower():
                error_lines = [line for line in content.split('\n') 
                             if 'error' in line.lower()]
                error_msg = f" * J2CJ conversion error: {result_path}\n" + '\n'.join(error_lines[-5:])
                logging.error(error_msg)
                return (1, error_msg)
            elif "failed to run command" in content.lower():
                error_lines = [line for line in content.split('\n') 
                             if 'error' in line.lower()]
                error_msg = f" * J2CJ conversion error: {result_path}\n" + '\n'.join(error_lines[-5:])
                logging.error(error_msg)
                return (1, error_msg)
            else:
                logging.info(f" * J2CJ conversion successful: {result_path}")
                return (0, "")

class J2CJTranslator:

    def __init__(self):
        self.executor = J2CJExecutor()
        self.pom_analyzer = POMAnalyzer()
        self.results = ExecutionResults()
    
    def find_project_root(self, module_path):
        """Find the project root directory from module path"""
        normalized_path = os.path.normpath(module_path)
        
        if "src/main/java" in normalized_path:
            idx = normalized_path.find("src/main/java")
            project_root = normalized_path[:idx].rstrip(os.sep)
            if os.path.exists(os.path.join(project_root, "pom.xml")):
                return project_root
        
        current_path = normalized_path
        while current_path and current_path != os.path.dirname(current_path):
            if os.path.exists(os.path.join(current_path, "pom.xml")):
                return current_path
            current_path = os.path.dirname(current_path)
        
        return os.path.dirname(normalized_path)

    def execute_module(self, module_path, project_name):
        """Execute j2cj translation for a single module"""
        module_name = os.path.basename(module_path)
        
        if not os.path.exists(module_path):
            error_msg = f"Path does not exist: ({module_path})"
            logging.error(error_msg)
            self.results.add_module(
                ModuleResult(name=module_name, path=module_path, status=-1, error=error_msg)
            )
            return -1

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
            with open(f"{module_path}/sources.txt", "w") as f:
                f.write("\n".join(java_files))

        classpath = self.executor.generate_classpath(module_path)
        with open(f"{module_path}/j2cj_jars.txt", "w") as f:
            f.write(classpath)
        
        log_file = f"{module_path}/j2cjoutput.log"

        project_root = self.find_project_root(module_path)
        output_dir = os.path.join(project_root, "j2cjgenerated")
        logging.info(f"Output directory: {output_dir}")

        # 构建 java 命令
        if self.executor.jdk_path_j2cj == "java":
            java_cmd = "java"
        else:
            java_cmd = f"{self.executor.jdk_path_j2cj}/bin/java"

        command = (
            f"timeout {self.executor.timeout} {java_cmd} "
            f"-ea -Dextra.log=true -Dfile.encoding=UTF-8 "
            f"-Dgenerate.mapping.file={module_name}.cjmap "
            f"-Dj2cj.module.name={module_name} "
            f"--patch-module jdk.compiler={self.executor.j2cj_tool_path}/j2cj.jar "
            f"-m jdk.compiler/com.excelsior.j2cj.main.Main "
            f"-d {output_dir} "
            f"-classpath {classpath} "
            f"-source 21 -target 21 -sourcepath com "
            f"@{module_path}/sources.txt > {log_file} 2>&1"
        )
        
        logging.debug("  Executing j2cj command")
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=module_path,
                env=os.environ
            )
            process.wait()
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
        """Execute j2cj for all modules in a project"""
        project_path = os.path.normpath(project_path)
        project_name = os.path.basename(project_path)
        logging.debug(f"Project path: {project_path}")
        logging.info(f"Starting batch processing for project: {project_name}")
        pom_path = os.path.join(project_path, "pom.xml")
        if not os.path.exists(pom_path):
            error_msg = f"No pom.xml found in {project_path}, skipping batch processing"
            logging.warning(error_msg)
            return -1
            
        modules = self.pom_analyzer.parse_pom_for_modules(pom_path)
        if not modules:
            return -1
            
        logging.info(f"Found {len(modules)} modules in project:")
        for i, module in enumerate(modules, 1):
            logging.info(f"  {i}. {os.path.basename(module)}")
        
        results = []
        for module in modules:
            result = self.execute_module(module, project_name)
            results.append(result)
            
        self.results.print_project_results(project_name)
        return 0 if all(r == 0 for r in results) else 1

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
    
    args = parser.parse_args()
    
    translator = J2CJTranslator()
    
    if args.domain_path:
        return translator.execute_domain(args.domain_path)
    elif args.project_path:
        return translator.execute_project(args.project_path)
    elif args.module_path:
        return translator.execute_module(args.module_path, os.path.basename(args.module_path))

if __name__ == "__main__":
    main()
