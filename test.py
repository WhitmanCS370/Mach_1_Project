import unittest
from sound_cli import *

class TestSoundRenaming(unittest.TestCase):

    
    def test_rename_sound(self):
        self.assertEqual(rename_sound("test_sound_file.wav"), "test sound file")
        self.assertEqual(rename_sound("another_test_sound.wav"), "another test sound")
        self.assertEqual(rename_sound("no underscores.wav"), "no underscores")
        self.assertEqual(rename_sound("sound_file no wav"), "sound file no wav")
        
    def test_rename_sound_arg(self):
        sys.argv = ['sound_cli.py', '--rename', './sounds/testRename.wav', './sounds/successRename.wav']
        
        with open('./sounds/testRename.wav', 'w') as f:
            f.write('')

        rename_sound_arg()

        self.assertTrue(os.path.exists('./sounds/successRename.wav'))
        
        os.remove('./sounds/successRename.wav')


if __name__ == '__main__':
    unittest.main()

