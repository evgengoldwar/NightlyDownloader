import configparser
from colorama import Fore
import os
from pathlib import Path
import utill


config = configparser.ConfigParser()
real_path: str = utill.get_real_path().__str__()
download_path: str = real_path + '/Downloads'

directory_client_backup = [
    'libraries', 'patches', 'mods', 'config'
]
directory_server_backup = [
    'libraries', 'config', 'mods'
]


def create_config():
    os.system('cls')

    '''Input variables'''
    input_github_token: str = input(Fore.GREEN + "Github token: " + Fore.CYAN)
    print('')
    input_minecraft_directory: str = input(
        Fore.GREEN + "Minecraft derectory: " + Fore.CYAN)
    print('')
    input_server_directory: str = input(
        Fore.GREEN + "Server directory: " + Fore.CYAN)

    config['General'] = {
        'rebuild_config': 2,
        'token': input_github_token,
        'repo_name': 'GTNewHorizons/DreamAssemblerXXL',
        'minecraft_directory': input_minecraft_directory,
        'server_directory': input_server_directory
    }

    config['Format'] = {
        '1': 'manifest.json',
        '2': 'mmcprism-java8',
        '3': 'mmcprism-new-java',
        '4': 'server',
        '5': 'server-new-java'
    }

    download_directory = Path(download_path)

    if not download_directory.exists():
        download_directory.mkdir()

    with open(real_path + '/config.ini', 'w') as cfg:
        config.write(cfg)


def check_config_file():
    os.system('cls')

    try:
        config.read(real_path + '/config.ini')

        if config.get('General', 'rebuild_config') in '1':
            create_config()
        else:
            print(
                Fore.CYAN + 'Rebuild config file?',
                '',
                Fore.YELLOW + '1) True',
                Fore.YELLOW + '2) False',
                '',
                sep='\n' + Fore.RESET)
            values: str = input(Fore.BLUE + 'Select action: ')
            utill.check_values('Invalid values', values, 2)
            config.set('General', 'rebuild_config', values)
            with open(real_path + '/config.ini', 'w') as cfg:
                config.write(cfg)
            os.system('cls')
    except Exception:
        create_config()
