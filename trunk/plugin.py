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
import pickle
import os

class Plugin(object):
    """
    The base class that new plugins should inherit from
    """

    def __init__(self, teh_bot):
        """
        Plugins should add there command-functions to self.command_dictionary
        """
        self.teh_bot = teh_bot
        self.command_dictionary = {}
        self.command_info = {}
        self.sender = ""
        self.channel = ""
        self.command_pattern = "^:(.+)!.+ PRIVMSG (.+) :%s(.+)$" % teh_bot.command_prefix
        if not os.path.isdir("plugins/save"):
            os.mkdir("plugins/save/")
    
    def do(self, line):
        """
        Looks in the command dictionary after a function matching the command.
        The function should only return True if the plugin sent a message to a channel/user.
        """
        match = re.match(self.command_pattern, line)
        if match:
            self.sender, self.channel, command_line = match.groups()
            split_command_line = command_line.split()
            command = split_command_line[0]
            if(command in self.command_dictionary):
                self.command_dictionary[command](command_line[len(command):].strip())
                return True
        return False
    
    def send (self, message):
        """
        Sends message back to channel or user
        """
        if self.channel == self.teh_bot.nick:
            self.channel = self.sender
        self.teh_bot.send_message_without_flood(self.channel, message)
        
    def send_raw_irc_message (self, message):
        """
        Sends a raw IRC message to the IRC server
        """
        self.teh_bot.socket.send(message)
    
    def save_object_to_file(self, object, filename):
        plugin_filename = self.get_plugin_filename()
        filepath = "plugins/save/%s.%s.obj" % (plugin_filename, filename)
        file = open(filepath,"w")
        pickle.dump(object, file)
        file.close()
    
    def restore_object_from_file(self, filename):
        plugin_filename = self.get_plugin_filename()
        filepath = "plugins/save/%s.%s.obj" % (plugin_filename, filename)
        try:
            file = open(filepath,"r")
            object = pickle.load(file)
            file.close()
            return object
        except:
            return False
    
    def get_plugin_filename(self):
        name = ""
        string = self.__str__()
        str_pattern = "^.+\.(.+)\..* .*$"
        str_match = re.match(str_pattern, string)
        if str_match:
            name = str_match.group(1)
        return name
    
    def message_to_bot(self,line):
        message_to_bot_pattern = "^:(.+)!.+ PRIVMSG %s :.+$" % self.teh_bot.nick
        message_to_bot = re.match(message_to_bot_pattern, line)
        if message_to_bot:
            self.sender = message_to_bot.group(1)
            self.channel = self.teh_bot.nick
        return message_to_bot
    
    def is_command(self,line):
        command_pattern = "^:(.+)!.+ PRIVMSG (.+) :%s.+$" % self.teh_bot.command_prefix
        command = re.match(command_pattern, line)
        if command:
            self.sender, self.channel = command.groups()
        return command