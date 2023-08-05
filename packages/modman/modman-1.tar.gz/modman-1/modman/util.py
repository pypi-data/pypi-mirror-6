from contextlib import contextmanager
import os
import importlib
import shutil
import tempfile


@contextmanager
def tempdir():
    dirname = tempfile.mkdtemp()
    try:
        yield dirname
    finally:
        shutil.rmtree(dirname)


def load(import_path):
    module_name, func_name = import_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def guess_extension(url):
    last_part = url.split('/')[-1]
    if '.' in last_part:
        return last_part.split('.')[-1]
    else:
        return ''


def default_installer(workspace, game_location):
    installed_files = []
    for base_path, dirs, files in os.walk(workspace):
        for dir_name in dirs:
            src_path = os.path.join(base_path, dir_name)
            rel_path = os.path.relpath(src_path, workspace)
            dst_path = os.path.join(game_location, rel_path)
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)
        for file_name in files:
            src_path = os.path.join(base_path, file_name)
            rel_path = os.path.relpath(src_path, workspace)
            dst_path = os.path.join(game_location, rel_path)
            shutil.copyfile(src_path, dst_path)
            installed_files.append(dst_path)
    return installed_files
