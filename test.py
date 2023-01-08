#!/bin/env python
from windows import *
from time import sleep
import os

# test code
if __name__ == "__main__":
        w,h = os.get_terminal_size() 
        root = Screen()

        win = root.new_child_window(70, 20, 0,0)
        win.border()
        win.fill()
        win.write_text("Window 1", 2,1)

        c_win = win.new_child_window(55,13,5,5, is_inverted=True)
        c_win.write_text("Window 2", 2,1)
        c_win.fill()

        cc_win = c_win.new_child_window(30,5, 2,5, is_inverted=False)
        cc_win.write_text("window 3", 2,1)
        cc_win.fill()


        def main(): 
                print("\033[?1049h", end="") # enable alternative screen buffer
                print("\033[0;0H", end="") # cursor to top left
                root.refresh()
                print("\033[?25l", end="") # hide cursor

        try:
                while True:
                        main()
                        sleep(0.1)

        except KeyboardInterrupt:
                print("\033[?1049l", end="") # disable alternative screen buffer
                print("\033[?25h", end="") # show cursor