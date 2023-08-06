'''
create tasks for coverage.py


Add coverage related tasks to ``dodo.py``::

    from doitpy.coverage import Coverage, PythonPackage

    def task_coverage():
        """show coverage for all modules including tests"""
        cov = Coverage([PythonPackage('my_pkg_name', 'tests')],
                       config=Config(branch=False, parallel=True,
                                     omit=['tests/no_cover.py'],)
                       )
        yield cov.all() # create task `coverage`
        yield cov.src() # create task `coverage_src`
        yield cov.by_module() # create tasks `coverage_module:<path/to/test>`


'''

import glob

from confclass import Config


def sep(*args):
    """join strings or list of strings ignoring None values"""
    return ' '.join(a for a in args if a)


class PythonPackage(object):
    """Contain list of modules of the package (does not handle sub-packages)

    :ivar list-str src: list of path of source modules
    :ivar list-str test: list of path of all modules from test folder
    :ivar list-str test_files: list of path of actual test modules
    """

    # TODO should track sub-packages

    #: :class:`confclass.Config`
    #:
    #: :var str test_prefix: string prefix on name of files
    #: :var str pkg_test_dir: path to location of test files
    config = Config(
        test_prefix = 'test_',
        pkg_test_dir = 'tests',
        )

    def __init__(self, path, test_path=None, config=None):
        """
        :param str/pathlib.Path path: dir path to package.
        :param str/pathlib.Path test_path: if test_path is not given assume
                it is on config.pkg_test_dir inside source package.
        """
        self.config = self.config.make(config)
        self.test_prefix = self.config['test_prefix']

        self.src_base = str(path) if path else ''
        if test_path is None:
            self.test_base = '{}/{}'.format(self.src_base,
                                            self.config['pkg_test_dir'])
        else:
            self.test_base = str(test_path)
        self.src = glob.glob("{}/*.py".format(self.src_base))
        self.test = glob.glob("{}/*.py".format(self.test_base))
        self.test_files = glob.glob("{}/{}*.py".format(
                self.test_base, self.test_prefix))

    def all_modules(self):
        """Yield all source and test modules."""
        for mod in self.src + self.test:
            yield mod


class Coverage(object):
    """generate tasks for coverage.py"""

    #: :class:`confclass.Config`
    #:
    #: :var string cmd_run_test: shell command used to run tests
    #: :var branch bool: measure branche coverage
    #: :var parallel bool: measure using `--parallel-mode` (needed for
    #:              subprocess and multiprocess coverage
    #: :var list-str omit: list of paths to omit from coverage
    config = Config(
        cmd_run_test = "`which py.test`",
        branch=True,
        parallel=False,
        omit=[])

    def __init__(self, pkgs, config=None):
        """
        :param list-str/PythonPackage pkgs: packages to measure coverage
        """
        self.config = self.config.make(config)
        self.pkgs = []
        for pkg in pkgs:
            if isinstance(pkg, PythonPackage):
                self.pkgs.append(pkg)
            else:
                self.pkgs.append(PythonPackage(pkg))


    def _action_list(self, modules, test=None):
        """return list of actions to be used in a doit task"""
        run_options = []
        if self.config['branch']:
            run_options.append('--branch')
        if self.config['parallel']:
            run_options.append('--parallel-mode')

        report_options = []
        if self.config['omit']:
            omit_list = ','.join(self.config['omit'])
            report_options.append('--omit {}'.format(omit_list))

        actions = [sep("coverage run", sep(*run_options),
                       self.config['cmd_run_test'], test)]
        if self.config['parallel']:
            actions.append('coverage combine')
        actions.append(sep("coverage report --show-missing",
                           sep(*report_options), sep(*modules)))
        return actions


    def all(self, basename='coverage'):
        """show coverage for all modules including tests"""
        all_modules = []

        for pkg in self.pkgs:
            for module in pkg.all_modules():
                all_modules.append(module)

        yield {
            'basename': basename,
            'actions': self._action_list(all_modules),
            'verbosity': 2,
            }


    def src(self, basename='coverage_src'):
        """show coverage for all modules (exclude tests)"""
        all_modules = []

        for pkg in self.pkgs:
            for module in pkg.src:
                all_modules.append(module)

        yield {
            'basename': basename,
            'actions': self._action_list(all_modules),
            'verbosity': 2,
            }


    def by_module(self, basename='coverage_module'):
        """show coverage for individual modules"""
        for pkg in self.pkgs:
            to_strip = len('{}/{}'.format(pkg.test_base, pkg.test_prefix))
            tests = glob.glob('{}/{}*.py'.format(pkg.test_base,
                                                 pkg.test_prefix))
            for test in tests:
                source = pkg.src_base + '/' + test[to_strip:]
                yield {
                    'basename': basename,
                    'name': test,
                    'actions': self._action_list([source, test], test),
                    'verbosity': 2,
                    }

