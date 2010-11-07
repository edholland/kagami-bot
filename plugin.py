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

import re

class Plugin(object):

    def __init__(self, teh_bot):
        self.teh_bot = teh_bot
        self.command_dictionary = {}
        self.command_pattern = "^:(.+)!.+ PRIVMSG (.+) :%s(.+)$" % teh_bot.command_prefix
    
    def do(self, line):
        match = re.match(self.command_pattern, line)
        if match:
            self.sender, self.channel, command_line = match.groups()
            split_command_line = command_line.split()
            command = split_command_line[0]
            if(command in self.command_dictionary):
                self.command_dictionary[command](command_line[len(command):].strip())
    
    def send (self, message):
        if self.channel == self.teh_bot.nick:
            self.channel = self.sender
        if self.teh_bot.flood_safe():
            self.teh_bot.send_message(self.channel, message)