#! /usr/bin/python

"""versioneer.py

(like a rocketeer, but for versions)

* https://github.com/warner/python-versioneer
* Brian Warner
* License: Public Domain
* Version: 0.8+

This file helps distutils-based projects manage their version number by just
creating version-control tags.

For developers who work from a VCS-generated tree (e.g. 'git clone' etc),
each 'setup.py version', 'setup.py build', 'setup.py sdist' will compute a
version number by asking your version-control tool about the current
checkout. The version number will be written into a generated _version.py
file of your choosing, where it can be included by your __init__.py

For users who work from a VCS-generated tarball (e.g. 'git archive'), it will
compute a version number by looking at the name of the directory created when
te tarball is unpacked. This conventionally includes both the name of the
project and a version number.

For users who work from a tarball built by 'setup.py sdist', it will get a
version number from a previously-generated _version.py file.

As a result, loading code directly from the source tree will not result in a
real version. If you want real versions from VCS trees (where you frequently
update from the upstream repository, or do new development), you will need to
do a 'setup.py version' after each update, and load code from the build/
directory.

You need to provide this code with a few configuration values:

 versionfile_source:
    A project-relative pathname into which the generated version strings
    should be written. This is usually a _version.py next to your project's
    main __init__.py file. If your project uses src/myproject/__init__.py,
    this should be 'src/myproject/_version.py'. This file should be checked
    in to your VCS as usual: the copy created below by 'setup.py
    update_files' will include code that parses expanded VCS keywords in
    generated tarballs. The 'build' and 'sdist' commands will replace it with
    a copy that has just the calculated version string.

 versionfile_build:
    Like versionfile_source, but relative to the build directory instead of
    the source directory. These will differ when your setup.py uses
    'package_dir='. If you have package_dir={'myproject': 'src/myproject'},
    then you will probably have versionfile_build='myproject/_version.py' and
    versionfile_source='src/myproject/_version.py'.

 tag_prefix: a string, like 'PROJECTNAME-', which appears at the start of all
             VCS tags. If your tags look like 'myproject-1.2.0', then you
             should use tag_prefix='myproject-'. If you use unprefixed tags
             like '1.2.0', this should be an empty string.

 parentdir_prefix: a string, frequently the same as tag_prefix, which
                   appears at the start of all unpacked tarball filenames. If
                   your tarball unpacks into 'myproject-1.2.0', this should
                   be 'myproject-'.

To use it:

 1: include this file in the top level of your project
 2: make the following changes to the top of your setup.py:
     import versioneer
     versioneer.versionfile_source = 'src/myproject/_version.py'
     versioneer.versionfile_build = 'myproject/_version.py'
     versioneer.tag_prefix = '' # tags are like 1.2.0
     versioneer.parentdir_prefix = 'myproject-' # dirname like 'myproject-1.2.0'
 3: add the following arguments to the setup() call in your setup.py:
     version=versioneer.get_version(),
     cmdclass=versioneer.get_cmdclass(),
 4: run 'setup.py update_files', which will create _version.py, and will
    modify your __init__.py to define __version__ (by calling a function
    from _version.py)
 5: modify your MANIFEST.in to include versioneer.py
 6: add both versioneer.py and the generated _version.py to your VCS
"""

import os, sys, re
from distutils.core import Command
from distutils.command.sdist import sdist as _sdist
from distutils.command.build import build as _build

versionfile_source = None
versionfile_build = None
tag_prefix = None
parentdir_prefix = None

VCS = "git"


