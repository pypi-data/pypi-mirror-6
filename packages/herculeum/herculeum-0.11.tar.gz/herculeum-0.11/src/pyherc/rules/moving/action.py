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
    def __init__(self, character, new_location, new_level,
                 skip_creature_check, dying_rules):
        """
        Default constructor

        :param character: character moving
        :type character: Character
        :param new_location: location to move
        :type new_location: (int, int)
        :param new_level: level to move
        :type new_level: Level
        :param skip_creature_check: bypass checking if other creature blocks
        :type skip_creature_check: boolean
        :param dying_rules: rules for dying
        """
        super().__init__()

        self.character = character
        self.new_location = new_location
        self.new_level = new_level
        self.model = None
        self.skip_creature_check = skip_creature_check
        self.dying_rules = dying_rules

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

        traps = self.character.level.get_traps(self.character.location)

        for trap in traps:
            trap.on_enter(self.character)

        self.dying_rules.check_dying(self.character)

    @log_debug
    def is_legal(self):
        """
        Check if the move is possible to perform

        :returns: True if move is possible, false otherwise
        :rtype: Boolean
        """
        location_ok = True
        if self.new_level is not None:
            if not self.new_level.blocks_movement(self.new_location[0],
                                                  self.new_location[1]):
                if (not self.skip_creature_check and
                        self.new_level.get_creature_at(self.new_location)):
                    location_ok = False
            else:
                location_ok = False
        else:
            location_ok = False

        return location_ok

    def __str__(self):
        """
        String representation of this action
        """
        return '{0} at {1}:{2}'.format(self.character,
                                       self.new_location,
                                       self.new_level)


class WalkAction(MoveAction):
    """
    Action for walking
    """
    @log_info
    def execute(self):
        """
        Execute this move
        """
        super().execute()


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
                         new_level=None,
                         skip_creature_check=False,
                         dying_rules=None)

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


class SwitchPlacesAction():
    """
    Action for switching places with another creature

    .. versionadded:: 0.11
    """

    @log_debug
    def __init__(self, character, other_character, dying_rules):
        """
        Default constructor

        :param character: character to move
        :type character: Character
        :param other_character: other character to move
        :type other_character: Character
        """
        assert character is not None
        assert other_character is not None

        self.character = character
        self.other_character = other_character

        self.move_action_1 = WalkAction(self.character,
                                        self.other_character.location,
                                        self.other_character.level,
                                        True,
                                        dying_rules)

        self.move_action_2 = WalkAction(self.other_character,
                                        self.character.location,
                                        self.character.level,
                                        True,
                                        dying_rules)

    @log_info
    def execute(self):
        """
        Execute this move
        """
        if self.is_legal():
            self.move_action_1.execute()
            self.move_action_2.execute()
        else:
            self.character.add_to_tick(Duration.instant)

    @log_debug
    def is_legal(self):
        """
        Check if the move is possible to perform

        :returns: True if move is possible, false otherwise
        :rtype: Boolean
        """
        model = self.character.model

        if model.player in (self.character, self.other_character):
            return False
        else:
            return (self.move_action_1.is_legal() and
                    self.move_action_2.is_legal())
