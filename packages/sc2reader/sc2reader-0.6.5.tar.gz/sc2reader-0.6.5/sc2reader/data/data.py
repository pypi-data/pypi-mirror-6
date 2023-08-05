# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

try:
    from collections import OrderedDict
except ImportError as e:
    from ordereddict import OrderedDict

from sc2reader.log_utils import loggable


class Unit(object):
    """Represents an in-game unit."""
    def __init__(self, unit_id):
        #: A reference to the player that currently owns this unit. Only available for 2.0.8+ replays.
        self.owner = None

        #: The frame the unit was started at. Only available for 2.0.8+ replays.
        #: Specifically, it is the frame the :class:`~sc2reader.events.tracker.UnitInitEvent` is received. For units
        #: that are born and not initiated this will be the same as :attr:`finished_at`.
        self.started_at = None

        #: The frame the unit was finished at. Only available for 2.0.8+ replays.
        #: Specifically, it is the frame that the :class:`~sc2reader.events.tracker.UnitDoneEvent` is received. For units
        #: that are born and not initiated this will be the frame that the :class:`~sc2reader.events.tracker.UnitBornEvent`
        #: is received.
        self.finished_at = None

        #: The frame the unit died at. Only available for 2.0.8+ replays.
        #: Specifically, it is the frame that the :class:`~sc2reader.events.tracker.UnitDiedEvent` is received.
        self.died_at = None

        #: A reference to the player that killed this unit. Only available for 2.0.8+ replays.
        #: This value is not set if the killer is unknown or not relevant (morphed into a
        #: different unit or used to create a building, etc)
        self.killed_by = None

        #: The unique in-game id for this unit. The id can sometimes be zero because
        #: TargetUnitCommandEvents will create a new unit with id zero when a unit
        #: behind the fog of war is targetted.
        self.id = unit_id

        #: A reference to the unit type this unit is current in.
        #: e.g. SeigeTank is a different type than SeigeTankSeiged
        self._type_class = None

        #: A history of all the unit types this unit has had stored
        #: in order by frame the type was acquired.
        self.type_history = OrderedDict()

        #: Is this unit type a hallucinated one?
        self.hallucinated = False

        self.flags = 0

    def apply_flags(self, flags):
        self.flags = flags
        self.hallucinated = flags & 2 == 2

    def set_type(self, unit_type, frame):
        self._type_class = unit_type
        self.type_history[frame] = unit_type

    def is_type(self, unit_type, strict=True):
        if strict:
            if isinstance(unit_type, int):
                if self._type_class:
                    return unit_type == self._type_class.id
                else:
                    return unit_type == 0
            elif isinstance(unit_type, Unit):
                return self._type_class == unit_type
            else:
                if self._type_class:
                    return unit_type == self._type_class.str_id
                else:
                    return unit_type is None
        else:
            if isinstance(unit_type, int):
                if self._type_class:
                    return unit_type in [utype.id for utype in self.type_history.values()]
                else:
                    return unit_type == 0
            elif isinstance(unit_type, Unit):
                return unit_type in self.type_history.values()
            else:
                if self._type_class:
                    return unit_type in [utype.str_id for utype in self.type_history.values()]
                else:
                    return unit_type is None

    @property
    def name(self):
        """The name of the unit type currently active. None if no type is assigned"""
        return self._type_class.name if self._type_class else None

    @property
    def title(self):
        return self._type_class.title if self._type_class else None

    @property
    def type(self):
        """ The internal type id of the current unit type of this unit. None if no type is assigned"""
        return self._type_class.id if self._type_class else None

    @property
    def race(self):
        """ The race of this unit. One of Terran, Protoss, Zerg, Neutral, or None"""
        return self._type_class.race if self._type_class else None

    @property
    def minerals(self):
        """ The mineral cost of the unit. None if no type is assigned"""
        return self._type_class.minerals if self._type_class else None

    @property
    def vespene(self):
        """ The vespene cost of the unit. None if no type is assigned"""
        return self._type_class.vespene if self._type_class else None

    @property
    def supply(self):
        """ The supply used by this unit. Negative for supply providers. None if no type is assigned """
        return self._type_class.supply if self._type_class else None

    @property
    def is_worker(self):
        """ Boolean flagging units as worker units. SCV, MULE, Drone, Probe """
        return self._type_class.is_worker if self._type_class else False

    @property
    def is_building(self):
        """ Boolean flagging units as buildings. """
        return self._type_class.is_building if self._type_class else False

    @property
    def is_army(self):
        """ Boolean flagging units as army units. """
        return self._type_class.is_army if self._type_class else False

    def __str__(self):
        return "{0} [{1:X}]".format(self.name, self.id)

    def __cmp__(self, other):
        return cmp(self.id, other.id)

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return str(self)


