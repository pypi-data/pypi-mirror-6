
import os
import sys
import termios
import contextlib
import time 
import re
from colorama import Fore, Back, Style, init, deinit
init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
from termcolor import cprint 
from pyfiglet import figlet_format, Figlet
import copy
import aalib
import Image
import urllib2
from cStringIO import StringIO
import xml.etree.ElementTree as ET
import itertools


NEXT_SLIDE = '\x1b[C'
PREVIOUS_SLIDE = '\x1b[D'
QUIT = chr(4)
spacer = re.compile("\s+")

strip_ANSI_sub = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE).sub

def strip_ANSI(s):
    return strip_ANSI_sub("", s)


COLOR_DICT = {
        # Foreground & Background ANSI Color Constants
        'black': Fore.BLACK,
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE,
        'reset': Fore.RESET,
}


class SlideParser(object):
    @staticmethod
    def node_parser(element, args=[]):
        ctags = {'h': 'heading',
                 't': 'text',
                 'i': 'image',
                 'ty' : 'typewriter', 
                 'c' : 'command',
                 'f' : 'format' }
#        print element.tag
        if len(element) == 0:
            sc = SlideComponent(element.text.strip("\n\t "), args)
            return sc
        else:
            slide_component = SlideComponent(args = args)
            components = []
            
            for child in element:
                ctag = child.tag
                if ctag in ctags:
                    ctag = ctags[ctag]                
                component = SlideParser.node_parser(child, args + [[ctag, child.attrib]])
                components.append(component)
            slide_component.components = components
            return slide_component

    @staticmethod
    def slide_parser(element):
        components = []
        ctags = {'h': 'heading',
                 't': 'text',
                 'i': 'image',
                 'ty' : 'typewriter', 
                 'c' : 'command',
                 'f' : 'format' }

        for child in element:
            ctag = child.tag
            if ctag in ctags:
               ctag = ctags[ctag]                

            components.append(SlideParser.node_parser(child, [[ctag, child.attrib]]))
        return Slide(components,  element.attrib)
 
    @staticmethod
    def slides_parser(text):
        tree = ET.fromstring(text)
        slides = []
        for child in tree:
            if child.tag == "slide":
                slide = SlideParser.slide_parser(child)
                slides.append(slide)
        return slides

class SlideComponent(object):
    def __init__(self, text = "", args = [], components = []):
        self.text = text
        self.args = {}
        self.components = components
        for arg in args:
            self.args[arg[0]] = arg[1]

    @staticmethod
    def printer_function(color, style = []):
        def p_func(text):
            SlideDeck.format_print(COLOR_DICT[color] + text,options = style)
        return p_func

    @staticmethod
    def print_text(text,args, nospace = False):
        printer_func = sys.stdout.write
        
        text = text.replace("\$","\n")
        
        if 'center' in args and nospace == False:
            rows, cols = SlideDeck.get_term_size()
            if 'leftalign' in args['center']:
#                print "Hello !"
                text = "\n".join([" "*(cols/3) + t for t in text.split("\n")])
            elif 'format' in args:
                text = SlideDeck.center(text, cols)
            else:
                text = SlideDeck.center_color(text,cols)

        if 'format' in args:
            color = args['format']['color'] if 'color' in args['format'] else 'white'
            if 'style' in args['format']:
                printer_func = SlideComponent.printer_function(color, args['format']['style'].split(','))
            else:
                printer_func = SlideComponent.printer_function(color)
                
        if 'typewriter' in args:
            duration = 0.1 #customize this
            for c in text:
                printer_func(c)
                sys.stdout.flush()
                if not c.isspace():
                    time.sleep(duration)
        else:
            printer_func(text)
                

    def present(self, nospace = False):
        
        if 'heading' in self.args and len(self.components) == 0:            
            self.args["heading"]["font"] = self.args["heading"]["font"] if 'font' in self.args["heading"] else "starwars"
            self.args["heading"]["fg"] = self.args["heading"]["fg"] if 'fg' in self.args["heading"] else "yellow"
            self.args["heading"]["bg"] = self.args["heading"]["bg"] if 'bg' in self.args["heading"] else "red"
            self.args["heading"]["style"] = self.args["heading"]["style"] if 'style' in self.args["heading"] else "bold"
 
            SlideDeck.print_heading(self.text,
                                    self.args["heading"]["font"],
                                    self.args['heading']["fg"],
                                    "on_" + self.args['heading']["bg"],
                                    self.args['heading']["style"].split(","))

            

        if 'format' in self.args and len(self.components) == 0: 
#            print self.text,self.args,nospace
            self.print_text(self.text + " ",self.args, nospace)
#            nospace = True

        elif 'text' in self.args and len(self.components) == 0: 
#            print self.text,self.args,nospace
            self.print_text(self.text,self.args, nospace)
