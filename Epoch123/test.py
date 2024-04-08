from play_sound_commands import *
from sound_data import *
from sound_dir_commands import *


# test that list_sounds() works
def test_list_sounds():
    assert list_sounds() == None

# test that search_sound_dir() works
def test_search_sound_dir():
    # search_sound_dir(test="toast")
    assert search_sound_dir() == None

def test_sound_visualize():
    assert curses.wrapper(sound_visualize, "toast/toaster-2.wav") == None

def test_play_sound():
    assert play_sound("toast/toaster-2.wav") == None

def test_play_sound_simultaneously():
    sounds = ["coffee/coffee-slurp-2.wav", "coffee/coffee-slurp-3.wav", "coffee/coffee-slurp-6.wav"]
    assert play_sound_simultaneously(sounds) == None

def test_play_sound_sequentially():
    sounds = ["coffee/coffee-slurp-2.wav", "coffee/coffee-slurp-3.wav", "coffee/coffee-slurp-6.wav"]
    assert play_sound_sequentially(sounds) == None

def test_play_random_sound():
    assert play_random_sound() == None

def test_play_sound_reverse():
    assert play_sound_reverse("toast/toaster-2.wav") == None

def test_play_sound_speed():
    assert play_sound_speed("toast/toaster-2.wav", 2) == None

def test_play_random_sound():
    assert play_random_sound() == None

def test_play_random_snippet():
    assert play_random_sound_snippet("toast/toaster-2.wav") == None

def test_play_sound_snippet():
    assert play_sound_snippet("toast/toaster-2.wav", 1500, 3000) == None

# main
if __name__ == "__main__":
    test_list_sounds()
    test_search_sound_dir()
    test_sound_visualize()
    test_play_sound()
    test_play_sound_simultaneously()
    test_play_sound_sequentially()
    test_play_random_sound()
    test_play_sound_reverse()
    test_play_sound_speed()
    test_play_random_sound()
    test_play_random_snippet()
    test_play_sound_snippet()
    print("All tests passed!")