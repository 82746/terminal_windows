#!/bin/env python3

from datetime import datetime
from time import sleep
import sys
import os
import string

class Pixel:
        class Decor:
                # SGR control sequences
                RESET = '\033[0m'
                BOLD = '\033[1m'
                FAINT = '\033[2m'
                ITALIC = '\033[3m'
                UNDERLINE = '\033[4m'
                SLOW_BLINK = '\033[5m'
                RAPID_BLINK = '\033[6m'
                INVERT = '\033[7m'
                STRIKE = '\033[8m'

        def __init__(self, value:chr=None, decors:list[chr]=[]) -> None:
                self.__value = value
                self.__decors = decors
                self.__decorated_value = value
                self.__gen_decorated_str()
        
        def __gen_decorated_str(self) -> None:
                if self.__value == None:
                        self.__decorated_value = None
                        return

                
                self.__decorated_value = "".join(self.__decors) + self.__value + Pixel.Decor.RESET

                #print(self.__decorated_value)

        # valid decors in Pixel.Decor
        def add_decor(self, decor:chr) -> None:
                if decor not in self.__decors:
                        self.__decors.append(decor)
                self.__gen_decorated_str()

        def rm_decor(self, decor:chr) -> None:
                self.__decors.remove(decor)
                self.__gen_decorated_str()
        
        @property
        def value(self):
                return self.__value

        @property
        def decorated_value(self):
                return self.__decorated_value

        @value.setter
        def value(self, new_val):
                self.__gen_decorated_str()
                self.__value = new_val
        


