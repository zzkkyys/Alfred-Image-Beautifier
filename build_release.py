import os
import sys
import xmltodict
import subprocess
import zipfile
import plistlib

PLIST_PATH = 'info.plist'
README_PATH = 'README.md'

# 1. 获取 info.plist 的 version 字段
def get_plist_version():

    with open('info.plist', 'rb') as f:
        plist_data = plistlib.load(f)

    version = plist_data.get('version')
    return version
# 2. 获取最新 git tag
def get_latest_tag():
    try:
        tag = subprocess.check_output(['git', 'tag', '--list', '--sort=-v:refname'], encoding='utf-8').split('\n')[0]
        return tag.strip() if tag else None
    except Exception:
        return None

# 3. 比较 version 和 tag
def should_release(version, tag):
    if not tag:
        return True
    # 只比较数字部分
    def norm(s):
        return [int(x) for x in s.strip('v').split('.') if x.isdigit()]
    return norm(version) > norm(tag)

# 4. 写入 readme 到 info.plist 的 readme 字段
def inject_readme():
    
    with open(PLIST_PATH, 'rb') as f:
        plist_data = plistlib.load(f)

    plist_data['readme'] = open(README_PATH).read()

    with open(PLIST_PATH, 'wb') as f:
        plistlib.dump(plist_data, f)
        
# 5. 打包为 alfredworkflow 文件
def make_zip(version):
    name = f'Alfred-Image-Beautifier-{version}.alfredworkflow'
    exclude = {'.git', '__pycache__', '.DS_Store'}
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk('.'):
            # 排除隐藏目录
            dirs[:] = [d for d in dirs if d not in exclude and not d.startswith('.')]
            for file in files:
                if file in exclude or file.endswith('.pyc') or file.startswith('.'):
                    continue
                path = os.path.join(root, file)
                arcname = os.path.relpath(path, '.')
                z.write(path, arcname)
    print(f'打包完成: {name}')
    return name

if __name__ == '__main__':
    version = get_plist_version()
    with open(os.environ['GITHUB_ENV'], 'a') as f:
        f.write(f"RELEASE_VERSION={version}\n")
    
    tag = get_latest_tag()
    print(f'info.plist version: {version}, latest tag: {tag}')
    if not should_release(version, tag):
        print('无需发布，version 未大于最新 tag')
        sys.exit(0)
    inject_readme()
    zipname = make_zip(version)
    print(f'::set-output name=workflow::{zipname}')
