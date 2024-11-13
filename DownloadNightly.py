from github import Github
from colorama import init
init(autoreset=True)
from colorama import Fore, Back, Style
import os
import requests
import time
import zipfile
import configparser
import shutil




config = configparser.ConfigParser()
clear = lambda: os.system('cls')
createDir = lambda: os.mkdir('Downloads')
osExit = lambda: os._exit(0)
dirsClientBackup = [
        'libraries', 'patches', 'mods', 'config'
    ]
dirsServerBackup = [
        'libraries', 'config', 'mods'
]




def main():
    clear()
    check_config_file()
    dialog_menu()

    



def dialog_menu():
    clear()
    print(Fore.CYAN + 'Menu', '', Fore.YELLOW + '1) Download nightly', Fore.YELLOW + '2) Install nightly', Fore.YELLOW + '3) Backup Client / Server', Fore.YELLOW + '4) Restore backup', Fore.YELLOW + '5) Exit', '', sep='\n')
    values = input(Fore.BLUE + 'Select action: ')
    check_values('Invalid values', values, 5)

    match int(values):
        case 1:
            clear()
            download_nightly()
        case 2:
            clear()
            check_install_nightly()
        case 3:
            clear()
            dialolg_menu_backup()
        case 4:
            clear()
            restore_backup()
        case 5:
            clear()
            osExit()


def check_config_file():
    try:
            var = os.path.dirname(os.path.realpath(__file__))
            config.read(var + '/Downloads/config.ini')

            if config.get('General', 'regenerateConfig') in '1':
                create_config()
            else: 
                print(Fore.CYAN + 'Regenerate config file?', '', Fore.YELLOW + '1) True', Fore.YELLOW + '2) False', '', sep='\n')
                values = input(Fore.BLUE + "Select action: ")
                check_values('Invalid values', values, 2)
                config.set('General', 'regenerateConfig', values)
                with open(var + '/Downloads/config.ini', 'w') as configfile:
                    config.write(configfile)
            clear()
    except:
        create_config()


def create_config():
    input_github_token = input(Fore.GREEN + "Github token: " + Fore.CYAN)
    print('')
    input_output_directory = os.path.dirname(os.path.realpath(__file__))
    input_minecraft_directory = input(Fore.GREEN + "Minecraft derectory: " + Fore.CYAN)
    print('')
    input_server_directory = input(Fore.GREEN + "Server directory: " + Fore.CYAN)

    config['General'] = {
                    'regenerateConfig' : 2,
                    'token' : input_github_token,
                    'outDir' : input_output_directory,
                    'repoName' : 'GTNewHorizons/DreamAssemblerXXL',
                    'minecraft_directory' : input_minecraft_directory,
                    'server_directory' : input_server_directory
                }
    config['Format'] = {
                    1 : 'manifest.json',
                    2 : 'mmcprism-java8',
                    3 : 'mmcprism-new-java',
                    4 : 'server',
                    5 : 'server-new-java'
                }
    
    if not os.path.isdir(input_output_directory + '/Downloads'):
        os.chdir(input_output_directory)
        createDir()

    with open(input_output_directory + '/Downloads/config.ini', 'w') as configfile:
        config.write(configfile)


