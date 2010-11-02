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
from collections import deque
from ConfigParser import ConfigParser
import re
import time

class Bot(object):

    def __init__(self, setup_filename, command_class):
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
                          }
        config = ConfigParser(default_values)
        config.read(setup_filename)  
        try:
            self.host = config.get("server", "host")
        except:
            print "Error: Could not find a host address in %s" % setup_filename
            exit()
        self.port = config.getint("server", "port")
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
        self.commands = command_class(self.command_prefix)
        self.connected = False
        self.time_of_last_messages_sent_to_bot = deque([0,0,0,0])
        self.time_of_last_sent_line = 0
        self.wait_before_sending_line = 0.0
        self.socket_timeout = 120
        
    def connect(self):
        """
        Connects and registers with the IRC Server.
        """
        self.socket = socket.socket()
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
        # Listen for replies from the server
        self.listen()
    
    def listen(self):
        """
        Starts listen to messages from the server
        """
        readbuffer=""
        disconnect = False
        number_of_socket_timeouts = 0
        old_bot_leave = "^:%s!.* QUIT .*$" % self.nick_original
        while self.connected:
            try:
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
                    elif(sline[1]=="PRIVMSG"):
                        # A message has been sent somewhere on the server
                        self.privmsg(line)
                    elif(self.nick != self.nick_original and
                         re.match(old_bot_leave, line)):
                            # Try to get back nick when a user with that nick quits
                            # A way to Fix wrong nick after a disconnection where the ghost
                            # from last connection is still around
                            self.nick = self.nick_original
                            self.socket.send("NICK %s\r\n" % self.nick)
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
        if((self.time_of_last_sent_line - time.time()) < 10):
            self.wait_before_sending_line = 0.0
        for line in messages:
            line = line.rstrip()
            # Sleep for a short time to prevent flooding
            time.sleep(self.wait_before_sending_line)
            self.wait_before_sending_line += 0.2
            self.socket.send("PRIVMSG %s :%s\r\n" % (to, line))
        self.time_of_last_sent_line = time.time()
        
    def privmsg(self, line):
        """
        Parse messages sent on the server and decides
        if some action is required from the bot
        """
        command_pattern = "^:(.+)!.+ PRIVMSG (.+) :%s(.+)$" % self.command_prefix
        command_match = re.match(command_pattern, line)
        message_to_bot_pattern = "^:(.+)!.+ PRIVMSG %s :(.+)$" % self.nick
        message_to_bot_match = re.match(message_to_bot_pattern, line)
        if(command_match):
            # The message is a command for the bot
            sender, receiver, command = command_match.groups()
            try:
                answer = self.commands.do(command)
                if(self.flood_safe()):
                    if(receiver == self.nick or command.startswith("help")):
                        self.send_message(sender, answer)
                    else:
                        self.send_message(receiver, answer)
            except:
                print "Bad command syntax"
        elif(message_to_bot_match):
            # A message (that is not a command) has been sent to the bot)
            sender, message = message_to_bot_match.groups()
            answer = [
                      "Hai!",
                      "I'm a open source bot written in Python ( http://code.google.com/p/kagami-bot/ )",
                      "Type '%shelp' to see what commands I understand" % self.command_prefix,
                      ]
            if(self.flood_safe()):
                self.send_message(sender, answer)
    
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