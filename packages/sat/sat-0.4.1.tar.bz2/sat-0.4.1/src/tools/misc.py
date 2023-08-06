#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Misc usefull classes"""

from sat.core.i18n import _
import sys
from logging import debug, warning


class TriggerException(Exception):
    pass


class SkipOtherTriggers(Exception):
    """ Exception to raise if normal behaviour must be followed instead of
        following triggers list """
    pass


class TriggerManager(object):
    """This class manage triggers: code which interact to change the behaviour
    of SàT"""

    MIN_PRIORITY = float('-inf')
    MAX_PRIORITY = float('+inf')

    def __init__(self):
        self.__triggers = {}

    def add(self, point_name, callback, priority=0):
        """Add a trigger to a point
        @param point_name: name of the point when the trigger should be run
        @param callback: method to call at the trigger point
        @param priority: callback will be called in priority order, biggest
        first
        """
        if point_name not in self.__triggers:
            self.__triggers[point_name] = []
        if priority != 0 and priority in [trigger_tuple[0] for trigger_tuple in self.__triggers[point_name]]:
            if priority in (self.MIN_PRIORITY, self.MAX_PRIORITY):
                warning(_("There is already a bound priority [%s]") % point_name)
            else:
                debug(_("There is already a trigger with the same priority [%s]") % point_name)
        self.__triggers[point_name].append((priority, callback))
        self.__triggers[point_name].sort(key=lambda trigger_tuple:
                                         trigger_tuple[0], reverse=True)

    def remove(self, point_name, callback):
        """Remove a trigger from a point
        @param point_name: name of the point when the trigger should be run
        @param callback: method to remove, must exists in the trigger point"""
        for trigger_tuple in self.__triggers[point_name]:
            if trigger_tuple[1] == callback:
                self.__triggers[point_name].remove(trigger_tuple)
                return
        raise TriggerException("Trying to remove an unexisting trigger")

    def point(self, point_name, *args, **kwargs):
        """This put a trigger point
        All the trigger for that point will be run
        @param point_name: name of the trigger point
        @return: True if the action must be continued, False else"""
        if point_name not in self.__triggers:
            return True

        for priority,trigger in self.__triggers[point_name]:
            try:
                if not trigger(*args, **kwargs):
                    return False
            except SkipOtherTriggers:
                break
        return True
