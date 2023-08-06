###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Additional (html5) zope.schema fileds

$Id: __init__.py 3978 2014-03-25 10:52:43Z roger.ineichen $
"""
__docformat__ = "reStructuredText"


from p01.schema.field import Color
from p01.schema.field import Date
from p01.schema.field import Datetime
from p01.schema.field import DatetimeLocal
from p01.schema.field import EMail
from p01.schema.field import Month
from p01.schema.field import Number
from p01.schema.field import Search
from p01.schema.field import Tel
from p01.schema.field import Time
from p01.schema.field import URL
from p01.schema.field import Week

# additional methods
from p01.schema.field import isValidEMailAddress
