import os
import subprocess
import sys

from .deps import APPIMAGETOOL, ensure_appimagetool
from .docker import docker_run
from .fs import copy_tree
from .log import debug, log
from .tmp import TemporaryDirectory


__all__ = ['build_appimage']


def build_appimage(appdir=None, destination=None):
    '''Build an AppImage from an AppDir
    '''
    if appdir is None:
        appdir = 'AppDir'

    log('BUILD', appdir)
    ensure_appimagetool()

    cmd = [APPIMAGETOOL, appdir]
    if destination is not None:
        cmd.append(destination)
    cmd = ' '.join(cmd)

    debug('SYSTEM', cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)
    stdout = []
    while True:
        out = p.stdout.readline()
        try:
            out = out.decode()
        except AttributeError:
            out = str(out)
        stdout.append(out)
        if out == '' and p.poll() is not None:
            break
        elif out:
            out = out.replace('%', '%%')[:-1]
            for line in out.split(os.linesep):
                if line.startswith('WARNING'):
                    log('WARNING', line[9:])
                elif line.startswith('Error'):
                    raise RuntimeError(line)
                else:
                    debug('APPIMAGE', line)
    rc = p.poll()
    if rc != 0:
        print(''.join(stdout))
        sys.stdout.flush()
        raise RuntimeError('Could not build AppImage')
