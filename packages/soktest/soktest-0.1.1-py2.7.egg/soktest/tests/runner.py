import sys
import unittest
from mock import patch, MagicMock

from soktest.runner import TestRunner
from soktest.tests.base import TestOrganizer
from soktest.base import TestCase


class RunnerTests(TestOrganizer):

    class __init__(unittest.TestCase):

        def test_normal(self):
            runner = TestRunner('module', 'test2.log', 'dir')
            self.assertEqual('module', runner.module)
            self.assertEqual('test2.log', runner.log_file_name)
            self.assertEqual('dir', runner.log_file_dir)
            self.assertEqual([], runner.tests)
            self.assertEqual(None, runner.verbosity)

        def test_default(self):
            runner = TestRunner('module2')
            self.assertEqual('module2', runner.module)
            self.assertEqual('test.log', runner.log_file_name)
            self.assertEqual('', runner.log_file_dir)
            self.assertEqual([], runner.tests)
            self.assertEqual(None, runner.verbosity)

    class import_tests(unittest.TestCase):

        @patch('soktest.runner.venusian.Scanner')
        def test_default(self, ScannerMock):
            runner = TestRunner('module3')
            runner.import_tests()

            ScannerMock.assert_called_once_with()
            scanner = ScannerMock.return_value
            scanner.scan('module3', categories=('tests',))

    class prepere_all_test_cases(unittest.TestCase):

        @patch.object(TestCase, '_alltests', [])
        def test_default(self):
            test = MagicMock()
            runner = TestRunner('module')
            suite = MagicMock()
            TestCase._alltests.append(test)

            result = runner.prepere_all_test_cases(suite)

            suite.loadTestsFromTestCase.assert_called_once_with(test)
            self.assertEqual([suite.loadTestsFromTestCase(), ], result)

    class update_verbosity(unittest.TestCase):

        def test_default(self):
            runner = TestRunner('module')
            runner.update_verbosity()
            self.assertEqual(1, runner.verbosity)

        def test_default_with_tests(self):
            runner = TestRunner('module')
            runner.tests = [1, ]
            runner.update_verbosity()
            self.assertEqual(2, runner.verbosity)

        def test_with_value(self):
            runner = TestRunner('module')
            runner.update_verbosity(3)
            self.assertEqual(3, runner.verbosity)

    class update_tests_from_argv(unittest.TestCase):

        def test_default(self):
            with patch('soktest.runner.argv', []) as argv_mock:
                argv_mock.append(1)
                argv_mock.append(2)
                argv_mock.append(3)

                runner = TestRunner('module')
                runner.update_tests_from_argv()
                self.assertEqual([2, 3], runner.tests)

    class do_tests(unittest.TestCase):

        @patch('soktest.runner.unittest.TextTestRunner')
        def test_default(self, TextTestRunnerMock):
            runner = TestRunner('module')
            with patch.object(runner, 'get_all_test_suite') as get_all_test_suite:
                runner.do_tests()

                get_all_test_suite.assert_called_once_with()
                self.assertEqual(sys.argv[1:], runner.tests)
                self.assertTrue(runner.verbosity in [1, 2])
                TextTestRunnerMock.assert_called_once_with(
                    verbosity=runner.verbosity)
                TextTestRunnerMock().run.assert_called_once_with(
                    get_all_test_suite())

    class additional_preparation(unittest.TestCase):

        def test_default(self):
            runner = TestRunner('module')
            self.assertEqual(None, runner.additional_preparation())

    class get_all_test_suite(unittest.TestCase):

        @patch('soktest.runner.unittest')
        def test_without_tests(self, unittest_mock):
            runner = TestRunner('module')
            with patch.object(runner, 'start_logging') as start_logging_mock:
                with patch.object(runner, 'import_tests') as import_tests_mock:
                    with patch.object(runner, 'prepere_all_test_cases') as prepere_all_test_cases_mock:
                        with patch.object(runner, 'prepere_specyfic_test_cases') as prepere_specyfic_test_cases_mock:

                            runner.get_all_test_suite()

                            start_logging_mock.assert_called_once_with()
                            import_tests_mock.assert_called_once_with()

                            unittest_mock.TestLoader.assert_called_once_with()
                            prepere_all_test_cases_mock.assert_called_once_with(
                                unittest_mock.TestLoader())
                            self.assertEqual(
                                0, prepere_specyfic_test_cases_mock.call_count)

        @patch('soktest.runner.unittest')
        def test_with_tests(self, unittest_mock):
            runner = TestRunner('module')
            runner.tests = [1]
            with patch.object(runner, 'start_logging') as start_logging_mock:
                with patch.object(runner, 'import_tests') as import_tests_mock:
                    with patch.object(runner, 'prepere_all_test_cases') as prepere_all_test_cases_mock:
                        with patch.object(runner, 'prepere_specyfic_test_cases') as prepere_specyfic_test_cases_mock:

                            runner.get_all_test_suite()

                            start_logging_mock.assert_called_once_with()
                            import_tests_mock.assert_called_once_with()

                            unittest_mock.TestLoader.assert_called_once_with()
                            prepere_specyfic_test_cases_mock.assert_called_once_with(
                                unittest_mock.TestLoader(), [1])
                            self.assertEqual(
                                0, prepere_all_test_cases_mock.call_count)

    class get_logger(unittest.TestCase):

        @patch('soktest.runner.logging')
        def test_default(self, loggin_mock):
            runner = TestRunner('module_log')
            result = runner.get_logger()
            loggin_mock.getLogger.assert_called_once_with('module_log')
            self.assertEqual(loggin_mock.getLogger(), result)

    class get_log_filename(unittest.TestCase):

        @patch('soktest.runner.path.exists')
        def test_with_path_exists(self, exists_mock):
            exists_mock.return_value = True
            runner = TestRunner('module', 'test_log.log', 'log_dir')
            result = runner.get_log_filename()

            exists_mock.assert_called_once_with('log_dir')
            self.assertEqual('log_dir/test_log.log', result)

        @patch('soktest.runner.path.exists')
        def test_without_path_exists(self, exists_mock):
            exists_mock.return_value = False
            runner = TestRunner('module', 'test_log.log', 'log_dir')
            result = runner.get_log_filename()

            exists_mock.assert_called_once_with('log_dir')
            self.assertEqual('test_log.log', result)

    class start_logging(unittest.TestCase):

        @patch('soktest.runner.logging')
        def test_default(self, loggin_mock):
            with patch('soktest.runner.log_init') as log_init_mock:
                runner = TestRunner('module')

                runner.start_logging()
                log_init_mock.assert_called_once_with('module', 'sok_test')
                loggin_mock.basicConfig.assert_called_once_with(
                    level=loggin_mock.INFO,
                    format="%(asctime)-15s:%(message)s",
                    filename='test.log',
                )
                runner.get_logger().info.assert_called_once_with(
                    '\n\t*** TESTING STARTED ***')

    class prepere_specyfic_test_cases(unittest.TestCase):

        @patch.object(TestRunner, '_PrepereSpecyficTestCases')
        def test_default(self, PrepereSpecyficTestCasesMock):
            runner = TestRunner('module')
            result = runner.prepere_specyfic_test_cases('suite', 'tests_names')
            PrepereSpecyficTestCasesMock.assert_called_once_with(
                'suite', 'tests_names')
            PrepereSpecyficTestCasesMock().assert_called_once_with()
            self.assertEqual(PrepereSpecyficTestCasesMock()(), result)


