# coding: utf-8
import subprocess
import sys
import os


if sys.version_info[0] == 2:
    PY3 = False
    text = unicode
    byte = str
else:
    PY3 = True
    text = str
    byte = bytes

strings = (text, byte)


def check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output


if not hasattr(subprocess, "check_output"):
    subprocess.check_output = check_output


def basename(name=None, noext=False):
    if not name:
        name = sys.argv[0]
    name = os.path.expanduser(name)
    name = os.path.abspath(name)
    name = os.path.basename(name)
    if noext:
        name = os.path.splitext(name)[0]
    return name
