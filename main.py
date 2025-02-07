import config
import os
from github import Github
from colorama import Fore
import utill
from pathlib import Path
import time
import requests
import sys
import shutil


def main() -> None:
    config.check_config_file()
    main_menu()


'''Variables'''
server_path = Path(config.download_path + '/Server')
client_path = Path(config.download_path + '/Client')
download_directory: str = config.download_path


def main_menu() -> None:
    os.system('cls')

    print(
        Fore.CYAN + 'Menu',
        '',
        Fore.YELLOW + '1) Download nightly',
        Fore.YELLOW + '2) Install nightly',
        Fore.YELLOW + '3) Backup Client / Server',
        Fore.YELLOW + '4) Restore backup',
        Fore.YELLOW + '5) Exit',
        '',
        sep='\n')

    values: str = input(Fore.BLUE + 'Select action: ')
    utill.check_values('Invalid values', values, 5)

    match int(values):
        case 1:
            os.system('cls')
            donwload_nightly()
        case 2:
            os.system('cls')
            install_nightly()
        case 3:
            os.system('cls')
            menu_backup()
        case 4:
            os.system('cls')
            restore_backup()
        case 5:
            os.system('cls')
            sys.exit()


def donwload_nightly():
    os.system('cls')

    '''Variables'''
    token: str = config.config.get('General', 'token')
    repo_name: str = config.config.get('General', 'repo_name')

    git = Github(token)
    repo: object = git.get_repo(repo_name)
    artifacts: list = repo.get_artifacts()
    format_version: str = utill.check_format_version()
    artifact_format: str = config.config.get('Format', format_version)
    output_directory = download_directory

    '''Set output directory'''
    os.chdir(output_directory)
    match int(format_version):
        case 1 | 2 | 3:
            if not client_path.exists():
                client_path.mkdir()
            output_directory += '/Client'
        case 4 | 5:
            if not server_path.exists():
                server_path.mkdir()
            output_directory += '/Server'

    '''Show last versions nightly'''
    os.system('cls')
    print(Fore.CYAN + 'Last versions' + Fore.RESET)
    print('')

    count: int = 0
    for artifact in artifacts:
        nightly_name: str = artifact.name
        if count >= 10:
            break
        if nightly_name.endswith(artifact_format):
            print(Fore.GREEN + artifact.name + Fore.RESET)
            count += 1

    '''Input nightly versions'''
    print(Fore.BLUE + '')
    input_version_nightly: str = input('Select version nightly: ')
    os.system('cls')
    artifact_version: str = '+' + input_version_nightly + '-'

    '''Download nightly'''
    for artifact in artifacts:
        nightly_name: str = artifact.name

        if artifact_version in nightly_name and nightly_name.endswith(artifact_format):
            artifact_download_url: str = artifact.archive_download_url
            headers = {'Authorization': f'token {token}'}

            print(Fore.GREEN + 'Artifact name: ', artifact.name, '\n')

            start_time: time = time.time()
            response = requests.get(
                artifact_download_url, headers=headers, stream=True)

            if not response.status_code == 200:
                print(Fore.RED + f"Error downloading artifact: '{artifact.name}': {
                      response.status_code} {response.reason}", '\n')

            output_directory_path = Path(output_directory + '/' + nightly_name)
            if not output_directory_path.exists():
                output_directory_path.mkdir()
            else:
                utill.delete_everything_in_folder(
                    output_directory_path.__str__())

            artifact_path: str = os.path.join(
                output_directory_path.__str__(), f'{artifact.name}.zip')

            total_size: str = int(response.headers.get('Content-Length', 0))

            print(Fore.GREEN + 'Size artifact: ' + Fore.WHITE +
                  f'{total_size / (1024 * 1024):.2f} MB', '\n')

            download_size: int = 0

            with open(artifact_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        download_size += len(chunk)

                        print(Fore.GREEN + f'Download: ' + Fore.WHITE + f'{download_size / (
                            1024 * 1024):.2f} MB of {total_size / (1024 * 1024):.2f} MB', end='\r')
            elapsed_time: time = time.time() - start_time
            print('')
            print(
                Fore.GREEN + f"\nArtifact download by " + Fore.WHITE + f"{elapsed_time:.2f} second.", '\n')
    utill.zip_manipulation(output_directory_path.__str__())
    input(Fore.MAGENTA + 'Press enter:')
    main_menu()


