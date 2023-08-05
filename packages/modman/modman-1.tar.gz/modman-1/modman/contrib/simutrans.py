import shutil
import os

from .. import util


def pak_addon(workspace, game_location, base_pak):
    filenames = os.listdir(workspace)
    pak_dir = os.path.join(workspace, base_pak)
    if base_pak not in filenames:
        os.mkdir(pak_dir)
    for name in filenames:
        shutil.move(os.path.join(workspace, name), pak_dir)
    return util.default_installer(workspace, game_location)
