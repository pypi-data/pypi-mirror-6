js.vanderlee_colorpicker
************************

Introduction
============

This library packages `vanderlee/colorpicker`_ for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org/
.. _`vanderlee/colorpicker`: https://github.com/vanderlee/colorpicker

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.vanderlee_colorpicker``) are published to some URL.

The parsers and swatches are not included in the default resource
``colorpicker``, but have their own resources (``cmyk_parser``,
``cmyk_percentrage_parser``, ``swatches_crayola``, ``swatches_pantone``,
``swatches_ral``), so remember to ``need()`` these explicitly if you want to
use some of those features.

The translations are not included in this package (yet?).
