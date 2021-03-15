import gzip
import shutil
from typing import List
import os
from helpers.helpers import get_files_dirs
from tqdm import tqdm

PATH = 'omar_data/'


def extract_files_and_delete_gz(files: List[str]):

    def _extract_file(filepath):
        with gzip.open(filepath, 'rb') as f_in:
            with open(filepath[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    with tqdm(total=len(files)) as t:
        for file in files:
            if file.endswith('.gz'):
                _extract_file(PATH + file)
                os.remove(PATH + file)
            elif not file.endswith('.grb'):
                print(file)
            t.update(1)


if __name__ == '__main__':
    files, dirs = get_files_dirs(PATH)
    extract_files_and_delete_gz(files)