class _PrepereSpecyficTestCasesTests_Base(unittest.TestCase):

    def setUp(self):
        self.suite = MagicMock()
        self.obj = TestRunner._PrepereSpecyficTestCases(self.suite, ['name1'])


class Runner_PrepereSpecyficTestCasesTests(TestOrganizer):

    class __init__(_PrepereSpecyficTestCasesTests_Base):

        def test_default(self):
            self.assertEqual(self.suite, self.obj.suite)
            self.assertEqual(['name1'], self.obj.tests_names)

    class unpack_name(_PrepereSpecyficTestCasesTests_Base):

        def test_default(self):
            result = self.obj.unpack_name('package.module.class:fun')
            self.assertEqual(['package.module.class', 'fun'], result)

    class get_test_case(_PrepereSpecyficTestCasesTests_Base):

        def test_exists(self):
            with patch('soktest.runner.TestCase._alltests_dict', {}) as alltests_dict_mock:
                alltests_dict_mock['something'] = 123
                self.assertEqual(123, self.obj.get_test_case('something'))

        def test_not_texists(self):
            with patch('soktest.runner.TestCase._alltests_dict', {}):
                self.assertRaises(
                    RuntimeError, self.obj.get_test_case, 'something')

    class validate_test_case(_PrepereSpecyficTestCasesTests_Base):

        def test_success(self):
            self.obj.validate_test_case('test_case', 'name')

        def test_fail(self):
            with patch('soktest.runner.TestCase._alltests_dict', {}):
                self.assertRaises(
                    RuntimeError, self.obj.validate_test_case, None, 'name')

    class prepere_suite(_PrepereSpecyficTestCasesTests_Base):

        def test_without_method_name(self):
            result = self.obj.prepere_suite('case', None)
            self.suite.loadTestsFromTestCase.assert_called_once_with('case')
            self.assertEqual(self.suite.loadTestsFromTestCase(), result)

        @patch('soktest.runner.unittest.TestSuite')
        def test_with_method_name(self, TestSuiteMock):
            case = MagicMock()
            result = self.obj.prepere_suite(case, 'method')
            TestSuiteMock.assert_called_once_with()
            case.assert_called_once_with('method')
            TestSuiteMock().addTest.assert_called_once_with(case())
            self.assertEqual(TestSuiteMock(), result)

    class __call__(_PrepereSpecyficTestCasesTests_Base):

        @patch('soktest.runner.unittest.TestSuite')
        def test_default(self, TestSuiteMock):
            with patch('soktest.runner.TestCase._alltests_dict', {}) as alltests_dict_mock:
                alltests_dict_mock['name1'] = MagicMock()
                result = self.obj()
                self.suite.loadTestsFromTestCase.assert_called_once()
                self.assertEqual([self.suite.loadTestsFromTestCase()], result)
