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
from time import strftime
from collections import deque
import re

class Log(Plugin):
    """
    Plugin that stores data into a logfile
    """
    
    def __init__(self,teh_bot):
        Plugin.__init__(self,teh_bot)
        self.last_urls = self.restore_object_from_file("last_urls")
        if not self.last_urls:
            self.last_urls = deque(["","","","","","","",""])
        self.last_messages = self.restore_object_from_file("last_messages")
        if not self.last_messages:
            self.last_messages = deque(["","","","","","","",""])
        self.command_dictionary_only_priv_msg_to_bot = {
                                                        "messages": self.messages,
                                                        "urls": self.urls,
                                                        }
        self.command_info_only_priv_msg_to_bot = {
                                                  "messages": [
                                                               "  %smessages" % self.teh_bot.command_prefix,
                                                               "Shows the last messages the bot have seen",
                                                               ],
                                                  "urls": [
                                                               "  %surls" % self.teh_bot.command_prefix,
                                                               "Shows the last urls the bot have seen",
                                                               ],
                                                   }
    def do(self,line):
        self.write_to_logfile(line)
        return Plugin.do(self, line)
    
    def write_to_logfile(self,line):
        """
        Writes stuff sent on the IRC server down into log files
        """
        current_time = strftime("%b %d %H:%M:%S")
        privmsg_match = re.match(":(.+)!.+ PRIVMSG (#[^ ]+) :(.*)$", line, re.IGNORECASE)
        if privmsg_match:
            sender = privmsg_match.group(1)
            channel= privmsg_match.group(2)
            message = privmsg_match.group(3)
            log_message = "%s %s: %s\n" % (current_time, sender, message)
            filename = "%s.messages" % channel
            self.append_to_file(log_message, filename)
            log_message = "%s %s: %s" % (channel, sender, message)
            self.last_messages.appendleft(log_message)
            self.last_messages.pop()
            self.save_object_to_file(self.last_messages, "last_messages")
            url_match = re.match(".*(http(s)?:\/\/[^ ]+)($| .*)", message, re.IGNORECASE)
            if url_match:
                url = url_match.group(1)
                log_message = "%s %s: %s\n" % (current_time, sender, url)
                filename = "%s.urls" % channel
                self.append_to_file(log_message, filename)
                log_message = "%s %s: %s" % (channel, sender, url)
                self.last_urls.appendleft(log_message)
                self.last_urls.pop()
                self.save_object_to_file(self.last_urls, "last_urls")
        log_message = "%s: %s\n" % (current_time, line)
        filename = "kagami"
        self.append_to_file(log_message, filename)
        
    def urls (self, arguments):
        temp = self.last_urls
        temp.reverse()
        self.send(temp)
        
    def messages (self, arguments):
        temp = self.last_messages
        temp.reverse()
        self.send(temp)