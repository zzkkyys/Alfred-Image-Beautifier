import os
import subprocess
import platform



def show_macos_notification(title, message):
    import shlex
    # 转义引号，防止AppleScript语法错误
    safe_title = title.replace('"', '\\"')
    safe_message = message.replace('"', '\\"')
    script = f'display notification "{safe_message}" with title "{safe_title}"'
    try:
        subprocess.call(['osascript', '-e', script])
    except Exception as e:
        print(f"通知失败: {e}")



def get_download_folder():
    system = platform.system()
    if system == 'Windows':
        return os.path.join(os.getenv('USERPROFILE'), 'Downloads')
    elif system == 'Darwin':  # macOS
        return os.path.join(os.path.expanduser('~'), 'Downloads')
    elif system == 'Linux':
        return os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        raise OSError("Unsupported operating system")
    

def open_pdf_with_updf(pdf_path):
    if not pdf_path:
        print("No PDF files found.")
        return

    applescript = f'''
    tell application "UPDF"
        activate
        open POSIX file "{pdf_path}"
    end tell
    '''

    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing AppleScript: {result.stderr}")
    else:
        print(f"Opened {pdf_path} with UPDF.")