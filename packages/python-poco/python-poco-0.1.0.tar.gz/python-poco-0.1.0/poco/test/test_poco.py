import unittest
from requests.exceptions import HTTPError

from poco.poco import PocoLocation, PocoSearcher


class PocoTest(unittest.TestCase):
    def test_results_as_dicts(self):
        results = PocoSearcher.results_as_dicts('Wingate Park')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], dict)

    def test_results_as_objects(self):
        results = PocoSearcher.results_as_objects('Wingate Park')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], PocoLocation)

    def test_no_results(self):
        results = PocoSearcher.results_as_objects('kekekeke')
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_invalid(self):
        self.assertRaises(HTTPError, PocoSearcher.results_as_objects, 'a')



