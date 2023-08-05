import unittest
import logging

from .testcase import TestCaseTypeTests, TestCaseTest
from .runner import RunnerTests, Runner_PrepereSpecyficTestCasesTests

all_test_cases = [
    TestCaseTypeTests,
    TestCaseTest,

] + RunnerTests.get_all() + Runner_PrepereSpecyficTestCasesTests.get_all()


def get_all_test_suite():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)-15s:%(message)s", filename='test.log')
    logging.getLogger('soktest').info('\n\t*** TESTING STARTED ***')
    suite = unittest.TestLoader()
    prepered_all_test_cases = []
    for test_case in all_test_cases:
        prepered_all_test_cases.append(
            suite.loadTestsFromTestCase(test_case)
        )
    return unittest.TestSuite(prepered_all_test_cases)
