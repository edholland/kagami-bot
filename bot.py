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

import socket
import time
import ssl
import os
import re
from collections import deque
from ConfigParser import ConfigParser

class Bot(object):

    def __init__(self, setup_filename):
        self.load_setup_file(setup_filename)
        self.command_info = {}
        self.command_info_only_priv_msg_to_bot = {}
        self.load_plugins(self.plugins_to_load)
        self.connected = False
        self.time_of_last_messages_sent_to_bot = deque([0,0,0,0])
        self.time_of_last_sent_line = 0
        self.wait_before_sending_line = 0.0
        self.socket_timeout = 120
    
    def load_setup_file(self,setup_filename):
        """
        Loads user settings stored in the setup file
        """
        default_values = {
                          "port": "6667",
                          "channels": "#kagami_test",
                          "nick": "kagami",
                          "ident": "kagami",
                          "real_name": "kagami",
                          "quit_message": "",
                          "command_prefix": "!!",
                          "server_timeout": "600",
                          "connection_wait_timer_start": "15",
                          "connection_wait_timer_max": "900",
                          "connection_wait_timer_multiplier": "2",
                          "plugins": "all",
                          "ssl": "no"
                          }
        config = ConfigParser(default_values)
        config.read(setup_filename)
        try:
            self.host = config.get("server", "host")
        except:
            print "Error: Could not find a host address in %s" % setup_filename
            exit()
        self.port = config.getint("server", "port")
        self.ssl = config.getboolean("server", "ssl")
        self.channels = config.get("server", "channels")
        self.nick = config.get("bot", "nick")
        self.nick_original = self.nick
        self.ident = config.get("bot", "ident")
        self.real_name = config.get("bot", "real_name")
        self.quit_message = config.get("bot", "quit_message")
        self.command_prefix = config.get("bot", "command_prefix")
        self.server_timeout = config.getint("server", "server_timeout")
        self.connection_wait_timer_start = config.getint("server", "connection_wait_timer_start")
        self.connection_wait_timer_max = config.getint("server", "connection_wait_timer_max")
        self.connection_wait_timer_multiplier = config.getint("server", "connection_wait_timer_multiplier")
        self.plugins_to_load = config.get("bot", "plugins").split(",")
    
    def load_plugins(self, plugins_to_load):
        """
        Imports and loads plugins
        Gets info about commands from the plugins and stores it in command_info
        """
        if not os.path.isdir("plugins"):
            os.mkdir("plugins")
        if "all" in plugins_to_load:
            plugins_to_load = self.get_names_of_all_plugins()
        self.plugins = []
        for plugin in plugins_to_load:
            plugin = plugin.strip().lower()
            string_import = "import plugins.%s" % plugin
            string_load_plugin = "self.plugins.append(plugins.%s.%s(self))" % (plugin, plugin.capitalize())
            try:
                exec string_import
                exec string_load_plugin
            except:
                print "Failed to load plugin: %s" % plugin
        for plugin in self.plugins:
            self.command_info.update(plugin.command_info)
            self.command_info_only_priv_msg_to_bot.update(plugin.command_info_only_priv_msg_to_bot)
            
    def get_names_of_all_plugins(self):
        """
        Returns a list of names for all plugins in the plugins folder
        """
        all_plugins = []
        plugin_pattern = "^([^_].*)\.py$"
        plugin_folder = os.listdir("plugins")
        for file in plugin_folder:
            plugin_match = re.match(plugin_pattern, file, re.IGNORECASE)
            if plugin_match:
                plugin = plugin_match.group(1)
                all_plugins.append(plugin)
        return all_plugins
        
    def connect(self):
        """
        Connects and registers with the IRC Server.
        """
        self.socket = socket.socket()
        if self.ssl:
            self.socket = ssl.SSLSocket(self.socket)
        self.socket.settimeout(self.socket_timeout)
        wait_time = self.connection_wait_timer_start
        while self.connected == False:
            try:
                self.socket.connect((self.host, self.port))
                self.connected = True
                print "Connected to %s on port %s" % (self.host, str(self.port))
            except:
                print "Failed to connect to %s on port %s" % (self.host, str(self.port))
                print "Reconnecting in %s seconds" % wait_time
                time.sleep(wait_time)
                if(wait_time * self.connection_wait_timer_multiplier < self.connection_wait_timer_max):
                    wait_time = wait_time * self.connection_wait_timer_multiplier
                elif(wait_time < self.connection_wait_timer_max):
                    wait_time = self.connection_wait_timer_max
        # Register on server
        self.socket.send("NICK %s\r\n" % self.nick)
        self.socket.send("USER %s %s something :%s\r\n" % (self.ident, self.host, self.real_name))
        self.last_time_sent_nick = time.time()
        # Listen for replies from the server
        self.listen()
    
    def listen(self):
        """
        Starts listen to messages from the server
        """
        readbuffer=""
        disconnect = False
        number_of_socket_timeouts = 0
        while self.connected:
            try:
                for plugin in self.plugins:
                    plugin.do_often()
                readbuffer += self.socket.recv(1024)
                number_of_socket_timeouts = 0 # Resets socket timeouts if it receives anything
                lines = readbuffer.split("\n")
                readbuffer = lines.pop()
                for line in lines:  
                    line = line.strip()
                    sline = line.split()
                    self.print_line(line)  
                    if(sline[0]=="PING"):
                        # The PING PONG game
                        self.socket.send("PONG %s\r\n" % sline[1])    
                    elif(sline[1]=="001"):
                        # 001: Sent to all clients once a connection has been established
                        #      and the user has successfully registered.
                        #      Now the bot can join it's channels
                        self.socket.send("JOIN :%s\r\n" % self.channels)
                    elif(sline[1]=="433"):
                        # 433: Nickname is already in use
                        self.nick += "_"
                        self.socket.send("NICK %s\r\n" % self.nick)
                    else:
                        # Send the line to all loaded plugins
                        for plugin in self.plugins:
                            plugin.do(line)
                    if(self.nick != self.nick_original and
                         time.time() - self.last_time_sent_nick > 1800):
                            # Try to get back original nick if it was used by another user when connecting
                            self.nick = self.nick_original
                            self.socket.send("NICK %s\r\n" % self.nick)
                            self.last_time_sent_nick = time.time()
            except KeyboardInterrupt:
                # If the bot program receives a keyboard interrupt
                # it still tries to leave the server in a correct way.
                disconnect = True
                self.connected = False
            except socket.timeout:
                number_of_socket_timeouts += 1
                if (number_of_socket_timeouts * self.socket_timeout >= self.server_timeout + self.socket_timeout):
                    self.connected = False
                    print "Connection timeout"
                elif (number_of_socket_timeouts * self.socket_timeout >= self.server_timeout):
                    self.socket.send("PING %s\r\n" % self.host)
            except socket.error:
                self.connected = False
                print "Connection failed"
        if disconnect:
            self.disconnect()
        else:
            self.reconnect()
    
    def reconnect(self):
        """
        Closes the socket and then tries to reconnect.
        """
        self.socket.close()
        self.nick = self.nick_original
        time.sleep(5)
        self.connect()
        
    def disconnect(self):
        """
        Sends a QUIT message and then leaves the server.
        """
        self.socket.send("QUIT :%s\r\n" % self.quit_message)
        time.sleep(1)
        self.socket.close()
        
    def print_line(self, line):
        """
        Prints an IRC message/line to the console.
        """
        sline = line.split()
        if(sline[0] != "PING" and sline[1] != "JOIN" and sline[1] != "QUIT"):
            print "%s - %s" % (time.strftime("%H:%M", time.localtime()), line)
    
    def send_message(self, to, messages):
        """
        Sends a message to a user or a channel
        """
        if not (type(messages) == type(list()) or type(messages) == type(deque())):
            messages = [messages]
        if len(to) > 0:
            if((self.time_of_last_sent_line - time.time()) < 10):
                # Resets wait time if some time has passed since last sent message
                self.wait_before_sending_line = 0.0
            for line in messages:
                print line
                line = line.rstrip()
                if len(line) > 0:
                    # Sleep for a short time to prevent flooding
                    time.sleep(self.wait_before_sending_line)
                    self.wait_before_sending_line += 0.2
                    if len(line) > 0:
                        self.socket.send("PRIVMSG %s :%s\r\n" % (to, line))
            self.time_of_last_sent_line = time.time()
    
    def send_message_without_flood(self, to, messages):
        if self.flood_safe():
            self.send_message(to, messages)
    
    def flood_safe(self):
        """
        Checks so that the bot have not received too many messages/commands
        and risk flooding the channel with responses.
        """
        current_time = time.time()
        self.time_of_last_messages_sent_to_bot.appendleft(current_time)
        old_time = self.time_of_last_messages_sent_to_bot.pop()
        if((current_time - old_time) < 15):
            return False
        else:
            return True