def install_nightly() -> None:
    os.system('cls')

    '''Variables'''
    current_directory: str = ''
    current_name_directory: str = ''
    minecraft_directory = config.config.get('General', 'minecraft_directory')
    minecraft_server_directory = config.config.get(
        'General', 'server_directory')

    print(
        Fore.CYAN + 'Menu',
        '',
        Fore.YELLOW + '1) Client',
        Fore.YELLOW + '2) Server',
        Fore.YELLOW + '3) Back',
        '',
        sep='\n')

    values = input(Fore.BLUE + 'Select action: ')
    utill.check_values('Invalid values', values, 3)

    match int(values):
        case 1:
            os.system('cls')
            current_directory = download_directory + '/Client'
            current_name_directory = 'Client'
        case 2:
            os.system('cls')
            current_directory = download_directory + '/Server'
            current_name_directory = 'Server'
        case 3:
            os.system('cls')
            main_menu()

    folders = utill.get_folders_in_directory(current_directory)

    if any(folders):
        print(Fore.RED + 'Installed nightly' + Fore.RESET)
        print('')

        count: int = 1
        for folder in folders:
            print(count.__str__() + ') ' + folder.name)
            count += 1
    else:
        print('')
        print(Fore.RED + 'Not found installed nightly' + Fore.RESET)
        print('')
        input(Fore.MAGENTA + 'Press enter: ')
        main_menu()

    '''Input folder'''
    print(Fore.BLUE + '')
    input_folder = input('Select nightly: ')
    utill.check_values('Invalid values', input_folder, len(folders))
    if int(input_folder) < 0:
        input_folder = 1
    num_folder = int(input_folder)
    num_folder -= 1

    current_directory = current_directory + '/' + folders[num_folder].name
    os.system('cls')
    os.chdir(current_directory)

    '''Copy/Paste file'''
    match current_name_directory:
        case 'Client':
            for client_directory in config.directory_client_backup:
                try:
                    folder_name_client = utill.find_folder_in_directory(
                        current_directory, client_directory)
                    for root, dirs, files in os.walk(minecraft_directory):
                        if os.path.isdir(str(root) + '/' + str(client_directory)):
                            '''Delete old folder'''
                            old_minecraft_directory = os.path.join(
                                root, client_directory)
                            shutil.rmtree(old_minecraft_directory)
                    match client_directory:
                        case 'libraries' | 'patches':
                            utill.copy_directory(
                                folder_name_client, minecraft_directory + '/' + client_directory)
                        case 'mods' | 'config':
                            utill.copy_directory(
                                folder_name_client, minecraft_directory + '/.minecraft' + '/' + client_directory)
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    sys.exit()
        case 'Server':
            for server_directory in config.directory_server_backup:
                try:
                    folder_name_server = utill.find_folder_in_directory(
                        current_directory, server_directory)
                    for root, dirs, files in os.walk(minecraft_server_directory):
                        if os.path.isdir(str(root) + '/' + str(server_directory)):
                            '''Delete old folder'''
                            old_minecraft_server_directory = os.path.join(
                                root, server_directory)
                            shutil.rmtree(old_minecraft_server_directory)
                        utill.copy_directory(
                            folder_name_server, minecraft_server_directory + '/' + server_directory)
                        break
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    sys.exit()
    print(Fore.CYAN + 'Nightly install successfully')
    print('')
    input(Fore.MAGENTA + 'Press enter: ')
    main_menu()


def menu_backup():
    os.system('cls')
    print(
        Fore.CYAN + 'Menu',
        '',
        Fore.YELLOW + '1) Backup Client',
        Fore.YELLOW + '2) Backup Server',
        Fore.YELLOW + '3) Back',
        '',
        sep='\n')
    values = input(Fore.BLUE + 'Select action: ')
    utill.check_values('Invalid values', values, 3)

    match int(values):
        case 1:
            os.system('cls')
            backup('Client')
        case 2:
            os.system('cls')
            backup('Server')
        case 3:
            os.system('cls')
            main_menu()


