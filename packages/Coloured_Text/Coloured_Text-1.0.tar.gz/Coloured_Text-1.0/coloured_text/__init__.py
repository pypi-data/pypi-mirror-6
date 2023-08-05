#!/usr/bin/env python


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


class Colours(object):
    """contains ansi escape characters which change the text colour
    of a terminal application"""
    
    TURQUOISE = "\033[96m"
    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    RESET = "\033[0m"



def colouredPrint(msg, colour="reset", end="\n"):
    """print coloured text. Onced the function has executed the
    colour will be reset back to it's default colour"""

    if(colour == "turquoise"):
        printColour = "\033[96m"

    elif(colour == "purple"):
        printColour = "\033[95m"

    elif(colour == "blue"):
        printColour = "\033[94m"

    elif(colour == "green"):
        printColour = "\033[92m"
            
    elif(colour == "yellow"):
        printColour = "\033[93m"
            
    elif(colour == "red"):
        printColour = "\033[91m"
            
    elif(colour == "gray"):
        printColour = "\033[90m"
            
    elif(colour == "reset"):
        printColour = "\033[0m"
        
    else:
        printColour = ""
        
    import sys # import the sys module
        
    # print the coloured message and then resets the colour
    sys.stdout.write(printColour + msg + "\033[0m" + end)


if __name__ == "__main__": # executed if the file is run directly
	
	# tells the user about Colour Text
    print("\033[92mThis file is the \033[91mColoured Text\033[94m module/libray. It is not ment to")
    print("be executed directly but rather imported and the class within used")
    print("to create coloured text in \022[90mterminal applications. For more infomation")
    print("please read the README.md file, go to http://www.github.com/icedvariables/coloured_text")
    print("or go the python package index page https://pypi.python.org/pypi/Coloured_Text")
