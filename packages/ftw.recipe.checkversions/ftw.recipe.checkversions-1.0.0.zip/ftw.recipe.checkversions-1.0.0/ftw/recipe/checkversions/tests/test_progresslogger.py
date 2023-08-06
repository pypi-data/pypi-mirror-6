from StringIO import StringIO
from ftw.recipe.checkversions.progresslogger import ProgressLogger
from time import sleep
from unittest2 import TestCase


class TestProgressLogger(TestCase):

    def test_succeeding_logging(self):
        output = StringIO()

        with ProgressLogger(5, output, timeout=0.03) as step:
            for i in range(5):
                step()
                sleep(0.0151)

        self.assertEqual(
            '\n'.join(('1 of 5 (20%)',
                       '3 of 5 (60%)',
                       '5 of 5 (100%)')),
            output.getvalue().strip())

    def test_failing_logging(self):
        timeout = 0

        output = StringIO()
        with self.assertRaises(ValueError):

            data = range(5)

            with ProgressLogger(data, output, timeout=timeout) as step:
                for i in data:
                    if i == 3:
                        raise ValueError('baz')

                    step()

        self.assertEqual(
            '\n'.join(('1 of 5 (20%)',
                       '2 of 5 (40%)',
                       '3 of 5 (60%)',)),
            output.getvalue().strip())

    def test_accepts_iterable_object(self):
        items = range(5)

        output = StringIO()
        with ProgressLogger(items, output) as step:
            for _item in items:
                step()

        self.assertEqual('1 of 5 (20%)', output.getvalue().strip())

    def test_acts_as_iterable_wrapper(self):
        output = StringIO()
        items = range(5)

        result = []

        for item in ProgressLogger(items, output):
            result.append(item)

        self.assertEqual('1 of 5 (20%)', output.getvalue().strip())

        self.assertEqual(
            items, result,
            'Iterating over the progresslogger yields the original items.')