#            nospace = True
 


        elif 'typewriter' in self.args and len(self.components) == 0: 
          #  print self.text,self.args,self.components
            self.print_text(self.text,self.args)


        if 'image' in self.args and len(self.components) == 0:
            # Put url option too 
            self.args["image"]["width"] = self.args["image"]["width"] if 'weight' in self.args["image"] else "40"
            self.args["image"]["height"] = self.args["image"]["height"] if 'height' in self.args["image"] else "40"

            SlideDeck.render_image(int(self.args["image"]["width"]),
                                   int(self.args["image"]["height"]),
                                   self.text)
        if 'command' in self.args and len(self.components) == 0:
            if 'print' in self.args['command']:
                SlideComponent.print_text(self.text,self.args)
                sys.stdout.flush()
                time.sleep(0.5)
            os.system(self.text.replace('\$',''))

        if len(self.components) > 0:
            for i,c in enumerate(self.components):
                if 'text' in self.args and len(self.components) > 0 and i > 0:
                    nospace = True
                c.present(nospace)

class Slide(object):
    def __init__(self,components, args = []):
        self.components = components
        self.args = args
    
    @property
    def slide_height(self):
        all_text  = ""
        for c in self.components:
            if 'text' in c.args:
                all_text += c.text
        return len(all_text.split("\n"))

    def present(self):
        rows, cols = SlideDeck.get_term_size()
        slide_height = self.slide_height
        top_margin = (rows-(slide_height if slide_height > 1 else 0))/2
#        print self.args
        if 'center' in self.args:
            print "\n"*(top_margin-1)
        
        for component in self.components:
            component.present()


class SlideDeck(object):
    
    def __init__(self,slides):
        self.slides = slides
        self.count = 0

    @contextlib.contextmanager
    def raw_mode(self,file):
        old_attrs = termios.tcgetattr(file.fileno())
        new_attrs = old_attrs[:]
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        try:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
            yield
        finally:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)

    
    @staticmethod
    def from_file(filename):
        with open(filename,"r") as f:
            text = f.read()
            slides = SlideParser.slides_parser(text)
            return SlideDeck(slides)
    @staticmethod
    def print_component(component, level = 0):
        if len(component.components) == 0:
            print level*"\t", component.args
        else:
            print level*"\t", component.args
            for c in component.components:
                SlideDeck.print_component(c,level + 1)
        
    @staticmethod
    def print_heading(text, fontname, background, foreground, options = [], width = 80):
        fig  = Figlet(fontname, justify = "right", width = 5)
        cprint(fig.renderText(text), background, foreground, attrs=options)

    @staticmethod
    def format_print(text, options=[]):
        cprint(text,   attrs= options, end='')

    @staticmethod
    def clear():
        '''Clears the screen. Should work everywhere.'''
        os.system('cls' if os.name=='nt' else 'clear')
    
    @staticmethod
    def get_term_size():
        '''Gets the size of your terminal. May not work everywhere. YMMV.'''
        rows, columns = os.popen('stty size', 'r').read().split()
        return int(rows), int(columns)

    @staticmethod
    def center(string, width):
        return  '\n'.join(((" "*(width/3)) + line for line in string.split("\n")))

    @staticmethod
    def center_color(string, width):
        center_string = []
        for line in string.split("\n"):
            strip_line = strip_ANSI(line)
            lefts, rights = "", ""
            left_right = True
            while len(strip_line) < width:
                if left_right:
                    strip_line = " " + strip_line
                    lefts += " "
                else:
                    strip_line += " "
                    rights += " "
                left_right = not left_right
            center_string.append("".join([lefts, line, rights]))
        return '\n'.join(center_string)


    @staticmethod
    def render_image(width,height,image_path):
        screen = aalib.AsciiScreen(width=width, height=height)
        fp = StringIO(open(image_path).read())
        image = Image.open(fp).convert('L').resize(screen.virtual_size)
        screen.put_image((0, 0), image)
        print screen.render()

    def present_slide(self,slide = None):
        ''' Presents Individual Slide ''' 
        SlideDeck.clear()
        slide.present()

    def present(self):
        SlideDeck.clear()
        self.present_slide(self.slides[self.count])

        with self.raw_mode(sys.stdin):
            try:
                while True:
                    ch = sys.stdin.read(3)
                    if not ch or ch == QUIT:
                        break
                    if ch == NEXT_SLIDE:
                        if self.count + 1 <= (len(self.slides) - 1):
                            self.present_slide(self.slides[self.count+1])
                            self.count += 1

                    elif ch == PREVIOUS_SLIDE:
                        if self.count - 1 >= 0:
                            self.present_slide(self.slides[self.count  - 1])
                            self.count -= 1
            except (KeyboardInterrupt, EOFError):
                pass


if __name__ == "__main__":
    s = SlideDeck.from_file(sys.argv[1])
#    for sl in s.slides:
#        print sl.args
    s.present()
