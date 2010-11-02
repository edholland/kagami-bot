#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2010, Peter Andersson < peter@keiji.se >  

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import random
import re

class Commands(object):

    def __init__(self, command_prefix):
        self.command_prefix = command_prefix
        random.seed()
        self.command_dictionary = {
                              "choice": self.random,
                              "help": self.help,
                              "question": self.question,
                              "random": self.random,
                              "scale": self.scale,
                              }
    
    def do(self,command_line):
        """
        Delegates command request to the right command function
        """
        split_command_line = command_line.split()
        command = split_command_line[0]
        if(command in self.command_dictionary):
            return self.command_dictionary[command](command_line[len(command):].strip())
        else:
            raise Exception
    
    def help(self, argument):
        """
        Returns information about the different commands
        that the bot understands
        """
        if(argument == "%squestion" % self.command_prefix or argument == "question"):
            answer = [
                      "  %squestion QUESTION" % self.command_prefix,
                      "Returns a positive or a negative response to your question",
                      ]
        elif(argument == "%sscale" % self.command_prefix or argument == "scale"):
            answer = [
                      "  %sscale STATEMENT" % self.command_prefix,
                      "  %sscale" % self.command_prefix,
                      "Scales your statment in procent",
                      "(random number between 1 and 100)",
                      ]
        elif(argument == "%srandom" % self.command_prefix or argument == "random"):
            answer = [
                      "  %srandom CHOICE1 CHOICE2 CHOICE3" % self.command_prefix,
                      "  %srandom CHOICE1, CHOICE2, CHOICE3" % self.command_prefix,
                      "  %srandom CHOICE1 or CHOICE2 or CHOICE3" % self.command_prefix,
                      "Makes a random choice of the ones provided",
                      "  %srandom NUMBER1 - NUMBER2" % self.command_prefix,
                      "  %srandom NUMBER1 to NUMBER2" % self.command_prefix,
                      "Selects a random number between the two provided",
                      ]
        else:
            answer = [
                      "I understand:",
                      "  %squestion" % self.command_prefix,
                      "  %srandom" % self.command_prefix,
                      "  %sscale" % self.command_prefix,
                      "Type '%shelp command' to see how a command works" % self.command_prefix,
                      ]
        return answer
    
    def random(self, arguments):
        """
        Returns a random string or a random integer
        """
        digit_random = re.match("^(\d+) *(-|to){1} *(\d+)$", arguments)
        if(digit_random):
            # Random integer
            # random x-y | random x to y
            from_number = digit_random.group(1)
            to_number = digit_random.group(3)
            if(from_number <= to_number):
                return [str(random.randint(int(from_number), int(to_number))).strip()]
        else:
            # Random string
            # random str1 str2 str3 | random str1, str2, str3 | random str1 or str2 or str3
            divided_by_comma = re.match("^.+,.+$", arguments)
            divided_by_or = re.match("^.+ or .+$", arguments)
            if(divided_by_comma):
                arguments = arguments.split(",")
            elif(divided_by_or):
                arguments = arguments.split("or")
            else:
                arguments = arguments.split()
            result = random.randint(0,  len(arguments) - 1)
            return [arguments[result].strip()]
        raise Exception
    
    def scale(self, message):
        """
        Returns a random scale (in procent)
        """
        result = random.randint(0, 100)
        scale = "|"
        for i in range(10):
            if(result >= i*10 and result < i*10+10):
                scale += "X"
            elif result > i*10:
                scale += ">"
            else:
                scale += "-"
        scale += "|"
        if(message != ""):
            return ["%s: %s (%s%%)" % (message, scale, result)]
        else:
            return ["%s (%s%%)" % (scale, result)]  
    
    def question(self, question):
        """
        Returns a random positive or negative answer to a question
        """
        answers = [
                   "Yes",
                  "No",
                  "Yes!!!",
                  "No!!!",
                  "Of course",
                  "No way",
                  "Hell yeah!",
                  "Nah no fun",
                  ]
        result = random.randint(0,  len(answers) - 1)
        return [answers[result]]