LONG_VERSION_PY = '''
# This file helps to compute a version number in source trees obtained from
# git-archive tarball (such as those provided by githubs download-from-tag
# feature). Distribution tarballs (build by setup.py sdist) and build
# directories (produced by setup.py build) will contain a much shorter file
# that just contains the computed version number.

# This file is released into the public domain. Generated by
# versioneer-0.8+ (https://github.com/warner/python-versioneer)

# these strings will be replaced by git during git-archive
git_refnames = "%(DOLLAR)sFormat:%%d%(DOLLAR)s"
git_full = "%(DOLLAR)sFormat:%%H%(DOLLAR)s"


import subprocess
import sys

def run_command(args, cwd=None, verbose=False, hide_stderr=False):
    try:
        # remember shell=False, so use git.cmd on windows, not just git
        p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE,
                             stderr=(subprocess.PIPE if hide_stderr else None))
    except EnvironmentError:
        e = sys.exc_info()[1]
        if verbose:
            print("unable to run %%s" %% args[0])
            print(e)
        return None
    stdout = p.communicate()[0].strip()
    if sys.version >= '3':
        stdout = stdout.decode()
    if p.returncode != 0:
        if verbose:
            print("unable to run %%s (error)" %% args[0])
        return None
    return stdout


import sys
import re
import os.path

def get_expanded_variables(versionfile_abs):
    # the code embedded in _version.py can just fetch the value of these
    # variables. When used from setup.py, we don't want to import
    # _version.py, so we do it with a regexp instead. This function is not
    # used from _version.py.
    variables = {}
    try:
        f = open(versionfile_abs,"r")
        for line in f.readlines():
            if line.strip().startswith("git_refnames ="):
                mo = re.search(r'=\s*"(.*)"', line)
                if mo:
                    variables["refnames"] = mo.group(1)
            if line.strip().startswith("git_full ="):
                mo = re.search(r'=\s*"(.*)"', line)
                if mo:
                    variables["full"] = mo.group(1)
        f.close()
    except EnvironmentError:
        pass
    return variables

def versions_from_expanded_variables(variables, tag_prefix, verbose=False):
    refnames = variables["refnames"].strip()
    if refnames.startswith("$Format"):
        if verbose:
            print("variables are unexpanded, not using")
        return {} # unexpanded, so not in an unpacked git-archive tarball
    refs = set([r.strip() for r in refnames.strip("()").split(",")])
    # starting in git-1.8.3, tags are listed as "tag: foo-1.0" instead of
    # just "foo-1.0". If we see a "tag: " prefix, prefer those.
    TAG = "tag: "
    tags = set([r[len(TAG):] for r in refs if r.startswith(TAG)])
    if not tags:
        # Either we're using git < 1.8.3, or there really are no tags. We use
        # a heuristic: assume all version tags have a digit. The old git %%d
        # expansion behaves like git log --decorate=short and strips out the
        # refs/heads/ and refs/tags/ prefixes that would let us distinguish
        # between branches and tags. By ignoring refnames without digits, we
        # filter out many common branch names like "release" and
        # "stabilization", as well as "HEAD" and "master".
        tags = set([r for r in refs if re.search(r'\d', r)])
        if verbose:
            print("discarding '%%s', no digits" %% ",".join(refs-tags))
    if verbose:
        print("likely tags: %%s" %% ",".join(sorted(tags)))
    for ref in sorted(tags):
        # sorting will prefer e.g. "2.0" over "2.0rc1"
        if ref.startswith(tag_prefix):
            r = ref[len(tag_prefix):]
            if verbose:
                print("picking %%s" %% r)
            return { "version": r,
                     "full": variables["full"].strip() }
    # no suitable tags, so we use the full revision id
    if verbose:
        print("no suitable tags, using full revision id")
    return { "version": variables["full"].strip(),
             "full": variables["full"].strip() }

def versions_from_vcs(tag_prefix, root, verbose=False):
    # this runs 'git' from the root of the source tree. This only gets called
    # if the git-archive 'subst' variables were *not* expanded, and
    # _version.py hasn't already been rewritten with a short version string,
    # meaning we're inside a checked out source tree.

    if not os.path.exists(os.path.join(root, ".git")):
        if verbose:
            print("no .git in %%s" %% root)
        return {}

    GIT = "git"
    if sys.platform == "win32":
        GIT = "git.cmd"
    stdout = run_command([GIT, "describe", "--tags", "--dirty", "--always"],
                         cwd=root)
    if stdout is None:
        return {}
    if not stdout.startswith(tag_prefix):
        if verbose:
            print("tag '%%s' doesn't start with prefix '%%s'" %% (stdout, tag_prefix))
        return {}
    tag = stdout[len(tag_prefix):]
    stdout = run_command([GIT, "rev-parse", "HEAD"], cwd=root)
    if stdout is None:
        return {}
    full = stdout.strip()
    if tag.endswith("-dirty"):
        full += "-dirty"
    return {"version": tag, "full": full}


def versions_from_parentdir(parentdir_prefix, root, verbose=False):
    # Source tarballs conventionally unpack into a directory that includes
    # both the project name and a version string.
    dirname = os.path.basename(root)
    if not dirname.startswith(parentdir_prefix):
        if verbose:
            print("guessing rootdir is '%%s', but '%%s' doesn't start with prefix '%%s'" %%
                  (root, dirname, parentdir_prefix))
        return None
    return {"version": dirname[len(parentdir_prefix):], "full": ""}

tag_prefix = "%(TAG_PREFIX)s"
parentdir_prefix = "%(PARENTDIR_PREFIX)s"
versionfile_source = "%(VERSIONFILE_SOURCE)s"

def get_versions(default={"version": "unknown", "full": ""}, verbose=False):
    # I am in _version.py, which lives at ROOT/VERSIONFILE_SOURCE. If we have
    # __file__, we can work backwards from there to the root. Some
    # py2exe/bbfreeze/non-CPython implementations don't do __file__, in which
    # case we can only use expanded variables.

    variables = { "refnames": git_refnames, "full": git_full }
    ver = versions_from_expanded_variables(variables, tag_prefix, verbose)
    if ver:
        return ver

    try:
        root = os.path.abspath(__file__)
        # versionfile_source is the relative path from the top of the source
        # tree (where the .git directory might live) to this file. Invert
        # this to find the root from __file__.
        for i in range(len(versionfile_source.split("/"))):
            root = os.path.dirname(root)
    except NameError:
        return default

    return (versions_from_vcs(tag_prefix, root, verbose)
            or versions_from_parentdir(parentdir_prefix, root, verbose)
            or default)

'''


