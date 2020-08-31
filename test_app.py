import unittest

from app import found_trigger_words_in_message

class Testing_Messages(unittest.TestCase):
    
    # def test(self):
    #     self.assertTrue(True)
    def test_found_trigger_words_in_message(self):
        '''
        Testing if there are trigger words being used in messages
        '''
        actual = found_trigger_words_in_message("hi")
        self.assertNotEqual(actual, set(["hi"]))

        actual = found_trigger_words_in_message("white-list")
        self.assertEqual(actual, set(["white-list"]))

        actual = found_trigger_words_in_message("hey guys")
        self.assertEqual(actual, set(["guys"]))
        
        actual = found_trigger_words_in_message("master list")
        self.assertEqual(actual, set(["master"]))

        actual = found_trigger_words_in_message("hi guys")
        self.assertEqual(actual, set(["guys"]))

        actual = found_trigger_words_in_message("MASTER")
        self.assertEqual(actual, set(["master"]))

        actual = found_trigger_words_in_message("WHITELIST")
        self.assertEqual(actual, set(["whitelist"]))

        actual = found_trigger_words_in_message("WHITE LIST")
        self.assertEqual(actual, set(["white list"]))

        actual = found_trigger_words_in_message("WHITE-LIST")
        self.assertEqual(actual, set(["white-list"]))

        actual = found_trigger_words_in_message("BlAck-LIST")
        self.assertEqual(actual, set(["black-list"]))

if __name__ == "main":
    unittest.main()
    
