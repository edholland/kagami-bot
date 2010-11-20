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
from datetime import date

class Special_days(Plugin):
    """
    A plugin that announce the beginning of special days
    """

    def __init__(self, teh_bot):
        Plugin.__init__(self, teh_bot)
        self.last_announced_date = date.today()
        
    def do_often(self):
        """
        Sends day announcements stored in special_days.txt in the plugin config folder
        """
        cur_date = date.today()
        if cur_date != self.last_announced_date:
            filepath = "plugins/config/special_days.txt"
            file = open(filepath,"r")
            self.days = file.readlines()
            file.close()
            cur_day_name = cur_date.strftime("%a").lower()
            cur_day = int(cur_date.day)
            cur_month = int(cur_date.month)
            for line in self.days:
                pattern1 = "^([0-9]+)\/([0-9]+):(.+)$"
                pattern2 = "^([a-z]{3}) ([0-9]+)\/([0-9]+)-([0-9]+)\/([0-9]+):(.+)$"
                pattern1_match = re.match(pattern1, line)
                pattern2_match = re.match(pattern2, line, re.IGNORECASE)
                if pattern1_match:
                    day, month, message = pattern1_match.groups()
                    if int(day) == cur_day and int(month) == cur_month:
                        self.send(message)
                        pass
                elif pattern2_match:
                    day_name, day_from, month_from, day_to, month_to, message = pattern2_match.groups()
                    day_from = int(day_from)
                    month_from = int(month_from)
                    day_to = int(day_to)
                    month_to = int(month_to)
                    if (cur_day_name == day_name.lower()
                        and(
                            (cur_month > month_from and cur_month < month_to)
                            or (cur_month == month_from and cur_month == month_to
                                and cur_day >= day_from and cur_day <= day_to)
                            or (cur_month == month_from and cur_month != month_to
                                and cur_day >= day_from)
                            or (cur_month != month_from and cur_month == month_to
                                and cur_day <= day_to)
                            )
                        ):
                        self.send(message)
            self.last_announced_date = date.today()