#!/usr/bin/env python

# Version: 2.0
# Date: 17 Dec 2013


# Copyright 2013 Max Black

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.



class Fore(object):
    """contains ansi escape characters which change the text colour
    of a terminal application"""
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
class Back(object):
    """contains ansi escape characters which change the text colour
    of a terminal application"""
    
    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"

class Formatting(object):
    """Contains ansi escape characters which change the formating (bold,
    underscore, etc) of text in a terminal application"""
    
    BOLD = "\033[1m"
    UNDERSCORE = "\033[4m"
    
    RESET_ALL = "\033[0m"


def rainbow(msg, colours=["\033[30m", "\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m", "\033[37m", "\033[0m"], end="\033[0m\n"):
    """print text with each letter a different colour"""
    
    import sys # import the sys module
    
    # convert the message into a list so it can be interated through in
    # a for loop
    msg = list(msg)
    
    # get the length of the colours list
    COLOURS_LENGTH = len(colours)
    
    # the string that will be print at the end
    toPrint = ""
    
    # create a j variable to iterate over the colour list
    j = 0
    
    # iterate over the message list
    for i in msg:
        
        # set the j variable back to 0 if the end of the colours list is
        # reached
        if(j == COLOURS_LENGTH):
            j = 0
        
        # add the colour to the toPrint string
        toPrint += colours[j]
        
        # add the letter to the toPrint string
        toPrint += i
        
        # add 1 to the j variable so that the next colour in the colours
        # list is used on the interation
        j+=1
        
    
    # print the toPrint string and the end string
    sys.stdout.write(toPrint+end)


def colouredPrint(msg, colour="reset", foreOrBack="fore", end="\033[0m\n"):
    """print coloured text. Onced the function has executed the
    colour will be reset back to it's default colour"""
    
    colours = {"fore":{"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m",
    "blue":"\033[34m", "magenta":"\033[35m", "cyan":"\033[36m", "white":"\033[37m", "reset":"\033[0m"},
    "back":{"black":"\033[40m", "red":"\033[41m", "green":"\033[42m", "yellow":"\033[43m",
    "blue":"\033[44m", "magenta":"\033[45m", "cyan":"\033[46m", "white":"\033[47m", "reset":"\033[0m"}}
        
    import sys # import the sys module
        
    # print the coloured message and then resets the colour
    sys.stdout.write(colours[foreOrBack][colour] + msg + end)


if __name__ == "__main__": # executed if the file is run directly
	
	# tells the user about Colour Text
    print("\033[34mThis file is the \033[32;1mColoured Text\033[34;0m module/libray. It is not ment to")
    print("be executed directly but rather imported and the classes and functions within used")
    print("to create coloured text in a \033[35mterminal\033[0m applications. For more infomation")
    print("please read the README.md file, go to http://www.github.com/icedvariables/coloured_text")
    print("or go the python package index page https://pypi.python.org/pypi/Coloured_Text")
