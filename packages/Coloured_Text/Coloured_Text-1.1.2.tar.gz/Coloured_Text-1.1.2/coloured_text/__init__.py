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


def rainbow(msg, colours=["\033[96m","\033[95m","\033[94m","\033[93m","\033[92m","\033[91m","\033[90m", "\033[0m"], end="\033[0m\n"):
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


def colouredPrint(msg, colour="reset", end="\033[0m\n"):
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
    sys.stdout.write(printColour + msg + end)


if __name__ == "__main__": # executed if the file is run directly
	
	# tells the user about Colour Text
    print("\033[92mThis file is the \033[91mColoured Text\033[94m module/libray. It is not ment to")
    print("be executed directly but rather imported and the class within used")
    print("to create coloured text in \022[90mterminal applications. For more infomation")
    print("please read the README.md file, go to http://www.github.com/icedvariables/coloured_text")
    print("or go the python package index page https://pypi.python.org/pypi/Coloured_Text")