def backup(action):
    minecraft_directory = config.config.get('General', 'minecraft_directory')
    minecraft_server_directory = config.config.get(
        'General', 'server_directory')

    match action:
        case 'Client':
            for client_directory in config.directory_client_backup:
                try:
                    folder_name_client = utill.find_folder_in_directory(
                        minecraft_directory, client_directory)

                    if os.path.exists(folder_name_client):
                        os.rename(folder_name_client, str(
                            folder_name_client) + '1')
                        print(
                            Fore.GREEN + f'Folder {os.path.basename(folder_name_client)} successfully backup', '\n')
                    else:
                        print(
                            Fore.RED + f'{os.path.basename(folder_name_client)} folder doesnt exist', '\n')
                except FileExistsError:
                    print(
                        Fore.RED + f'{os.path.basename(folder_name_client)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    sys.exit()
        case 'Server':
            for server_directory in config.directory_server_backup:
                try:
                    folder_name_server = utill.find_folder_in_directory(
                        minecraft_server_directory, server_directory)

                    if os.path.exists(folder_name_server):
                        os.rename(folder_name_server, str(
                            folder_name_server) + '1')
                        print(
                            Fore.GREEN + f'Folder {os.path.basename(folder_name_server)} successfully backup', '\n')
                    else:
                        print(
                            Fore.RED + f'{os.path.basename(folder_name_server)} folder doesnt exist', '\n')
                except FileExistsError:
                    print(
                        Fore.RED + f'{os.path.basename(folder_name_server)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    sys.exit()
        case _:
            print(Fore.RED + 'Error', '\n')
            sys.exit()


def restore_backup():
    minecraft_directory = config.config.get('General', 'minecraft_directory')
    minecraft_server_directory = config.config.get(
        'General', 'server_directory')

    print(
        Fore.CYAN + 'Menu',
        '',
        Fore.YELLOW + '1) Client',
        Fore.YELLOW + '2) Server',
        Fore.YELLOW + '3) Back',
        '',
        sep='\n')
    values = input(Fore.BLUE + 'Select action: ')
    utill.check_values('Invalid values', values, 3)
    os.system('cls')

    match int(values):
        case 1:
            for client_directory in config.directory_client_backup:
                try:
                    folder_name_client = utill.find_folder_in_directory(
                        minecraft_directory, client_directory + '1')

                    if os.path.exists(folder_name_client):
                        if os.path.exists(folder_name_client[:-1]):
                            shutil.rmtree(folder_name_client[:-1])
                        os.rename(folder_name_client, folder_name_client[:-1])
                        print(
                            Fore.GREEN + f'Folder {os.path.basename(folder_name_client)} successfully restore', '\n')
                    else:
                        print(
                            Fore.RED + f'{os.path.basename(folder_name_client)} folder doesnt exist', '\n')
                except FileExistsError:
                    print(
                        Fore.RED + f'{os.path.basename(folder_name_client)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    sys.exit()
        case 2:
            for server_directory in config.directory_server_backup:
                try:
                    folder_name_server = utill.find_folder_in_directory(
                        minecraft_server_directory, server_directory + '1')
                    if os.path.exists(folder_name_server):
                        if os.path.exists(folder_name_server[:-1]):
                            shutil.rmtree(folder_name_server[:-1])
                        os.rename(folder_name_server, folder_name_server[:-1])
                        print(
                            Fore.GREEN + f'Folder {os.path.basename(folder_name_server)} successfully restore', '\n')
                    else:
                        print(
                            Fore.RED + f'{os.path.basename(folder_name_server)} folder doesnt exist', '\n')
                except FileExistsError:
                    print(
                        Fore.RED + f'{os.path.basename(folder_name_server)} folder already has a backup', '\n')
                except Exception as e:
                    print(Fore.RED + f'Error: {e}')
                    sys.exit()
        case 3:
            main_menu()
        case _:
            print(Fore.RED + 'Error', '\n')
            sys.exit()

    input(Fore.MAGENTA + 'Backup successfully restore press enter:')
    main_menu()


if __name__ == "__main__":
    main()
