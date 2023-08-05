js.mochikit
***********

Introduction
============

This library packages `MochiKit`_ for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org/
.. _`MochiKit`: http://mochikit.org/

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.mochikit``) are published to some URL.

You can either depend on ``js.mochikit.mochikit`` to get all of MochiKit, or
pick individual modules like ``js.mochikit.Sortable``.
