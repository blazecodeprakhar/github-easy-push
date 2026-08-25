import subprocess
import sys
import os
import shutil

def build():
    print("==================================================")
    print("  Building GitHub Easy Push Single Standalone EXE ")
    print("==================================================")

    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[*] PyInstaller not found. Installing pyinstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    icon_path = os.path.abspath("icon.png")

    # Use --onefile to embed python313.dll and all runtime libraries directly into the single executable
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=GitHub_Easy_Push",
        f"--icon={icon_path}",
        f"--add-data={icon_path};.",
        "main.py"
    ]

    print(f"[*] Running command: {' '.join(cmd)}")
    res = subprocess.call(cmd)
    if res == 0:
        dist_exe = os.path.abspath(os.path.join("dist", "GitHub_Easy_Push.exe"))
        root_exe = os.path.abspath("GitHub_Easy_Push.exe")
        shutil.copy(dist_exe, root_exe)

        print("==================================================")
        print(" BUILD SUCCESSFUL!")
        print(f" Single Portable EXE generated & placed at: {root_exe}")
        print("==================================================")
    else:
        print("==================================================")
        print(" BUILD FAILED. Check PyInstaller logs above.")
        print("==================================================")

if __name__ == "__main__":
    build()
