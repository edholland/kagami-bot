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

class Stats(Plugin):
    """
    Stores and shows user stats
    """

    def __init__(self, teh_bot):
        Plugin.__init__(self, teh_bot)
        self.command_prefix = self.teh_bot.command_prefix
        self.command_dictionary = {
                                   "stat": self.stat,
                                   }
        self.command_info = {
                             "stat": [
                                      "  %sstat USER" % self.teh_bot.command_prefix,
                                      "Shows stats about the user",
                                      ],
                             }
        self.user_data = self.restore_object_from_file("user_data")
        if not self.user_data:
            self.user_data = {}
    
    def do (self, line):
        self.store_data(line)
        return Plugin.do(self, line)
    
    def store_data (self, line):
        """
        Stores/Updates data for the user who sent the current line
        """
        privmsg_pattern = "^:(.+)!.+ PRIVMSG (.+) :(.+)$"
        privmsg_match = re.match(privmsg_pattern, line)
        if privmsg_match:
            sender, channel, message = privmsg_match.groups()
            lines = 1
            words = len(message.split())
            chars = len(message.replace(" ",""))
            urls = 0
            url_pattern = ".*(HTTP|http).*"
            url_match = re.match(url_pattern, message)
            if url_match:
                urls = 1
            if sender in self.user_data:
                old_data = self.user_data[sender]
                lines = old_data[0] + lines
                words = old_data[1] + words
                chars = old_data[2] + chars
                urls = old_data[3] + urls
            self.user_data.update({sender: [lines,words,chars,urls]})
            self.save_object_to_file(self.user_data, "user_data")
        
    def stat(self,argument):
        """
        Shows stats for a user
        """
        if len(argument) > 0:
            user = argument
        else:
            user = self.sender
        if user in self.user_data:
            lines, words, chars, urls = self.user_data[user]
            message = [
                       "%s has posted %s lines consisting of %s words and %s characters." % (user, lines, words, chars),
                       "Of all those meaningless lines %s did included a URL" % urls,
                       ]
            self.send(message)
        else:
            self.send(["Haven't got any fun data for that user yet"])