# Postinstall script for Shiboken
#
# This file is based on pywin32_postinstall.py file from pywin32 project

import os, sys, traceback, shutil, fnmatch, stat
from os.path import dirname, abspath
from subprocess import Popen, PIPE
import re


try:
    # When this script is run from inside the bdist_wininst installer,
    # file_created() and directory_created() are additional builtin
    # functions which write lines to Python23\shiboken-install.log. This is
    # a list of actions for the uninstaller, the format is inspired by what
    # the Wise installer also creates.
    file_created
    is_bdist_wininst = True
except NameError:
    is_bdist_wininst = False # we know what it is not - but not what it is :)
    def file_created(file):
        pass

def install():
    if sys.platform == "win32":
        install_win32()
    else:
        install_posix()

def filter_match(name, patterns):
    for pattern in patterns:
        if pattern is None:
            continue
        if fnmatch.fnmatch(name, pattern):
            return True
    return False

def set_exec(name):
    mode = os.stat(name).st_mode
    new_mode = mode
    if new_mode & stat.S_IRUSR:
        new_mode = new_mode | stat.S_IXUSR
    if new_mode & stat.S_IRGRP:
        new_mode = new_mode | stat.S_IXGRP
    if new_mode & stat.S_IROTH:
        new_mode = new_mode | stat.S_IXOTH
    if (mode != new_mode):
        print("Setting exec for '%s' (mode %o => %o)" % (name, mode, new_mode))
        os.chmod(name, new_mode)


def back_tick(cmd, ret_err=False):
    """ Run command `cmd`, return stdout, or stdout, stderr if `ret_err`

    Roughly equivalent to ``check_output`` in Python 2.7

    Parameters
    ----------
    cmd : str
        command to execute
    ret_err : bool, optional
        If True, return stderr in addition to stdout.  If False, just return
        stdout

    Returns
    -------
    out : str or tuple
        If `ret_err` is False, return stripped string containing stdout from
        `cmd`.  If `ret_err` is True, return tuple of (stdout, stderr) where
        ``stdout`` is the stripped stdout, and ``stderr`` is the stripped
        stderr.

    Raises
    ------
    Raises RuntimeError if command returns non-zero exit code
    """
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = proc.communicate()
    if not isinstance(out, str):
        # python 3
        out = out.decode()
    retcode = proc.returncode
    if retcode is None:
        proc.terminate()
        raise RuntimeError(cmd + ' process did not terminate')
    if retcode != 0:
        raise RuntimeError(cmd + ' process returned code %d' % retcode)
    out = out.strip()
    if not ret_err:
        return out
    return out, err.strip()


OSX_OUTNAME_RE = re.compile(r'\(compatibility version [\d.]+, current version '
                        '[\d.]+\)')

def osx_get_install_names(libpath):
    """ Get OSX library install names from library `libpath` using ``otool``

    Parameters
    ----------
    libpath : str
        path to library

    Returns
    -------
    install_names : list of str
        install names in library `libpath`
    """
    out = back_tick('otool -L ' + libpath)
    libs = [line for line in out.split('\n')][1:]
    return [OSX_OUTNAME_RE.sub('', lib).strip() for lib in libs]


OSX_RPATH_RE = re.compile(r"path (.+) \(offset \d+\)")

def osx_get_rpaths(libpath):
    """ Get rpaths from library `libpath` using ``otool``

    Parameters
    ----------
    libpath : str
        path to library

    Returns
    -------
    rpaths : list of str
        rpath values stored in ``libpath``

    Notes
    -----
    See ``man dyld`` for more information on rpaths in libraries
    """
    lines = back_tick('otool -l ' + libpath).split('\n')
    ctr = 0
    rpaths = []
    while ctr < len(lines):
        line = lines[ctr].strip()
        if line != 'cmd LC_RPATH':
            ctr += 1
            continue
        assert lines[ctr + 1].strip().startswith('cmdsize')
        rpath_line = lines[ctr + 2].strip()
        match = OSX_RPATH_RE.match(rpath_line)
        if match is None:
            raise RuntimeError('Unexpected path line: ' + rpath_line)
        rpaths.append(match.groups()[0])
        ctr += 3
    return rpaths


