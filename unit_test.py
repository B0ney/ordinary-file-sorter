import unittest
import main
# python -m unittest unit_test.py
class Testclass(unittest.TestCase):
    '''testing'''
    def test_data_types(self):
        '''
        The purpose of this test is to ensure the data stored is as expected.
        These classes contain no methods for serialisation purposes.
        So do not expect these classes to contain methods.      
        '''
        #--------------------------------------------#

        data_1 = ("test_file", "exe",  "~/Downloads")
        data_2 = ("test_file", ".jar", "~/Downloads")

        file_1 = main.File(data_1[0], data_1[1], data_1[2])
        file_2 = main.File(data_2[0], data_2[1], data_2[2])

        self.assertEqual(file_1.name,       data_1[0])
        self.assertEqual(file_1.extension,  data_1[1])
        self.assertEqual(file_1.path,       data_1[2])

        self.assertEqual(file_2.name,       data_2[0])
        self.assertEqual(file_2.extension,  data_2[1])
        self.assertEqual(file_2.path,       data_2[2])

        #--------------------------------------------#

        data_3 = ("test_folder",    "~/Downloads")
        data_4 = ("Homework",       "~/Downloads/Picture")

        folder_1 = main.Folder(data_3[0], data_3[1])
        folder_2 = main.Folder(data_4[0], data_4[1])

        self.assertEqual(folder_1.name, data_3[0])
        self.assertEqual(folder_1.path, data_3[1])

        self.assertEqual(folder_2.name, data_4[0])
        self.assertEqual(folder_2.path, data_4[1])

    def test_move_token(self):
        '''
        The move token class stores 2 strings:
        1) Source (Can either be a file or folder)
        2) Destination

        We need to ensure that these two properties are fully expanded, i.e no "~"

        Future problem:
            We don't want the source and destination folder to be the same
        '''
        #--------------------------------------------#
        
        source_1, destination_1 = ("./test_folder", "./test_folder")

        move_token_1 = main.MoveToken(source_1, destination_1)
        self.assertFalse(move_token_1.is_valid())

        #--------------------------------------------#
        # Non-existent sources should return false
        source_2, destination_2 = ("./test_folder_two/fjajfldajfldajflda.txt", "./test_folder")

        move_token_2 = main.MoveToken(source_2, destination_2)
        self.assertFalse(move_token_2.is_valid())

        #--------------------------------------------#
        # Existing files, should return true
        source_3, destination_3 = ("./test_folder/test_file.txt", "./test_folder_3")

        move_token_3 = main.MoveToken(source_3, destination_3)
        self.assertTrue(move_token_3.is_valid())
        # pass


