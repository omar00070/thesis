from os import walk
from typing import List
## helper function


def get_files_dirs(path: str) -> List[str]:
    '''
        get all the files in a directory path
        :param path:    path to the files or directories
        :return:        list of files, list of direcotries in the path
    '''
    f = []
    dirs = []
    for (_, dirnames, filenames) in walk(path):
        f.extend(filenames)
        dirs.extend(dirnames)
        break
    return f, dirs