def localize_libpaths(libpath, local_libs, enc_path=None):
    """ Set rpaths and install names to load local dynamic libs at run time

    Use ``install_name_tool`` to set relative install names in `libpath` (as
    named in `local_libs` to be relative to `enc_path`.  The default for
    `enc_path` is the directory containing `libpath`.

    Parameters
    ----------
    libpath : str
        path to library for which to set install names and rpaths
    local_libs : sequence of str
        library (install) names that should be considered relative paths
    enc_path : str, optional
        path that does or will contain the `libpath` library, and to which the
        `local_libs` are relative.  Defaults to current directory containing
        `libpath`.
    """
    if enc_path is None:
        enc_path = abspath(dirname(libpath))
    install_names = osx_get_install_names(libpath)
    need_rpath = False
    for install_name in install_names:
        if install_name[0] in '/@':
            continue
        back_tick('install_name_tool -change %s @rpath/%s %s' %
           (install_name, install_name, libpath))
        need_rpath = True
    if need_rpath and enc_path not in osx_get_rpaths(libpath):
        back_tick('install_name_tool -add_rpath %s %s' %
           (enc_path, libpath))


def install_posix():
    # Try to find Shiboken package
    try:
        import Shiboken
    except ImportError:
        print("The Shiboken package not found: %s" % traceback.print_exception(*sys.exc_info()))
        return
    shiboken_path = os.path.abspath(os.path.dirname(Shiboken.__file__))
    print("Shiboken package found in %s..." % shiboken_path)

    executables = ['shiboken']
    if sys.platform.startswith('linux'):
        executables.append('patchelf')
        patchelf_path = os.path.join(shiboken_path, "patchelf")
        from distutils.spawn import spawn

        def rpath_cmd(shiboken_path, srcpath):
            cmd = [patchelf_path, '--set-rpath', shiboken_path, srcpath]
            spawn(cmd, search_path=False, verbose=1)

        shiboken_libs = [lib for lib in os.listdir(shiboken_path) if filter_match(
                       lib, ["shiboken.so", "shiboken"])]
    elif sys.platform == 'darwin':
        shiboken_libs = [lib for lib in os.listdir(shiboken_path) if filter_match(
                       lib, ["*.so", "*.dylib", "shiboken"])]

        def rpath_cmd(shiboken_path, srcpath):
            localize_libpaths(srcpath, shiboken_libs, shiboken_path)

    else:
        raise RuntimeError('Not configured for platform ' +
                           sys.platform)

    # Set exec mode on executables
    for executable in executables:
        execpath = os.path.join(shiboken_path, executable)
        set_exec(execpath)

    # Update rpath in Shiboken libs
    for srcname in shiboken_libs:
        if os.path.isdir(srcname):
            continue
        srcpath = os.path.join(shiboken_path, srcname)
        rpath_cmd(shiboken_path, srcpath)
        print("Patched rpath in %s to %s." % (srcpath, shiboken_path))

    # Check Shiboken installation status
    try:
        from Shiboken import shiboken
        print("Shiboken package successfully installed in %s..." % \
            os.path.abspath(os.path.dirname(shiboken.__file__)))
    except ImportError:
        print("The Shiboken package not installed: %s" % traceback.print_exception(*sys.exc_info()))


def install_win32():
    # Try to find Shiboken package
    try:
        from Shiboken import shiboken
    except ImportError:
        print("The Shiboken package not found: %s" % traceback.print_exception(*sys.exc_info()))
        return
    shiboken_path = os.path.dirname(shiboken.__file__)
    shiboken_path = shiboken_path.replace("\\", "/")
    shiboken_path = shiboken_path.replace("lib/site-packages", "Lib/site-packages")
    # There is no need to run post install procedure on win32, only print info
    print("Shiboken package found in %s..." % shiboken_path)

def uninstall():
    print("The Shiboken extensions were successfully uninstalled.")

def usage():
    msg = \
"""%s: A post-install script for the Shiboken extensions.
    
This should be run automatically after installation, but if it fails you
can run it again with a '-install' parameter, to ensure the environment
is setup correctly.
"""
    print(msg.strip() % os.path.basename(sys.argv[0]))

# NOTE: If this script is run from inside the bdist_wininst created
# binary installer or uninstaller, the command line args are either
# '-install' or '-remove'.

# Important: From inside the binary installer this script MUST NOT
# call sys.exit() or raise SystemExit, otherwise not only this script
# but also the installer will terminate! (Is there a way to prevent
# this from the bdist_wininst C code?)

if __name__ == '__main__':
    if len(sys.argv)==1:
        usage()
        sys.exit(1)

    arg_index = 1
    while arg_index < len(sys.argv):
        arg = sys.argv[arg_index]
        if arg == "-install":
            install()
        elif arg == "-remove":
            # bdist_msi calls us before uninstall, so we can undo what we
            # previously did.  Sadly, bdist_wininst calls us *after*, so
            # we can't do much at all.
            if not is_bdist_wininst:
                uninstall()
        else:
            print("Unknown option: %s" % arg)
            usage()
            sys.exit(0)
        arg_index += 1
