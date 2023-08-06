# -*- coding: utf-8 -*-

#   Copyright 2010-2014 Tuukka Turto
#
#   This file is part of pyherc.
#
#   pyherc is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   pyherc is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with pyherc.  If not, see <http://www.gnu.org/licenses/>.

"""
Module defining classes related to Move
"""
from pyherc.events import MoveEvent
from pyherc.aspects import log_debug, log_info
from pyherc.data.model import ESCAPED_DUNGEON
from pyherc.data.geometry import find_direction
from pyherc.data.constants import Duration


class MoveAction():
    """
    Action for moving
    """
    @log_debug
    def __init__(self, character, new_location, new_level=None):
        """
        Default constructor

        :param character: character moving
        :type character: Character
        :param new_location: location to move
        :type new_location: (int, int)
        :param new_level: level to move
        :type new_level: Level
        """
        super().__init__()

        self.character = character
        self.new_location = new_location
        self.new_level = new_level
        self.model = None

    @log_info
    def execute(self):
        """
        Executes this Move
        """
        if self.is_legal():

            affected_tiles = [self.character.location,
                              self.new_location]

            old_location = self.character.location
            self.character.location = self.new_location
            direction = find_direction(old_location, self.new_location)

            if self.new_level is not None:
                if self.character.level != self.new_level:
                    self.character.level.remove_creature(self.character)
                    self.character.level = self.new_level
                    self.new_level.add_creature(self.character,
                                                self.new_location)

            armour = self.character.inventory.armour
            if armour:
                speed_modifier = armour.armour_data.speed_modifier
            else:
                speed_modifier = 1

            self.character.add_to_tick(Duration.fast / speed_modifier)

            self.character.raise_event(MoveEvent(
                mover=self.character,
                old_location=old_location,
                direction=direction,
                affected_tiles=affected_tiles))

        else:
            self.character.add_to_tick(Duration.instant)

    @log_debug
    def is_legal(self):
        """
        Check if the move is possible to perform

        :returns: True if move is possible, false otherwise
        :rtype: Boolean
        """
        location_ok = False
        if self.new_level is not None:
            if not self.new_level.blocks_movement(self.new_location[0],
                                                  self.new_location[1]):
                #check for other creatures and such
                location_ok = True
                creatures = self.new_level.creatures
                for creature in creatures:
                    if creature.location == self.new_location:
                        location_ok = False
            else:
                location_ok = False
        else:
            pass

        return location_ok


class WalkAction(MoveAction):
    """
    Action for walking
    """
    @log_info
    def execute(self):
        """
        Execute this move
        """
        super().execute(self)


class EscapeAction(MoveAction):
    """
    Action for escaping the dungeon

    .. versionadded:: 0.8
    """
    @log_debug
    def __init__(self, character):
        """
        Default constructor
        """
        super().__init__(character=character,
                         new_location=None,
                         new_level=None)

    @log_info
    def execute(self):
        """
        Execute this move
        """
        model = self.character.model
        model.end_condition = ESCAPED_DUNGEON

    @log_debug
    def is_legal(self):
        """
        Check if the move is possible to perform

        :returns: True if move is possible, false otherwise
        :rtype: Boolean
        """
        model = self.character.model

        if model.player == self.character:
            return True
        else:
            return False
