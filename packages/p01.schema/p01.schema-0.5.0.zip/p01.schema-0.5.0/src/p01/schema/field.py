###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Schema fields

$Id: field.py 3978 2014-03-25 10:52:43Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

import p01.schema.exceptions
from p01.schema import interfaces


###############################################################################
#
# html5 input controls

# color
@zope.interface.implementer(interfaces.IColor)
class Color(zope.schema.TextLine):
    """A valid color"""
    __doc__ = interfaces.IColor.__doc__


# date
@zope.interface.implementer(interfaces.IDate)
class Date(zope.schema.Date):
    """A valid date"""
    __doc__ = interfaces.IDate.__doc__


# datetime
@zope.interface.implementer(interfaces.IDatetime)
class Datetime(zope.schema.Datetime):
    """A valid datetime"""
    __doc__ = interfaces.IDatetime.__doc__


@zope.interface.implementer(interfaces.IDatetimeLocal)
class DatetimeLocal(zope.schema.Datetime):
    """A valid datetime"""
    __doc__ = interfaces.IDatetimeLocal.__doc__



# email
rfc822_specials = '()<>@,;:\\"[]'

def isValidEMailAddress(addr):
    """Returns True if the email address is valid and False if not."""

    # First we validate the name portion (name@domain)
    c = 0
    while c < len(addr):
        if addr[c] == '@':
            break
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1

    # check whether we have any input and that the name did not end with a dot
    if not c or addr[c - 1] == '.':
        return False

    # check also starting and ending dots in (name@domain)
    if addr.startswith('.') or addr.endswith('.'):
        return False

    # Next we validate the domain portion (name@domain)
    domain = c = c + 1
    # Ensure that the domain is not empty (name@)
    if domain >= len(addr):
        return False
    count = 0
    while c < len(addr):
        # Make sure that domain does not end with a dot or has two dots in a row
        if addr[c] == '.':
            if c == domain or addr[c - 1] == '.':
                return False
            count = count + 1
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1
    if count >= 1:
        return True
    else:
        return False

@zope.interface.implementer(interfaces.IEMail)
class EMail(zope.schema.TextLine):
    """A valid email address."""
    __doc__ = interfaces.IEMail.__doc__

    def constraint(self, value):
        return '\n' not in value and '\r' not in value

    def _validate(self, value):
        super(EMail, self)._validate(value)
        if not isValidEMailAddress(value):
            raise p01.schema.exceptions.NotValidEMailAdress(value)


# month
@zope.interface.implementer(interfaces.IMonth)
class Month(zope.schema.TextLine):
    """A valid month"""
    __doc__ = interfaces.IMonth.__doc__


# number
@zope.interface.implementer(interfaces.INumber)
class Number(zope.schema.TextLine):
    """A valid number (integer)"""
    __doc__ = interfaces.ITel.__doc__


# search
@zope.interface.implementer(interfaces.ISearch)
class Search(zope.schema.TextLine):
    """A valid search"""
    __doc__ = interfaces.ISearch.__doc__


# tel
@zope.interface.implementer(interfaces.ITel)
class Tel(zope.schema.TextLine):
    """A valid telephone address"""
    __doc__ = interfaces.ITel.__doc__


# time
@zope.interface.implementer(interfaces.ITime)
class Time(zope.schema.TextLine):
    """A valid time"""
    __doc__ = interfaces.ITime.__doc__


# url
@zope.interface.implementer(interfaces.IURL)
class URL(zope.schema.TextLine):
    """A valid url"""
    __doc__ = interfaces.IURL.__doc__


# week
@zope.interface.implementer(interfaces.IWeek)
class Week(zope.schema.TextLine):
    """A valid week"""
    __doc__ = interfaces.IWeek.__doc__