import subprocess
import sys

def run_command(args, cwd=None, verbose=False, hide_stderr=False):
    try:
        # remember shell=False, so use git.cmd on windows, not just git
        p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE,
                             stderr=(subprocess.PIPE if hide_stderr else None))
    except EnvironmentError:
        e = sys.exc_info()[1]
        if verbose:
            print("unable to run %s" % args[0])
            print(e)
        return None
    stdout = p.communicate()[0].strip()
    if sys.version >= '3':
        stdout = stdout.decode()
    if p.returncode != 0:
        if verbose:
            print("unable to run %s (error)" % args[0])
        return None
    return stdout


import sys
import re
import os.path

def get_expanded_variables(versionfile_abs):
    # the code embedded in _version.py can just fetch the value of these
    # variables. When used from setup.py, we don't want to import
    # _version.py, so we do it with a regexp instead. This function is not
    # used from _version.py.
    variables = {}
    try:
        f = open(versionfile_abs,"r")
        for line in f.readlines():
            if line.strip().startswith("git_refnames ="):
                mo = re.search(r'=\s*"(.*)"', line)
                if mo:
                    variables["refnames"] = mo.group(1)
            if line.strip().startswith("git_full ="):
                mo = re.search(r'=\s*"(.*)"', line)
                if mo:
                    variables["full"] = mo.group(1)
        f.close()
    except EnvironmentError:
        pass
    return variables

def versions_from_expanded_variables(variables, tag_prefix, verbose=False):
    refnames = variables["refnames"].strip()
    if refnames.startswith("$Format"):
        if verbose:
            print("variables are unexpanded, not using")
        return {} # unexpanded, so not in an unpacked git-archive tarball
    refs = set([r.strip() for r in refnames.strip("()").split(",")])
    # starting in git-1.8.3, tags are listed as "tag: foo-1.0" instead of
    # just "foo-1.0". If we see a "tag: " prefix, prefer those.
    TAG = "tag: "
    tags = set([r[len(TAG):] for r in refs if r.startswith(TAG)])
    if not tags:
        # Either we're using git < 1.8.3, or there really are no tags. We use
        # a heuristic: assume all version tags have a digit. The old git %d
        # expansion behaves like git log --decorate=short and strips out the
        # refs/heads/ and refs/tags/ prefixes that would let us distinguish
        # between branches and tags. By ignoring refnames without digits, we
        # filter out many common branch names like "release" and
        # "stabilization", as well as "HEAD" and "master".
        tags = set([r for r in refs if re.search(r'\d', r)])
        if verbose:
            print("discarding '%s', no digits" % ",".join(refs-tags))
    if verbose:
        print("likely tags: %s" % ",".join(sorted(tags)))
    for ref in sorted(tags):
        # sorting will prefer e.g. "2.0" over "2.0rc1"
        if ref.startswith(tag_prefix):
            r = ref[len(tag_prefix):]
            if verbose:
                print("picking %s" % r)
            return { "version": r,
                     "full": variables["full"].strip() }
    # no suitable tags, so we use the full revision id
    if verbose:
        print("no suitable tags, using full revision id")
    return { "version": variables["full"].strip(),
             "full": variables["full"].strip() }

