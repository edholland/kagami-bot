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

from plugin import Plugin
import re

class Help(Plugin):

    def __init__(self, teh_bot):
        Plugin.__init__(self, teh_bot)
        self.command_dictionary = {
                                   "help": self.help,
                                   }
        
    def do(self,line):
        message_to_bot_pattern = "^:(.+)!.+ PRIVMSG %s :.+$" % self.teh_bot.nick
        message_to_bot = re.match(message_to_bot_pattern, line)
        if message_to_bot:
            #Only answer to private message sent directly to the bot
            self.channel = self.teh_bot.nick
            self.sender = message_to_bot.group(1)
            if not Plugin.do(self, line):
                self.greeting("")
            return True
        else:
            return False
    
    def greeting (self, argument):
        """
        Greets the user and tells him/her how to get help on the bot
        """
        greeting = [
                    "Hai!",
                    "I'm a open source bot written in Python ( http://code.google.com/p/kagami-bot/ )",
                    "Type '%shelp' to see what commands I understand" % self.teh_bot.command_prefix,
                    ]
        self.send(greeting)
    
    def help(self, argument):
        """
        Sends list of all commands or info on a specific command
        """
        command_info = self.teh_bot.command_info
        command_prefix = self.teh_bot.command_prefix
        if argument in command_info:
            self.send(command_info[argument])
        elif len(argument) == 0:
            commands = command_info.keys()
            commands.sort()
            answer = ["I understand:"]
            for command in commands:
                command_string = "  %s%s" % (command_prefix, command)
                answer.append(command_string)
            answer.append("Type '%shelp COMMAND' to see how a command works" % command_prefix)
            self.send(answer)