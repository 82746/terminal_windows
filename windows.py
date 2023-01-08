#!/bin/env python3

import string
import os

class Pixel:
        class Decoration:
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

        def __init__(self, value:chr=None, decors:list[chr]=[], z:int=0) -> None:
                self.__value = value
                self.__z = z
                self.__decors = decors
                self.__decorated_value = value
                self.__gen_decorated_str()
        
        def __gen_decorated_str(self) -> None:
                if self.__value == None:
                        self.__decorated_value = None
                        return

                
                self.__decorated_value = "".join(self.__decors) + self.__value + Pixel.Decoration.RESET

        # valid decors in Pixel.Decoration
        def add_decor(self, decor:chr) -> None:
                if decor not in self.__decors:
                        self.__decors.append(decor)
                self.__gen_decorated_str()

        def rm_decor(self, decor:chr) -> None:
                if decor in self.__decors:
                        self.__decors.remove(decor)
                self.__gen_decorated_str()
        
        @property
        def value(self):
                return self.__value

        @property
        def decorated_value(self):
                return self.__decorated_value
        
        @property
        def z(self):
                return self.__z

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

                self.__pixmap = [[[]]]
                self.__clear_pixmap()

                self.__children = []
                self.__parent = None

                self.__is_translucent = is_translucent
                self.__is_inverted = is_inverted

                # including children's content
                self.__rendered_pixmap = [[]]
                self.__clear_rendered_pixmap()

        def __clear_pixmap(self) -> None:
                # clear and fill with empty
                self.__pixmap = []
                for y in range(0,self.__height):
                        self.__pixmap.append([])

                        for x in range(0,self.__width):
                                self.__pixmap[y].append([ Pixel(value=None, z=-10) ])

        def __clear_rendered_pixmap(self) -> None:
                # clear and fill with empty
                self.__rendered_pixmap = []
                for y in range(0,self.__height):
                        self.__rendered_pixmap.append([])

                        for x in range(0,self.__width):
                                self.__rendered_pixmap[y].append(Pixel(value=None, z=-10))


        def border(self, t:str="─", l:str="│", r:str="│", b:str="─", tl:str="┌", tr:str="┐", bl:str="└", br:str="┘", z=1) -> None:
                """
                Add borders to window.
                """
                # top 
                for x in range(1,self.__width-1):
                        self.__pixmap[0][x].append(Pixel(t,z=z))

                # bottom
                for x in range(1,self.__width-1):
                        self.__pixmap[self.__height - 1][x].append(Pixel(b,z=z))

                # left
                for y in range(1,self.__height-1):
                        self.__pixmap[y][0].append(Pixel(l,z=z))

                #right
                for y in range(1,self.__height-1):
                        self.__pixmap[y][self.__width - 1].append(Pixel(r,z=z))
                
                #tl, tr, bl, br
                self.__pixmap[0][0].append(Pixel(tl,z=z))
                self.__pixmap[0][self.__width - 1].append(Pixel(tr,z=z))
                self.__pixmap[self.__height - 1][0].append(Pixel(bl,z=z))
                self.__pixmap[self.__height - 1][self.__width - 1].append(Pixel(br,z=z))
        

        
        def write_text(self, text:str, x:int, y:int, z:int=1, wrapping=False) -> None:
                """
                Write text inside window. X and Y positions are relative to window's position.
                """
                c_x_pos = x
                c_y_pos = y

                for c in text:
                        if c not in string.printable:
                                continue

                        if c_x_pos < self.__width and c_y_pos < self.__height:
                                self.__pixmap[c_y_pos][c_x_pos].append(Pixel(c,z=z))

                        c_x_pos += 1


        def __render_pixmap(self) -> list[list]:
                # update decorations
                self.__update_pixmap_invert()


                # clear render and fill with own content first
                self.__clear_rendered_pixmap()
                y = 0
                for row in self.__pixmap:
                        x = 0
                        for z_axis in row:
                                # check if pixel is outside of window
                                if x > self.__width - 1 or y > self.__height - 1 or x < 0 or y < 0:
                                        continue
                                # choose(by highest z) the pixel to be rendered from overlapping pixels
                                z_axis.sort(key=lambda pixel : pixel.z, reverse=True)
                                top_pixel = z_axis[0]
                                self.__rendered_pixmap[y][x] = top_pixel
                                x += 1
                        y += 1


                # overwrite with children's content 
                for child in self.__children:
                        child_map = [[]]
                        child_map = child.__render_pixmap()
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
                                        #if child.is_inverted:
                                        #        pixel.add_decor(Pixel.Decoration.INVERT)

                                        self.__rendered_pixmap[y][x] = pixel
                                        x += 1


                                y += 1

                return self.__rendered_pixmap

        def fill(self, z:int=-1) -> None:
                """
                Fill window with space.
                """
                # fill with " "-pixels at depth z
                for y in range(0,self.__height):
                        for x in range(0,self.__width):
                                self.__pixmap[y][x].append(Pixel(value=" ",z=z))


        def _render_and_draw(self) -> None:
                """
                Render and draw window and all its sub-windows.
                """
                self.__render_pixmap()

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
                """
                Clear all window's content.
                """
                self.__clear_pixmap()
        
        def new_child_window(self, width:int, height:int, x:int, y:int, is_translucent:bool = False, is_inverted:bool = False) -> 'Window':
                child_win = Window(width, height, x, y, is_translucent=is_translucent, is_inverted=is_inverted)
                self.__children.append(child_win)
                return child_win

        def pos(self) -> tuple:
                """
                Get window's X and Y positions.
                """
                return (self.__x, self.__y)
        

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
                """
                Set window's width and height.
                """
                if width and height > 1:
                        self.__width = width
                        self.__height = height
                else:
                        raise ValueError
        
        def __update_pixmap_invert(self):
                for row in self.__pixmap:
                        for z_axel in row:
                                for pixel in z_axel:
                                        if self.__is_inverted == True:
                                                pixel.add_decor(Pixel.Decoration.INVERT)
                                        elif self.__is_inverted == False:
                                                pixel.rm_decor(Pixel.Decoration.INVERT)

        def invert(self, invert:bool):
                """
                Invert window's colors.
                """
                self.__is_inverted = invert
                
class Screen(Window):
        def __init__(self) -> None:
                w,h = os.get_terminal_size()
                super().__init__(w, h, 0, 0)
        
        def refresh(self) -> None:
                """
                Update/refresh/re-draw the screen.
                """
                w,h = os.get_terminal_size()
                super().set_size(w,h)
                super()._render_and_draw()
        











