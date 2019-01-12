import unittest
import lyric_crawler
import funcs


class TestLyricCrawler(unittest.TestCase):

    def test_user_in(self):
        try:
            args = lyric_crawler.user_in()
            self.assertEqual(3, len(args))
            self.assertTrue(isinstance(args[0], str) and args[0].isdigit())
            self.assertIsInstance(args[1], lyric_crawler.SOURCE)
            self.assertIsInstance(args[2], str)
        except BaseException as e:
            self.assertIsInstance(e, SystemExit)

    def test_merge_lrc(self):
        try:
            funcs.merge_lrc(None, None)
        except BaseException as e:
            self.assertIsInstance(e, AssertionError)


if __name__ == "__main__":
    unittest.main()
