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
import random
import re
import time

class Konata(Plugin):
    
    def __init__(self, teh_bot):
        Plugin.__init__(self, teh_bot)
        self.command_pattern = "^:(.+)!.+ PRIVMSG (.+) :!*(.+)$"
        random.seed
        self.command_dictionary = {
                                   "jankenpon": self.jankenpon,
                                   "rockpaperscissors": self.jankenpon,
                                   }
        self.jankenpon = {
                          "Rock": ["Lizard", "Spock"],
                          "Paper": ["Rock", "Spock"],
                          "Scissors": ["Paper", "Lizard"],
                          "Spock": ["Rock", "Scissors"],
                          "Lizard": ["Paper", "Spock"],
                          }
        
    def do(self, line):
        Plugin.do(self, line)
        if self.sender.startswith("konata"):
            self.konata_speaks(line)
    
    def jankenpon (self, argument):
        self.last_jankenpon = random.choice(self.jankenpon.keys())
        self.time_of_last_jankenpon = time.time()
        self.send([self.last_jankenpon])
        
    def konata_speaks (self, line):
        pattern = "^:.+ PRIVMSG .+ :(.+)$"
        match = re.match(pattern, line)
        if match:
            says = match.group(1)
            question = "^.*(Yes|No).*$"
            question_match = re.match(question, says)
            scale = "^.*\|(X|=){10}\|.*$"
            scale_match = re.match(scale, says)
            jankenpon = "^.*(Rock|Paper|Scissors|Spock|Lizard).*$"
            jankenpon_match = re.match(jankenpon, says)
            if question_match or scale_match:
                answers = [
                       "Don't listen to her!",
                       "Doh",
                       "Don't feed the troll!",
                       "Rly? :p",
                       ]
                if random.randint(0,1):
                    time.sleep(1)
                    self.send([random.choice(answers)])
            elif (jankenpon_match and time.time() - self.time_of_last_jankenpon < 5):
                konatas_choice = jankenpon_match.group(1)
                konata_beats = self.jankenpon[konatas_choice]
                if konatas_choice == self.last_jankenpon:
                    self.send([random.choice([":/","Stop mimic my moves!","..."])])
                elif self.last_jankenpon in konata_beats:
                    self.send([random.choice([":(",";(","No","Cheater"])])
                else:
                    self.send([random.choice(["Ha!","For the win!","Peace of cake"])])
                
        