def download_nightly():
    clear()
    token = config.get('General', 'token')
    g = Github(token)

    repo_name = config.get('General', 'repoName')
    repo = g.get_repo(repo_name)

    input_version_nightly = input('Select version nightly: ')
    clear()

    artifacts = repo.get_artifacts()
    artifact_version = "+" + input_version_nightly + "-"

    print(Fore.CYAN + "Menu", Fore.YELLOW + "1 : manifest.json", Fore.YELLOW + "2 : mmcprism-java8", Fore.YELLOW + "3 : mmcprism-new-java", Fore.YELLOW + "4 : server", Fore.YELLOW + "5 : server-new-java", "", sep= "\n")
    formatVersion = input(Fore.BLUE + "Format version: ")
    check_values('Invalid format', formatVersion, 5)
    artifact_format = config.get('Format', formatVersion)
    output_directory = config.get('General', 'outDir') + "/Downloads/"
    os.chdir(output_directory)

    match int(formatVersion):
        case 1 | 2 | 3:
            if not os.path.isdir('Client'):
                os.mkdir('Client')
            output_directory += 'Client'
            delete_everything_in_folder('Client')
            
        case 4 | 5:
            if not os.path.isdir('Server'):
                os.mkdir('Server')
            output_directory += 'Server'
            delete_everything_in_folder('Server')


    for artifact in artifacts:
        nightly_name = artifact.name

        if artifact_version in nightly_name and nightly_name.endswith(artifact_format):
            artifact_download_url = artifact.archive_download_url
            headers = {'Authorization': f'token {token}'}

            print(Fore.GREEN + 'Artifact name: ',artifact.name, '\n')

            start_time = time.time()
            response = requests.get(artifact_download_url, headers=headers, stream=True)

            if response.status_code == 200:
                
                artifact_path = os.path.join(output_directory, f"{artifact.name}.zip")

                total_size = int(response.headers.get("Content-Length", 0))
                print(Fore.GREEN + 'Size artifact: ' + Fore.WHITE + f'{total_size / (1024 * 1024):.2f} MB', '\n')

                downloaded_size = 0

                with open(artifact_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                            print(Fore.GREEN + f'Download: '+ Fore.WHITE + f'{downloaded_size / (1024 * 1024):.2f} MB of {total_size / (1024 * 1024):.2f} MB', end='\r')
                elapsed_time = time.time() - start_time
                print('')
                print(Fore.GREEN + f"\nArtifact download by {elapsed_time:.2f} second.", '\n')
            else:
                print(Fore.RED + f"Error downloading artifact: '{artifact.name}': {response.status_code} {response.reason}", '\n')
    input(Fore.MAGENTA + 'Press enter:')
    zip_manipulation(output_directory)
    os.chdir("..")


def zip_manipulation(outputDir):
    clear()
    for i in os.listdir(outputDir):
        if i.endswith(".zip"):
            zipFile = i
            artifact_path = os.path.join(outputDir, zipFile)

            if os.path.exists(artifact_path):
                with zipfile.ZipFile(artifact_path, "r") as zip_ref:
                    zip_ref.extractall(outputDir)
                    for name in zip_ref.namelist():
                        info = zip_ref.getinfo(name)
                        zip_name = os.path.basename(info.filename)
                        zip_path = os.path.join(outputDir, zip_name)
                        with zipfile.ZipFile(zip_path, "r") as zf:
                            zf.extractall(outputDir)

                    print(Fore.GREEN + 'Artifact unzip:'+ Fore.WHITE + f'{zipFile}', '\n')
    input(Fore.MAGENTA + 'Press enter:')
    dialog_menu()


def check_install_nightly():
    clear()
    output_directory = config.get('General', 'outDir') + "/Downloads/"
    mineDir = config.get('General', 'minecraft_directory')
    servDir = config.get('General', 'server_directory')

    print(Fore.CYAN + 'Menu', '', Fore.YELLOW + '1) Client', Fore.YELLOW + '2) Server', Fore.YELLOW + '3) Back', '', sep='\n')
    values = input(Fore.BLUE + 'Select actioin: ')
    check_values('Invalid values', values, 3)
    os.chdir(output_directory)

    match int(values):
        case 1:
            if os.path.isdir('Client'):
                outDir = output_directory + 'Client'
                print(Fore.CYAN + 'Bacukup', '\n')
                backup('Client')
                print(Fore.CYAN + 'Install', '\n')
                for dirsC in dirsClientBackup:
                    try:
                        folder_name_client = find_folder_in_directory(outDir, dirsC)
                        for root, dirs, files in os.walk(mineDir):
                            if os.path.isdir(str(root) + '/' + str(dirsC)):
                                dirsClient = os.path.join(root, dirsC)
                                shutil.rmtree(dirsClient)
                        match dirsC:
                            case 'libraries' | 'patches':
                                copy_directory(folder_name_client, mineDir + '/' + dirsC)
                            case 'mods' | 'config':
                                copy_directory(folder_name_client, mineDir + '/.minecraft' + '/' + dirsC)
                    except Exception as e:
                        print(Fore.RED + f'Error: {e}')
                        osExit()
        case 2:
            if os.path.isdir('Server'):
                outDir = output_directory + 'Server'
                print(Fore.CYAN + 'Bacukup', '\n')
                backup('Server')
                print(Fore.CYAN + 'Install', '\n')
                for dirsS in dirsServerBackup:
                    try:
                        folder_name_server = find_folder_in_directory(outDir, dirsS)
                        for root, dirs, files in os.walk(servDir):
                            if os.path.isdir(str(root) + '/' + str(dirsS)):
                                dirsServer = os.path.join(root, dirsS)
                                shutil.rmtree(dirsServer)
                            copy_directory(folder_name_server, servDir + '/' + dirsS)
                            break
                    except Exception as e:
                        print(Fore.RED + f'Error: {e}')
                        osExit()
        case 3:
            dialog_menu()
    input(Fore.MAGENTA + 'Artifact successfully install press enter:')
    dialog_menu()


def backup(action):
    mineDir = config.get('General', 'minecraft_directory')
    servDir = config.get('General', 'server_directory')

    match action:
        case 'Client':
            for dirsC in dirsClientBackup:
                try:
                    folder_name_client = find_folder_in_directory(mineDir, dirsC)

                    if os.path.exists(folder_name_client):
                        os.rename(folder_name_client, str(folder_name_client) + '1')
                        print(Fore.GREEN + f'Folder {os.path.basename(folder_name_client)} successfully backup', '\n')
                    else:
                        print(Fore.RED + f'{os.path.basename(folder_name_client)} folder doesnt exist', '\n')
                except FileExistsError as e:
                    print(Fore.RED + f'{os.path.basename(folder_name_client)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    osExit()
        case 'Server':
            for dirsS in dirsServerBackup:
                try:
                    folder_name_server = find_folder_in_directory(servDir, dirsS)

                    if os.path.exists(folder_name_server):
                        os.rename(folder_name_server, str(folder_name_server) + '1')
                        print(Fore.GREEN + f'Folder {os.path.basename(folder_name_server)} successfully backup', '\n')
                    else:
                        print(Fore.RED + f'{os.path.basename(folder_name_server)} folder doesnt exist', '\n')
                except FileExistsError as e:
                    print(Fore.RED + f'{os.path.basename(folder_name_server)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    osExit()
        case _:
            print(Fore.RED + 'Error', '\n')
            osExit()


def dialolg_menu_backup():
    clear()
    print(Fore.CYAN + 'Menu', '', Fore.YELLOW + '1) Backup Client', Fore.YELLOW + '2) Backup Server', Fore.YELLOW + '3) Back', '', sep='\n')
    values = input(Fore.BLUE + 'Select action: ')
    check_values('Invalid values', values, 3)

    match int(values):
        case 1:
            clear()
            backup('Client')
        case 2:
            clear()
            backup('Server')
        case 3:
            clear()
            dialog_menu()


def restore_backup():
    mineDir = config.get('General', 'minecraft_directory')
    servDir = config.get('General', 'server_directory')

    print(Fore.CYAN + 'Menu', '', Fore.YELLOW + '1) Client', Fore.YELLOW + '2) Server', Fore.YELLOW + '3) Back', '', sep='\n')
    values = input(Fore.BLUE + 'Select action: ')
    check_values('Invalid values', values, 3)
    clear()

    match int(values):
        case 1:
            for dirsC in dirsClientBackup:
                try:
                    folder_name_client = find_folder_in_directory(mineDir, dirsC + '1')

                    if os.path.exists(folder_name_client):
                        if os.path.exists(folder_name_client[:-1]):
                            shutil.rmtree(folder_name_client[:-1])
                        os.rename(folder_name_client, folder_name_client[:-1])
                        print(Fore.GREEN + f'Folder {os.path.basename(folder_name_client)} successfully restore', '\n')
                    else:
                        print(Fore.RED + f'{os.path.basename(folder_name_client)} folder doesnt exist', '\n')
                except FileExistsError as e:
                    print(Fore.RED + f'{os.path.basename(folder_name_client)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    osExit()
        case 2:
            for dirsS in dirsServerBackup:
                try:
                    folder_name_server = find_folder_in_directory(servDir, dirsS + '1')
                    if os.path.exists(folder_name_server):
                        if os.path.exists(folder_name_server[:-1]):
                            shutil.rmtree(folder_name_server[:-1])
                        os.rename(folder_name_server, folder_name_server[:-1])
                        print(Fore.GREEN + f'Folder {os.path.basename(folder_name_server)} successfully restore', '\n')
                    else:
                        print(Fore.RED + f'{os.path.basename(folder_name_server)} folder doesnt exist', '\n')
                except FileExistsError as e:
                    print(Fore.RED + f'{os.path.basename(folder_name_server)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    osExit()
        case 3:
            dialog_menu()
        case _:
            print(Fore.RED + 'Error', '\n')
            osExit() 

    input(Fore.MAGENTA + 'Backup successfully restore press enter:')
    dialog_menu() 


def check_values(message, values, limit):

    clear()
    try:
        if int(values) > limit:
            print(Fore.RED + message, '\n')
            osExit()
    except ValueError:
        print(Fore.RED + message, '\n')
        osExit()


def delete_everything_in_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)
    os.chdir('..')


def copy_directory(src, dst):
    try:
        if not os.path.exists(src):
            print(Fore.RED + f'Folders {os.path.basename(src)} not found.', '\n')
            return
        
        if os.path.exists(dst):
            print(Fore.RED + f'Target folder {os.path.basename(dst)} already exists.', '\n')
            return
        
        shutil.copytree(src, dst)
        print(Fore.GREEN + f'Folder {os.path.basename(src)} successfully copied to {dst}.', '\n')
    except Exception as e:
        print(Fore.RED + f'Copying error: {e}', '\n')


def find_folder_in_directory(directory, folder_name):
    for root, dirs, files in os.walk(directory):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return str(directory) + '/' + str(folder_name)


main()