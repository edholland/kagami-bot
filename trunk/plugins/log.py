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
import re

class Log(Plugin):
    """
    Plugin that stores data into a logfile
    """
    
    def __init__(self,teh_bot):
        Plugin.__init__(self,teh_bot)
        
    def do(self,line):
        self.write_to_logfile(line)
        return Plugin.do(self, line)
    
    def write_to_logfile(self,line):
        """
        Writes stuff sent on the IRC server down into log files
        """
        current_time = strftime("%b %d %H:%M:%S")
        privmsg_match = re.match(":(.+)!.+ PRIVMSG (#.+) :(.*)$", line, re.IGNORECASE)
        if privmsg_match:
            sender = privmsg_match.group(1)
            channel= privmsg_match.group(2)
            message = privmsg_match.group(3)
            log_message = "%s %s: %s\n" % (current_time, sender, message)
            filename = "%s.messages" % channel
            self.append_to_file(log_message, filename)
            url_match = re.match(".*(http(s)?:\/\/[^ ]+)($| .*)", message, re.IGNORECASE)
            if url_match:
                url = url_match.group(1)
                log_message = "%s %s: %s\n" % (current_time, sender, url)
                filename = "%s.urls" % channel
                self.append_to_file(log_message, filename)
        log_message = "%s: %s\n" % (current_time, line)
        filename = "kagami"
        self.append_to_file(log_message, filename)