class UnitType(object):
    """ Represents an in game unit type """
    def __init__(self, **attributes):
        self.__dict__.update(**attributes)
    # def __init__(self, type_id, str_id=None, name=None, title=None, race=None, minerals=0,
    #              vespene=0, supply=0, is_building=False, is_worker=False, is_army=False):
    #     #: The internal integer id representing this unit type
    #     self.id = type_id

    #     #: The internal string id representing this unit type
    #     self.str_id = str_id

    #     #: The name of this unit type
    #     self.name = name

    #     #: The printable title of this unit type; has spaces and possibly punctuation
    #     self.title = title

    #     #: The race this unit type belongs to
    #     self.race = race

    #     #: The mineral cost of this unit type
    #     self.minerals = minerals

    #     #: The vespene cost of this unit type
    #     self.vespene = vespene

    #     #: The supply cost of this unit type
    #     self.supply = supply

    #     #: Boolean flagging this unit type as a building
    #     self.is_building = is_building

    #     #: Boolean flagging this unit type as a worker
    #     self.is_worker = is_worker

    #     #: Boolean flagging this unit type as an army unit
    #     self.is_army = is_army


class Command(object):
    """ Represents an in-game command """
    def __init__(self, **attributes):
        self.__dict__.update(**attributes)

    # def __init__(self, id, name=None, title=None, is_build=False, build_time=0, build_unit=None):
    #     #: The internal integer id representing this command.
    #     self.id = id

    #     #: The name of this command
    #     self.name = name

    #     #: The printable title of this command; has spaces and possibly punctuation.
    #     self.title = title

    #     #: Boolean flagging this command as creating a new unit.
    #     self.is_build = is_build

    #     #: The number of seconds required to build this unit. 0 if not ``is_build``.
    #     self.build_time = build_time

    #     #: A reference to the :class:`UnitType` type built by this command. Default to None.
    #     self.build_unit = build_unit


@loggable
class DataPack(object):
    def __init__(self, unit_types=None, commands=None):
        self.unit_types = dict()
        for unit_type in unit_types:
            self.add_unit_type(unit_type)

        self.commands = dict()
        for command in commands:
            self.add_command(command)

    def create_unit(self, unit_id, unit_type, frame):
        """
        :param unit_id: The unique id of this unit.
        :param unit_type: The unit type to assign to the new unit

        Creates a new unit and assigns it to the specified type.
        """
        unit = Unit(unit_id)
        self.change_type(unit, unit_type, frame)
        return unit

    def change_type(self, unit, new_type, frame):
        """
        :param unit: The changing types.
        :param unit_type: The unit type to assign to this unit

        Assigns the given type to a unit.
        """
        if new_type in self.units:
            unit_type = self.units[new_type]
            unit.set_type(unit_type, frame)
        else:
            self.logger.error("Unable to change type of {0} to {1} [frame {2}]; unit type not found in build {3}".format(unit, new_type, frame, self.id))

    def add_command(self, command):
        self.commands[command.id_str] = command
        self.commands[command.id_int] = command

    def add_unit_type(self, unit_type):
        self.unit_types[unit_type.id_str] = unit_type
        self.unit_types[unit_type.id_int] = unit_type
