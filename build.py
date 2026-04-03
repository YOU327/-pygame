import os
import subprocess
import sys

def build():
    # The main script to bundle
    main_script = "shit2.py"
    
    # Folders to include (assets)
    # Automatically include all subdirectories in the current folder that start with non-dot
    asset_dirs = []
    for item in os.listdir("."):
        if os.path.isdir(item) and not item.startswith(".") and item not in ["dist", "build", "__pycache__"]:
            asset_dirs.append(item)
    
    print(f"Detected asset directories: {asset_dirs}")
    
    # Construct PyInstaller command
    # --onefile: bundle everything into a single exe
    # --noconsole: don't show terminal window
    # --add-data: include folders
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        f"--name=shit2_compiled", # Output name
    ]
    
    for d in asset_dirs:
        # Syntax for --add-data: "source;destination" on Windows
        cmd.append(f"--add-data={d};{d}")
    
    cmd.append(main_script)
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful! Check the 'dist' folder for shit2_compiled.exe")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")

if __name__ == "__main__":
    build()