def versions_from_vcs(tag_prefix, root, verbose=False):
    # this runs 'git' from the root of the source tree. This only gets called
    # if the git-archive 'subst' variables were *not* expanded, and
    # _version.py hasn't already been rewritten with a short version string,
    # meaning we're inside a checked out source tree.

    if not os.path.exists(os.path.join(root, ".git")):
        if verbose:
            print("no .git in %s" % root)
        return {}

    GIT = "git"
    if sys.platform == "win32":
        GIT = "git.cmd"
    stdout = run_command([GIT, "describe", "--tags", "--dirty", "--always"],
                         cwd=root)
    if stdout is None:
        return {}
    if not stdout.startswith(tag_prefix):
        if verbose:
            print("tag '%s' doesn't start with prefix '%s'" % (stdout, tag_prefix))
        return {}
    tag = stdout[len(tag_prefix):]
    stdout = run_command([GIT, "rev-parse", "HEAD"], cwd=root)
    if stdout is None:
        return {}
    full = stdout.strip()
    if tag.endswith("-dirty"):
        full += "-dirty"
    return {"version": tag, "full": full}


def versions_from_parentdir(parentdir_prefix, root, verbose=False):
    # Source tarballs conventionally unpack into a directory that includes
    # both the project name and a version string.
    dirname = os.path.basename(root)
    if not dirname.startswith(parentdir_prefix):
        if verbose:
            print("guessing rootdir is '%s', but '%s' doesn't start with prefix '%s'" %
                  (root, dirname, parentdir_prefix))
        return None
    return {"version": dirname[len(parentdir_prefix):], "full": ""}
import os.path
import sys

# os.path.relpath only appeared in Python-2.6 . Define it here for 2.5.
def os_path_relpath(path, start=os.path.curdir):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")

    start_list = [x for x in os.path.abspath(start).split(os.path.sep) if x]
    path_list = [x for x in os.path.abspath(path).split(os.path.sep) if x]

    # Work out how much of the filepath is shared by start and path.
    i = len(os.path.commonprefix([start_list, path_list]))

    rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return os.path.curdir
    return os.path.join(*rel_list)

def do_vcs_install(versionfile_source, ipy):
    GIT = "git"
    if sys.platform == "win32":
        GIT = "git.cmd"
    files = [versionfile_source, ipy]
    try:
        me = __file__
        if me.endswith(".pyc") or me.endswith(".pyo"):
            me = os.path.splitext(me)[0] + ".py"
        versioneer_file = os_path_relpath(me)
    except NameError:
        versioneer_file = "versioneer.py"
    files.append(versioneer_file)
    present = False
    try:
        f = open(".gitattributes", "r")
        for line in f.readlines():
            if line.strip().startswith(versionfile_source):
                if "export-subst" in line.strip().split()[1:]:
                    present = True
        f.close()
    except EnvironmentError:
        pass    
    if not present:
        f = open(".gitattributes", "a+")
        f.write("%s export-subst\n" % versionfile_source)
        f.close()
        files.append(".gitattributes")
    run_command([GIT, "add", "--"] + files)

SHORT_VERSION_PY = """
# This file was generated by 'versioneer.py' (0.8+) from
# revision-control system data, or from the parent directory name of an
# unpacked source archive. Distribution tarballs contain a pre-generated copy
# of this file.

version_version = '%(version)s'
version_full = '%(full)s'
def get_versions(default={}, verbose=False):
    return {'version': version_version, 'full': version_full}

"""

DEFAULT = {"version": "unknown", "full": "unknown"}

def versions_from_file(filename):
    versions = {}
    try:
        f = open(filename)
    except EnvironmentError:
        return versions
    for line in f.readlines():
        mo = re.match("version_version = '([^']+)'", line)
        if mo:
            versions["version"] = mo.group(1)
        mo = re.match("version_full = '([^']+)'", line)
        if mo:
            versions["full"] = mo.group(1)
    f.close()
    return versions

def write_to_version_file(filename, versions):
    f = open(filename, "w")
    f.write(SHORT_VERSION_PY % versions)
    f.close()
    print("set %s to '%s'" % (filename, versions["version"]))


