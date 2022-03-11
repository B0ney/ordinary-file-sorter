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

    def test_move_token_same_folder(self):
        '''Tokens with the same folder must be invalid'''
        source_1, destination_1 = ("./test_folder", "./test_folder")

        move_token_1 = main.Token(source_1, destination_1, "MOVE")
        self.assertFalse(move_token_1.is_valid())

        # Why would we move a file to the same directory?
        # This ensure the move token returns false
        source_2, destination_2 = ("./test_folder/test_file.txt", "./test_folder")

        move_token_2 = main.Token(source_2, destination_2, "MOVE")
        self.assertFalse(move_token_2.is_valid())

    def test_move_token_non_existent_path(self):
        '''MoveTokens with a non existent SOURCE are invalid'''
        #--------------------------------------------#
        source_1, destination_1 = ("./test_folder_two/fjajfldajfldajflda.txt", "./test_folder")

        move_token_1 = main.Token(source_1, destination_1, "MOVE")
        self.assertFalse(move_token_1.is_valid())

    def test_move_token_existent_path(self):
        '''MoveTokens with an existent SOURCE are valid'''

        # Existing files, should return true
        source_1, destination_1 = ("./tests/test_file.txt", "./test_folder_3")

        move_token_1 = main.Token(source_1, destination_1, "MOVE")
        self.assertTrue(move_token_1.is_valid())

    def test_move_token_no_self_harm(self):
        ''' We don't want the program to move the FOLDER containing THIS project
            Using os.chdir() should not cause issues
        '''
        import os

        # Make sure the FOLDER containing this project is untotched
        this_code_path      = os.path.realpath(__file__)
        this_code_folder    = os.path.dirname(this_code_path)
        test_destination    = this_code_folder

        move_token_1 = main.Token(this_code_path, test_destination, "MOVE")
        self.assertFalse(move_token_1.is_valid())

        move_token_2 = main.Token(this_code_folder, test_destination, "MOVE")
        self.assertFalse(move_token_2.is_valid())

if __name__ == "__main__":
    import os
    os.chdir(os.path.expanduser("~/Downloads/"))
    dir_path = os.path.realpath(__file__)
    print(dir_path)