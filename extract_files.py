import gzip
import shutil
from typing import List
import os
from helpers.helpers import get_files_dirs
import tqdm

PATH = 'omar_data/'



def extract_files_and_delete_gz(files: List[str]):

    def _extract_file(filename):
        with gzip.open(filename, 'rb') as f_in:
            with open(filename[:-2], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    with tqdm(total=len(files)) as t:
        for file in files:
            _extract_file(file)
            os.remove(file)
            t.update(1)

if __name__ == '__main__':
    _, dirs = get_files_dirs(PATH)
    for _dir in dirs:
        files, _ = get_files_dirs(PATH + _dir)
        extract_files_and_delete_gz(files)