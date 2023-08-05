import unittest


class TestOrganizer(object):

    @classmethod
    def get_all(cls):
        tests = []
        for name in dir(cls):
            element = getattr(cls, name)
            is_class = isinstance(element, type)
            if is_class:
                is_test = issubclass(element, unittest.TestCase)
                if is_test:
                    tests.append(element)
        return tests
