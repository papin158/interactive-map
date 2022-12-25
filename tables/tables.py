import os
import re


def __get_derictories(path) -> dict:
    path = f'./{path}/'
    all_files = [i for i in os.listdir(path)]
    dirs = [i for i in all_files if os.path.isdir(f'{path}{i}')]
    other_files = {
        "Другое": [i[0:-4] for i in all_files if os.path.isfile(path=f'{path}{i}') and re.search(r".+\.csv$", i)]}

    directories = {i: [j[0:-4] for j in os.listdir(path=f'{path}{i}') if re.search(r"\w+\.csv$", j)] for i in dirs}

    if other_files['Другое']:
        directories |= other_files

    return directories
