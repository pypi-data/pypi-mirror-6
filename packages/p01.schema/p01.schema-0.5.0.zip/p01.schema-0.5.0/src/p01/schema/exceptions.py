###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Schema validation exceptions

$Id: exceptions.py 3978 2014-03-25 10:52:43Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.schema
import zope.i18nmessageid

_ = zope.i18nmessageid.MessageFactory('p01')


class NotValidEMailAdress(zope.schema.ValidationError):
    __doc__ = _("""Not a valid email address""")
