import os
import subprocess
import platform


def show_macos_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.call(['osascript', '-e', script])



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