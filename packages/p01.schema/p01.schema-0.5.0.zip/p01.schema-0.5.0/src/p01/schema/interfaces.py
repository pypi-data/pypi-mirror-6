###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Interfaces

$Id: interfaces.py 3978 2014-03-25 10:52:43Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.schema.interfaces
import zope.i18nmessageid

_ = zope.i18nmessageid.MessageFactory('p01')


###############################################################################
#
# schema (HTML5 input fields)

class IColor(zope.schema.interfaces.ITextLine):
    """Color schema"""


class IDate(zope.schema.interfaces.IDate):
    """Date schema"""


class IDatetime(zope.schema.interfaces.IDatetime):
    """Datetime schema"""


class IDatetimeLocal(zope.schema.interfaces.IDatetime):
    """Datetime local schema"""


class IEMail(zope.schema.interfaces.ITextLine):
    """A valid RFC822 email address field."""


class IMonth(zope.schema.interfaces.ITextLine):
    """Month schema"""


class INumber(zope.schema.interfaces.IInt):
    """URL schema"""


class ISearch(zope.schema.interfaces.ITextLine):
    """Search schema"""


class ITel(zope.schema.interfaces.ITextLine):
    """Telephone schema"""


class ITime(zope.schema.interfaces.ITextLine):
    """Time schema"""


class IURL(zope.schema.interfaces.ITextLine):
    """URL schema"""


class IWeek(zope.schema.interfaces.ITextLine):
    """Week schema"""
