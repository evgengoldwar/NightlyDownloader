import os
import shutil
from colorama import Fore
import sys
import zipfile
from pathlib import Path


def find_folder_in_directory(directory, folder_name):
    for root, dirs, files in os.walk(directory):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return str(directory) + '/' + str(folder_name)


def copy_directory(src, dst):
    try:
        if not os.path.exists(src):
            print(
                Fore.RED + f'Folders {os.path.basename(src)} not found.', '\n')
            return

        if os.path.exists(dst):
            print(
                Fore.RED + f'Target folder {os.path.basename(dst)} already exists.', '\n')
            return

        shutil.copytree(src, dst)
        print(Fore.GREEN + f'Folder {os.path.basename(src)
                                     } successfully copied to {dst}.', '\n')
    except Exception as e:
        print(Fore.RED + f'Copying error: {e}', '\n')


def delete_everything_in_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)
    os.chdir('..')


def get_real_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))


def check_values(message: str, values: int, limit: int) -> None:
    try:
        if int(values) > limit:
            os.system('cls')
            print(Fore.RED + message, '\n' + Fore.RESET)
            sys.exit()
    except Exception:
        print(Fore.RED + message, '\n')


def zip_manipulation(output_dir: str):
    for i in os.listdir(output_dir):
        if i.endswith(".zip"):
            zipFile = i
            artifact_path: str = os.path.join(output_dir, zipFile)

            if os.path.exists(artifact_path):
                with zipfile.ZipFile(artifact_path, "r") as zip_ref:
                    zip_ref.extractall(output_dir)
                    for name in zip_ref.namelist():
                        info = zip_ref.getinfo(name)
                        zip_name = os.path.basename(info.filename)
                        zip_path = os.path.join(output_dir, zip_name)
                        with zipfile.ZipFile(zip_path, "r") as zf:
                            zf.extractall(output_dir)

                    print(Fore.GREEN + 'Artifact unzip: ' +
                          Fore.WHITE + f'{zipFile}', '\n')


def get_folders_in_directory(directory):
    path = Path(directory)
    folders = [folder for folder in path.iterdir() if folder.is_dir()]
    return folders


def check_format_version() -> str:
    os.system('cls')

    print(
        Fore.CYAN + "Menu",
        Fore.YELLOW + "1 : manifest.json",
        Fore.YELLOW + "2 : mmcprism-java8",
        Fore.YELLOW + "3 : mmcprism-new-java",
        Fore.YELLOW + "4 : server",
        Fore.YELLOW + "5 : server-new-java",
        "", sep="\n")

    format_version: str = input(Fore.BLUE + 'Format version: ')
    check_values('Invalid format', format_version, 5)
    return format_version


def copy_directory(src, dst):
    try:
        if not os.path.exists(src):
            print(
                Fore.RED + f'Folders {os.path.basename(src)} not found.', '\n')
            return

        if os.path.exists(dst):
            print(
                Fore.RED + f'Target folder {os.path.basename(dst)} already exists.', '\n')
            return

        shutil.copytree(src, dst)
        print(Fore.GREEN + f'Folder {os.path.basename(src)
                                     } successfully copied to {Fore.BLUE + dst}.', '\n')
    except Exception as e:
        print(Fore.RED + f'Copying error: {e}', '\n')
