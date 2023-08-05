import unittest
import logging
from os import path
from sys import argv

import venusian
from soklog import init as log_init

from soktest.base import TestCase


class TestRunner(object):

    class _PrepereSpecyficTestCases(object):

        def __init__(self, suite, tests_names):
            self.suite = suite
            self.tests_names = tests_names

        def unpack_name(self, name):
            tab = name.split(':')
            if len(tab) < 2:
                tab.append(None)
            return tab

        def get_test_case(self, name):
            try:
                return TestCase._alltests_dict[name]
            except KeyError:
                names = '\n\t'.join(TestCase._alltests_dict.keys())
                raise RuntimeError(
                    'Bad test name: %s. Use one of:\n\t%s' % (name, names)
                )

        def validate_test_case(self, test_case, name):
            if test_case is None:
                filter_names = lambda test_name: test_name.endswith(
                    name) and test_name != name
                names = '\n\t'.join(filter(
                    filter_names, TestCase._alltests_dict.keys()))
                raise RuntimeError(
                    'Test name is ambiguous. Please provide full package name:\n\t%s' % (
                        names,)
                )

        def prepere_suite(self, test_case, method_name):
            if method_name is None:
                return self.suite.loadTestsFromTestCase(test_case)
            else:
                suite = unittest.TestSuite()
                case = test_case(method_name)
                suite.addTest(case)
                return suite

        def __call__(self):
            test_cases = []
            for name in self.tests_names:
                name, method_name = self.unpack_name(name)
                test_case = self.get_test_case(name)
                self.validate_test_case(test_case, name)
                test_cases.append(
                    self.prepere_suite(test_cases, method_name)
                )

            return test_cases

    def __init__(self, module, log_file_name='test.log', log_file_dir=''):
        self.module = module
        self.log_file_name = log_file_name
        self.log_file_dir = log_file_dir
        self.tests = []
        self.verbosity = None

    def import_tests(self):
        # we use venusian scanner for "import all tests"
        scanner = venusian.Scanner()
        scanner.scan(self.module, categories=('tests',))

    def prepere_all_test_cases(self, suite):
        test_cases = []
        for test_case in TestCase._alltests:
            test_cases.append(
                suite.loadTestsFromTestCase(test_case)
            )
        return test_cases

    def prepere_specyfic_test_cases(self, suite, tests_names):
        return self._PrepereSpecyficTestCases(suite, tests_names)()

    def get_log_filename(self):
        if path.exists(self.log_file_dir):
            return path.join(self.log_file_dir, self.log_file_name)
        else:
            return self.log_file_name

    def get_logger(self):
        return logging.getLogger(str(self.module))

    def start_logging(self):
        filename = self.get_log_filename()
        log_init(self.module, 'sok_test')

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)-15s:%(message)s",
            filename=filename,
        )
        self.get_logger().info('\n\t*** TESTING STARTED ***')

    def get_all_test_suite(self):
        self.start_logging()
        self.additional_preparation()
        self.import_tests()
        suite = unittest.TestLoader()

        if len(self.tests) == 0:
            return unittest.TestSuite(self.prepere_all_test_cases(suite))
        else:
            return unittest.TestSuite(self.prepere_specyfic_test_cases(suite, self.tests))

    def additional_preparation(self):
        pass

    def update_verbosity(self, verbosity=None):
        if verbosity is None:
            if len(self.tests) == 0:
                self.verbosity = 1
            else:
                self.verbosity = 2
        else:
            self.verbosity = verbosity

    def update_tests_from_argv(self):
        self.tests = argv[1:]

    def do_tests(self):
        self.update_tests_from_argv()
        self.update_verbosity()
        suite = self.get_all_test_suite()
        unittest.TextTestRunner(verbosity=self.verbosity).run(suite)