class Window:
        def __init__(self, width:int, height:int, x:int, y:int, is_translucent:bool=False, is_inverted:bool=False) -> None:
                self.__height = height
                self.__width = width
                self.__x = x
                self.__y = y

                self.__pixmap = [[]]
                self.__clear_window_content()

                self.__children = []
                self.__parent = None
                self.__z = 0

                self.__is_translucent = is_translucent
                self.__is_inverted = is_inverted

                # including children's content
                self.__rendered_pixmap = [[]]

        def __clear_window_content(self) -> None:
                # clear and fill with empty
                self.__pixmap = []
                for y in range(0,self.__height):
                        self.__pixmap.append([])

                        for x in range(0,self.__width):
                                self.__pixmap[y].append(Pixel(value=None))

        def border(self, t:str="─", l:str="│", r:str="│", b:str="─", tl:str="┌", tr:str="┐", bl:str="└", br:str="┘") -> None:
                # top 
                for x in range(0,self.__width-1):
                        self.__pixmap[0][x] = Pixel(t)

                # bottom
                for x in range(0,self.__width-1):
                        self.__pixmap[self.__height - 1][x] = Pixel(b)

                # left
                for y in range(0,self.__height-1):
                        self.__pixmap[y][0] = Pixel(l)

                #right
                for y in range(0,self.__height-1):
                        self.__pixmap[y][self.__width - 1] = Pixel(r)
                
                #tl, tr, bl, br
                self.__pixmap[0][0] = Pixel(tl)
                self.__pixmap[0][self.__width - 1] = Pixel(tr)
                self.__pixmap[self.__height - 1][0] = Pixel(bl)
                self.__pixmap[self.__height - 1][self.__width - 1] = Pixel(br)
        

        
        def write(self, text:str, x, y, wrapping=False) -> None:
                c_x_pos = x
                c_y_pos = y

                for c in text:
                        if c not in string.printable:
                                continue

                        if c_x_pos < self.__width and c_y_pos < self.__height:
                                self.__pixmap[c_y_pos][c_x_pos] = Pixel(c)

                        c_x_pos += 1



        def pos(self) -> tuple:
                return (self.__x, self.__y)

        def render_char_map(self) -> list[list]:
                # fill with own conent first
                self.__rendered_pixmap = self.__pixmap

                # overwrite with children's content (if child.z > self.z)
                for child in self.__children:
                        child_map = [[]]
                        child_map = child.render_char_map()
                        ch_x, ch_y= child.pos()

                        y = ch_y
                        for row in child_map:
                                x = ch_x
                                if self.__height - 1 < y or y < 0:
                                        y += 1
                                        continue

                                for pixel in row:
                                        if self.__width - 1 < x or x < 0:
                                                x += 1
                                                continue

                                        if pixel.value == None:
                                                if child.is_translucent:
                                                        self.__rendered_pixmap[y][x] = Pixel(value=None)
                                                        x += 1
                                                        continue

                                        # add decorated char 
                                        if child.is_inverted:
                                                pixel.add_decor(Pixel.Decor.INVERT)

                                        self.__rendered_pixmap[y][x] = pixel
                                        x += 1


                                y += 1

                return self.__rendered_pixmap

        def fill_over(self) -> None:
                # clear and fill with " "
                self.__pixmap = []
                for y in range(0,self.__height):
                        self.__pixmap.append([])

                        for x in range(0,self.__width):
                                self.__pixmap[y].append(Pixel(value=" "))

        def fill_under(self) -> None:
                for y in range(0,self.__height):
                        for x in range(0,self.__width):
                                if self.__pixmap[y][x].value == None:
                                        self.__pixmap[y][x] = Pixel(value=" ")



        def draw_render(self) -> None:
                self.render_char_map()
                print("\033[0;;H", end="") # cursor to pos 0,0 before printing
                window_str = ""

                y = 0
                for row in self.__rendered_pixmap:
                        x = 0
                        if self.__height - 1 < y or y < 0:
                                y += 1
                                continue

                        for pixel in row:
                                # clip stuff outside window borders
                                if self.__width - 1 < x or x < 0:
                                        x += 1
                                        continue

                                if pixel.decorated_value == None:
                                        window_str += " "
                                else:
                                        window_str += pixel.decorated_value

                                x += 1
                                
                        y += 1

                        window_str += '\n'

                window_str = window_str.strip('\n ') # remove last extra linebreak

                
                print(window_str, flush=True, end="")


        def clear_window(self) -> None:
                self.__clear_window_content()
        
        def new_child_window(self, width:int, height:int, x:int, y:int, is_translucent:bool = False, is_inverted:bool = False) -> 'Window':
                child_win = Window(width, height, x, y, is_translucent=is_translucent, is_inverted=is_inverted)
                self.__children.append(child_win)
                return child_win

        @property
        def size(self) -> tuple:
                return (self.__width, self.__height)

        @property
        def z(self) -> int:
                return self.__z

        @property
        def is_translucent(self) -> bool:
                return self.__is_translucent

        @property
        def is_inverted(self) -> bool:
                return self.__is_inverted

        def set_size(self, width:int, height:int) -> None:
                if width and height > 1:
                        self.__width = width
                        self.__height = height
                else:
                        raise ValueError

        def invert(self, invert:bool):
                self.__is_inverted = invert
                



class Calendar:
        def __init__(self) -> None:
                pass  
w,h = os.get_terminal_size() 
root = Window(w,h,0,0)

win = root.new_child_window(50, 20, 0,0)
win.border()
win.write("helloa", 2,2)
win.write("helloa", 2,3)
win.write("helloa", 2,4)
win.write("helloa", 10,11)

c_win = win.new_child_window(90,5, 10,8, is_translucent=True)
c_win.border()
c_win.write("ali-ikkuna rajaa sen ali-ikkunat", 1,1)

cc_win = root.new_child_window(50,5,16,16, is_inverted=True)
cc_win.write("x   -  Window name", 1,0)
cc_win.fill_under()

#print(cc_win.content[1])


        
w,h = os.get_terminal_size()

def main(): 
        print("\033[?1049h", end="") # enable alternative screen buffer
        print("\033[0;0H", end="") # cursor to top left
        root.draw_render()
        print("\033[?25l", end="") # hide cursor

try:
        while True:
                main()
                sleep(0.1)
except:
        print("\033[?1049l", end="") # disable alternative screen buffer
        print("\033[?25h", end="") # show cursor
