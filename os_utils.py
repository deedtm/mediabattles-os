import os


def get_cwd_path(path: str):
    tree = path.split('/')
    return os.path.join(os.getcwd(), *tree)
