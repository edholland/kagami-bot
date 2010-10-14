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


### Normal Settings ###

# The bots nick
nick = "kagami"

# The bots ident
ident = nick

# The real name of the bot
# Can be anything
real_name = "keiji.se"

# The irc server that the bot will join
host = "irc.quakenet.se"

# Port for irc server (normaly 6667)
port = 6667

# Channels to join at startup
# Separate multiple channels with ','
channels = "#kagami_test"

# Message that will be shown when the bot
# leaves the server
quit_message = "Bye Bye"

# Used before bot commands
# Can be changed so that it does not collide with other bots
command_prefix = "!!"


### Advanced Settings ###

# Time of silence (in seconds) before the server checks if the connection is still alive
# default: 600
server_timeout = 600

# How long the bot should wait (in seconds) before attempting a first connection retry
# default 15
connection_wait_timer_start = 15

# The wait time will grow by this multiplier
# default: 2
connection_wait_timer_multiplier = 2

# The time to wait will go up to a maximum of this value (in seconds)
# defailt: 900
connection_wait_timer_max = 900

