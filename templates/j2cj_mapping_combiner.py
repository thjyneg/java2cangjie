import os
from mapping_file_Combiner import MappingFileCombiner
import argparse

# 根目录，所有东西都应该在此根目录下

MAPPING_PATH = os.getenv('MAPPING_PATH', '/opt/j2cj_tools/mapping')

def generate_root_cjmap_file(workspace_path):
    print(f"create root.cjmap in {workspace_path}...")
    
    root_mapping = os.path.join(workspace_path, "root.cjmap")
    ext_cjdef = os.path.join(workspace_path, "ext.cjdef")
    ext_cjmap = os.path.join(workspace_path, "ext.cjmap")
    # 删除旧文件
    for file_path in [root_mapping, ext_cjdef, ext_cjmap]:
        try:
            os.remove(file_path)
        except OSError:
            pass  # 文件不存在时忽略

    # 写入 root.cjmap 内容
    with open(root_mapping, 'w', encoding='utf-8') as f:
        f.write('// J2CJ自带映射文件\n')
        f.write('#include "stdlib.cjmap"\n')
        f.write('#include "mappings.cjmap"\n')
        f.write('// J2CJ扩展映射文件\n')
        f.write('#include "ext.cjmap"\n')
        f.write('#include "ext.cjdef"\n')

            # 创建 ext.cjdef 和 ext.cjmap 文件
        with open(ext_cjdef, 'w', encoding='utf-8') as cjdef_file:
            cjdef_file.write('// 扩展定义文件\n')
        with open(ext_cjmap, 'w', encoding='utf-8') as cjmap_file:
            cjmap_file.write('// 扩展映射文件\n')
            for root, _, files in os.walk(MAPPING_PATH):
                for file in files:
                    if file.endswith(".cjmap"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as temp:
                            cjmap_file.write(temp.read())
                            cjmap_file.write('\n')
        combiner = MappingFileCombiner(workspace_path)
        combiner.dealMappingFile()
    print("create root.cjmap finish.")

def main():
    parser = argparse.ArgumentParser(description='J2CJ project analysis tool')
    parser.add_argument('-d', '--directory', type=str, required=True,
                       help='Project directory path')
    args = parser.parse_args()                   
    generate_root_cjmap_file(args.directory)

if __name__ == "__main__":
    main()
