#!/usr/bin/python
# -*- coding: utf-8 -*-

# SàT Exceptions
# Copyright (C) 2011  Jérôme Poisson (goffi@goffi.org)

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


class ProfileUnknownError(Exception):
    pass


class ProfileNotInCacheError(Exception):
    pass


class ProfileNotSetError(Exception):
    """
    This error raises when no profile has been set (value @NONE@ is found, but it should have been replaced)
    """
    pass


class NotConnectedProfileError(Exception):
    pass


class ProfileKeyUnknownError(Exception):
    pass


class UnknownEntityError(Exception):
    pass


class UnknownGroupError(Exception):
    pass


class NotFound(Exception):
    pass


class DataError(Exception):
    pass


class ConflictError(Exception):
    pass


class CancelError(Exception):
    pass


class InternalError(Exception):
    pass


class BridgeInitError(Exception):
    pass


class BridgeExceptionNoService(Exception):
    pass

class DatabaseError(Exception):
    pass