def get_versions(default=DEFAULT, verbose=False):
    # returns dict with two keys: 'version' and 'full'
    assert versionfile_source is not None, "please set versioneer.versionfile_source"
    assert tag_prefix is not None, "please set versioneer.tag_prefix"
    assert parentdir_prefix is not None, "please set versioneer.parentdir_prefix"
    # I am in versioneer.py, which must live at the top of the source tree,
    # which we use to compute the root directory. py2exe/bbfreeze/non-CPython
    # don't have __file__, in which case we fall back to sys.argv[0] (which
    # ought to be the setup.py script). We prefer __file__ since that's more
    # robust in cases where setup.py was invoked in some weird way (e.g. pip)
    try:
        root = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        root = os.path.dirname(os.path.abspath(sys.argv[0]))
    versionfile_abs = os.path.join(root, versionfile_source)

    # extract version from first of _version.py, 'git describe', parentdir.
    # This is meant to work for developers using a source checkout, for users
    # of a tarball created by 'setup.py sdist', and for users of a
    # tarball/zipball created by 'git archive' or github's download-from-tag
    # feature.

    variables = get_expanded_variables(versionfile_abs)
    if variables:
        ver = versions_from_expanded_variables(variables, tag_prefix)
        if ver:
            if verbose: print("got version from expanded variable %s" % ver)
            return ver

    ver = versions_from_file(versionfile_abs)
    if ver:
        if verbose: print("got version from file %s %s" % (versionfile_abs,ver))
        return ver

    ver = versions_from_vcs(tag_prefix, root, verbose)
    if ver:
        if verbose: print("got version from git %s" % ver)
        return ver

    ver = versions_from_parentdir(parentdir_prefix, root, verbose)
    if ver:
        if verbose: print("got version from parentdir %s" % ver)
        return ver

    if verbose: print("got version from default %s" % ver)
    return default

def get_version(verbose=False):
    return get_versions(verbose=verbose)["version"]

class cmd_version(Command):
    description = "report generated version string"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        ver = get_version(verbose=True)
        print("Version is currently: %s" % ver)


class cmd_build(_build):
    def run(self):
        versions = get_versions(verbose=True)
        _build.run(self)
        # now locate _version.py in the new build/ directory and replace it
        # with an updated value
        target_versionfile = os.path.join(self.build_lib, versionfile_build)
        print("UPDATING %s" % target_versionfile)
        os.unlink(target_versionfile)
        f = open(target_versionfile, "w")
        f.write(SHORT_VERSION_PY % versions)
        f.close()

class cmd_sdist(_sdist):
    def run(self):
        versions = get_versions(verbose=True)
        self._versioneer_generated_versions = versions
        # unless we update this, the command will keep using the old version
        self.distribution.metadata.version = versions["version"]
        return _sdist.run(self)

    def make_release_tree(self, base_dir, files):
        _sdist.make_release_tree(self, base_dir, files)
        # now locate _version.py in the new base_dir directory (remembering
        # that it may be a hardlink) and replace it with an updated value
        target_versionfile = os.path.join(base_dir, versionfile_source)
        print("UPDATING %s" % target_versionfile)
        os.unlink(target_versionfile)
        f = open(target_versionfile, "w")
        f.write(SHORT_VERSION_PY % self._versioneer_generated_versions)
        f.close()

INIT_PY_SNIPPET = """
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
"""

class cmd_update_files(Command):
    description = "modify __init__.py and create _version.py"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        ipy = os.path.join(os.path.dirname(versionfile_source), "__init__.py")
        print(" creating %s" % versionfile_source)
        f = open(versionfile_source, "w")
        f.write(LONG_VERSION_PY % {"DOLLAR": "$",
                                   "TAG_PREFIX": tag_prefix,
                                   "PARENTDIR_PREFIX": parentdir_prefix,
                                   "VERSIONFILE_SOURCE": versionfile_source,
                                   })
        f.close()
        try:
            old = open(ipy, "r").read()
        except EnvironmentError:
            old = ""
        if INIT_PY_SNIPPET not in old:
            print(" appending to %s" % ipy)
            f = open(ipy, "a")
            f.write(INIT_PY_SNIPPET)
            f.close()
        else:
            print(" %s unmodified" % ipy)
        do_vcs_install(versionfile_source, ipy)

def get_cmdclass():
    return {'version': cmd_version,
            'update_files': cmd_update_files,
            'build': cmd_build,
            'sdist': cmd_sdist,
            }
