======
README
======

This package provides an enhanced z3c.form implementation supporting twitter
bootstrap 3 concepts including p01.form enhancements and jsonrpc support
given from j01.jsonrpc.

  >>> import p01.schema
  >>> from p01.schema import interfaces


color
-----

  >>> p01.schema.Color
  <class 'p01.schema.field.Color'>

  >>> field = p01.schema.Color()
  >>> interfaces.IColor.providedBy(field)
  True


date
----

  >>> p01.schema.Date
  <class 'p01.schema.field.Date'>

  >>> field = p01.schema.Date()
  >>> interfaces.IDate.providedBy(field)
  True


datetime
--------

  >>> p01.schema.Datetime
  <class 'p01.schema.field.Datetime'>

  >>> field = p01.schema.Datetime()
  >>> interfaces.IDatetime.providedBy(field)
  True


dateime-local
-------------

  >>> p01.schema.DatetimeLocal
  <class 'p01.schema.field.DatetimeLocal'>

  >>> field = p01.schema.DatetimeLocal()
  >>> interfaces.IDatetimeLocal.providedBy(field)
  True


email
-----

  >>> p01.schema.EMail
  <class 'p01.schema.field.EMail'>

  >>> email = p01.schema.EMail()
  >>> interfaces.IEMail.providedBy(email)
  True


month
-----

  >>> p01.schema.Month
  <class 'p01.schema.field.Month'>

  >>> field = p01.schema.Month()
  >>> interfaces.IMonth.providedBy(field)
  True


number
------

  >>> p01.schema.Number
  <class 'p01.schema.field.Number'>

  >>> field = p01.schema.Number()
  >>> interfaces.INumber.providedBy(field)
  True


search
------

  >>> p01.schema.Search
  <class 'p01.schema.field.Search'>

  >>> field = p01.schema.Search()
  >>> interfaces.ISearch.providedBy(field)
  True


tel
---

  >>> p01.schema.Tel
  <class 'p01.schema.field.Tel'>

  >>> field = p01.schema.Tel()
  >>> interfaces.ITel.providedBy(field)
  True


time
----

  >>> p01.schema.Time
  <class 'p01.schema.field.Time'>

  >>> field = p01.schema.Time()
  >>> interfaces.ITime.providedBy(field)
  True


url
---

  >>> p01.schema.URL
  <class 'p01.schema.field.URL'>

  >>> field = p01.schema.URL()
  >>> interfaces.IURL.providedBy(field)
  True


week
----

  >>> p01.schema.Week
  <class 'p01.schema.field.Week'>

  >>> field = p01.schema.Week()
  >>> interfaces.IWeek.providedBy(field)
  True
