import contextlib
import io
import os
import subprocess
import sys

import six
from six.moves import xrange, input

try:
    import simplejson as json
except ImportError:
    import json


stdout = io.FileIO(sys.stdout.fileno(), "wb")
stderr = io.FileIO(sys.stderr.fileno(), "wb")


def run_proc(cmd, **kwargs):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, **kwargs)
    out = p.communicate()[0]
    return (p.returncode, out.strip())


def find_nearest(directory, search):
    directory = os.path.abspath(directory)
    parts = directory.split(os.path.sep)
    for idx in xrange(len(parts)):
        d = os.path.sep.join(parts[:-idx])
        if not d:
            d = os.path.sep.join(parts)
        s = os.path.join(d, search)
        if os.path.isdir(s) or os.path.isfile(s):
            return d
    raise OSError


def out(msg):
    if isinstance(msg, six.text_type):
        msg = msg.encode("utf-8")
    stdout.write(msg)
    stdout.flush()


def err(msg):
    if isinstance(msg, six.text_type):
        msg = msg.encode("utf-8")
    stderr.write(msg)
    stderr.flush()


def error(msg, exit=True):
    err("ERROR: {}".format(msg))
    if exit:
        sys.exit(1)


def warn(msg):
    err("WARNING: {}".format(msg))


def confirm(msg):
    answer = input("%s [y/n]: ")
    return answer == "y"


def api_error(e):
    data = e.read().decode("utf-8")
    try:
        data = json.loads(data)
    except ValueError:
        message = data
    else:
        message = data["message"]
    if "\n" in message:
        output = "\n\n{}".format(message)
    else:
        output = message
    out("API returned an error [{}]: {}\n".format(e.code, message))
    sys.exit(1)


class BadCommand(Exception):
    pass


def find_command(cmd, paths=None, pathext=None):
    """
    Searches the PATH for the given command and returns its path
    Pulled from pip
    """
    if paths is None:
        paths = os.environ.get("PATH", "").split(os.pathsep)
    if isinstance(paths, six.string_types):
        paths = [paths]
    # check if there are funny path extensions for executables, e.g. Windows
    if pathext is None:
        pathext = get_pathext()
    pathext = [ext for ext in pathext.lower().split(os.pathsep)]
    # don"t use extensions if the command ends with one of them
    if os.path.splitext(cmd)[1].lower() in pathext:
        pathext = [""]
    # check if we find the command on PATH
    for path in paths:
        # try without extension first
        cmd_path = os.path.join(path, cmd)
        for ext in pathext:
            # then including the extension
            cmd_path_ext = cmd_path + ext
            if os.path.isfile(cmd_path_ext):
                return cmd_path_ext
        if os.path.isfile(cmd_path):
            return cmd_path
    raise BadCommand("Cannot find command {!r}".format(cmd))


def get_pathext(default_pathext=None):
    """
    Returns the path extensions from environment or a default
    Pulled from pip
    """
    if default_pathext is None:
        default_pathext = os.pathsep.join([".COM", ".EXE", ".BAT", ".CMD"])
    pathext = os.environ.get("PATHEXT", default_pathext)
    return pathext


# from Python 2.7
def check_output(*popenargs, **kwargs):
    if "stdout" in kwargs:
        raise ValueError("stdout argument not allowed, it will be overridden.")
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd)
    return output


@contextlib.contextmanager
def stdin_buffer():
    import termios, tty
    if sys.stdin.isatty():
        before = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        try:
            yield
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, before)
    else:
        yield
