# System imports
import platform
import subprocess
import sys
from pathlib import Path

# Third party imports
import pyinstaller_versionfile

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR)

SEPARATOR = ':.'
MAIN_PATH = "main.py"
ICON_PATH = str(BASE_DIR) + "/deploy/static/bot.icns"
DIST_PATH = "deploy/output/macOS/dist"
BUILD_PATH = "deploy/output/macOS/build"
SPEC_PATH = "deploy/output/macOS"
VERSION_FILE_PATH = ""
METADATA_PATH = ""

if platform.system() == 'Windows':
    SEPARATOR = ';.'
    MAIN_PATH = "main.py"
    ICON_PATH = str(BASE_DIR) + "\\deploy\\static\\bot.ico"
    DIST_PATH = "deploy\\output\\windows\\dist"
    BUILD_PATH = "deploy\\output\\windows\\build"
    SPEC_PATH = "deploy\\output\\windows"
    VERSION_FILE_PATH = f"{BASE_DIR}\\VERSIONFILE.txt"
    METADATA_PATH = f"{BASE_DIR}\\metadata.yml"

if __name__ == "__main__":

    cmd = ['python', '-m', 'PyInstaller',
           '--name', 'Bianche',
           '--noconfirm',
           '--windowed',
           '--noconsole',
           '--onefile', MAIN_PATH,
           '--add-data', ICON_PATH + SEPARATOR,
           '--distpath', DIST_PATH,
           '--workpath', BUILD_PATH,
           '--specpath', SPEC_PATH,
           '--icon', ICON_PATH
           ]

    if platform.system() == 'Darwin':
        subprocess.run(cmd, check=True, cwd=BASE_DIR)
    elif platform.system() == 'Windows':
        cmd.extend(['--version-file', VERSION_FILE_PATH])

        # Manage Windows version metadata
        pyinstaller_versionfile.create_versionfile_from_input_file(
            output_file=VERSION_FILE_PATH,
            input_file=METADATA_PATH,
        )

        subprocess.run(cmd, check=True, shell=True, cwd=BASE_DIR)
