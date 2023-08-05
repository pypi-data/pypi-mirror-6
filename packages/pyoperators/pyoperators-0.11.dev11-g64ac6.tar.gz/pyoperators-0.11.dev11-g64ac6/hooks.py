"""
The version number is obtained from git tags, branch and commit identifier.
It has been designed for the following workflow:

- git checkout master
- modify, commit, commit
- set version 0.1 in setup.py -> 0.1.dev03
- modify, commit              -> 0.1.dev04
- git checkout -b v0.1        -> 0.1.dev04
- modify, commit              -> v0.1.dev01
- git tag 0.1                 -> 0.1
- modify... and commit        -> 0.1.post01
- git tag 0.1.1               -> 0.1.1
- git checkout master         -> 0.1.dev04 ok
- modify, commit              -> 0.1.dev05
- set version=0.2 in setup.py -> 0.2.dev02
- modify, commit              -> 0.2.dev03

"""
import os
import re
import sys
from numpy.distutils.command.build_ext import build_ext
from subprocess import call, Popen, PIPE
from distutils.core import Command
from distutils.command.sdist import sdist
from distutils.command.build import build

try:
    root = os.path.dirname(os.path.abspath(__file__))
except NameError:
    root = os.path.dirname(os.path.abspath(sys.argv[0]))
abbrev = 5


def get_version(name, default):
    version = get_version_git(default)
    if version != '':
        return version
    return get_version_init_file(name) or default


def get_version_git(default):
    def run(cmd, cwd=root):
        git = "git"
        if sys.platform == "win32":
            git = "git.cmd"
        process = Popen([git] + cmd, cwd=cwd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if stderr != '':
            raise RuntimeError(stderr)
        if process.returncode != 0:
            raise RuntimeError('Error code: {0}.'.format(process.returncode))
        return stdout.strip()

    def get_branches():
        return run(['for-each-ref', '--sort=-committerdate', 'refs/heads/v[0-9'
                    ']*', '--format=%(refname)']).split('\n')

    def get_branch_name():
        return run(['rev-parse', '--abbrev-ref', 'HEAD'])

    def get_description():
        try:
            description = run([
                'describe', '--tags', '--abbrev={0}'.format(abbrev)])
        except RuntimeError:
            description = run([
                'describe', '--tags', '--abbrev={0}'.format(abbrev),
                '--always']).split('-')
            return '', '', description[0], '-' + description[1]
        regex = r"""^
        (?P<tag>.*?)
        (?:-
            (?P<rev>\d+)
            (?P<commit>-g[0-9a-f]{5,40})
        )?
        $"""
        m = re.match(regex, description, re.VERBOSE)
        return (m.group(_) for _ in 'tag,rev,commit'.split(','))

    def get_dirty():
#        try:
#            run(['diff-index', '--quiet', 'HEAD'])
        run(['diff-index', 'HEAD'])
#        except RuntimeError:
#            return '-dirty'
        return ''

    def get_master_rev(default):
        branches = get_branches()
        for branch in branches:
            id = re.match('^refs/heads/v(.*)$', branch).group(1)
            if id == default:
                continue
            common = run(['merge-base', 'HEAD', branch])
            rev = int(run(['rev-list', '--count', 'HEAD', '^' + common]))
            if rev > 0:
                return common, rev
        return run(['rev-list', '--count', 'HEAD'])

    try:
        run(['rev-parse', '--is-inside-work-tree'])
    except (OSError, RuntimeError):
        return ''

    branch = get_branch_name()
    dirty = get_dirty()

    if branch == 'master':
        try:
            return run(['describe', '--tags', '--candidates=0']) + dirty
        except RuntimeError:
            pass
        commit, rev = get_master_rev(default)
        if default != '':
            return '{0}.dev{1:02}-g{2}{3}'.format(default, rev,
                                                  commit[:abbrev], dirty)
        return str(rev) + dirty

    isrelease = re.match('^v[0-9.]+$', branch) is not None
    tag, rev, commit = get_description()
    if isrelease:
        version = tag
    else:
        version = branch
    if rev is not None:
        version += '.post' if isrelease else '.dev'
        version += '{0:02}'.format(int(rev)) + commit
    return version + dirty


def get_version_init_file(name):
    try:
        f = open(os.path.join(name, '__init__.py')).read()
    except IOError:
        return ''
    m = re.search(r"__version__ = '(.*)'", f)
    if m is None:
        return ''
    return m.groups()[0]


def write_version(name, version):
    try:
        init = open(os.path.join(root, name, '__init__.py.in')).readlines()
    except IOError:
        return
    init += ['\n', '__version__ = ' + repr(version) + '\n']
    open(os.path.join(root, name, '__init__.py'), 'w').writelines(init)


class BuildCommand(build):
    def run(self):
        write_version(self.distribution.get_name(),
                      self.distribution.get_version())
        build.run(self)


class SDistCommand(sdist):
    def make_release_tree(self, base_dir, files):
        write_version(self.distribution.get_name(),
                      self.distribution.get_version())
        sdist.make_release_tree(self, base_dir, files)


class CoverageCommand(Command):
    description = "run the package coverage"
    user_options = [('file=', 'f', 'restrict coverage to a specific file')]

    def run(self):
        call(['nosetests', '--with-coverage', '--cover-package',
              'pyoperators', self.file])
        call(['coverage', 'html'])

    def initialize_options(self):
        self.file = 'test'

    def finalize_options(self):
        pass


class TestCommand(Command):
    description = "run the test suite"
    user_options = [('file=', 'f', 'restrict test to a specific file')]

    def run(self):
        call(['nosetests', self.file])

    def initialize_options(self):
        self.file = 'test'

    def finalize_options(self):
        pass


def get_cmdclass():
    return {'build': BuildCommand,
            'build_ext': build_ext,
            'coverage': CoverageCommand,
            'sdist': SDistCommand,
            'test': TestCommand}
