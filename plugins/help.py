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

class Help(Plugin):

    def __init__(self, teh_bot):
        Plugin.__init__(self, teh_bot)
        self.command_dictionary_only_priv_msg_to_bot = {
                                                        "help": self.help,
                                                        }
        self.command_info_only_priv_msg_to_bot = {
                                                  "help": [
                                                           "  %shelp" % self.command_prefix,
                                                           "Shows information about the commands that the bot understands",
                                                           ],
                             }
        
    def do(self,line):
        if Plugin.do(self, line):
            return True
        elif self.message_to_bot(line) and not self.is_command(line):
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
        command_info_only_priv_msg_to_bot = self.teh_bot.command_info_only_priv_msg_to_bot
        if argument in command_info:
            self.send(command_info[argument])
        elif argument in command_info_only_priv_msg_to_bot:
            self.send(command_info_only_priv_msg_to_bot[argument])
        elif len(argument) == 0:
            commands = command_info.keys()
            priv_commands = command_info_only_priv_msg_to_bot.keys()
            priv_commands = map(self.private_command_format, priv_commands)
            commands.extend(priv_commands)
            commands.sort()
            answer = ["I understand:"]
            for command in commands:
                command_string = "  %s%s" % (self.command_prefix, command)
                answer.append(command_string)
            answer.append("(*Command does only work in a private chat with the bot)")
            answer.append("Type '%shelp COMMAND' to see how a command works" % self.command_prefix)
            self.send(answer)
            
    def private_command_format(self,command):
        """
        Adds a * after commands only working in a private chat with the bot
        """
        return "%s*" % command