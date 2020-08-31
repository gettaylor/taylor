import unittest

from app import found_trigger_words_in_message

class Testing_Messages(unittest.TestCase):
    
    # def test(self):
    #     self.assertTrue(True)
    def test_found_trigger_words_in_message(self):
        '''
        Testing if there are trigger words being used in messages
        '''
        actual = found_trigger_words_in_message("white-list")
        self.assertEqual(actual, set(["white-list"]))

if __name__ == "main":
    unittest.main()
    
