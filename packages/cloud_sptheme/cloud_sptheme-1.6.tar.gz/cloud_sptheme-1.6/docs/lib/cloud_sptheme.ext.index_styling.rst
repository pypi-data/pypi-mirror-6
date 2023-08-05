==========================================================================
:mod:`cloud_sptheme.ext.index_styling` - improves css styling for genindex
==========================================================================

.. module:: cloud_sptheme.ext.index_styling
    :synopsis: adds additional css styling to general index

Overview
========
This Sphinx extension intercepts & modifies the general index data
before it is rendered to html, adding some additional css classes
to help Sphinx themes (e.g. :doc:`/cloud_theme`)
provide addtional per-type styling for index entries.

Internals
=========
This extension adds the following css classes to ``genindex.html``:

* For all entries referencing an ``attribute``, ``method``, ``class``,
  ``function``, or ``module``:

  - The text containing the type of the entry (e.g. ``attribute`` or ``method``) is wrapped in a
    :samp:`<span class="category {type}">...</span>` tag.

  - If the entry contains a location (e.g. ``myclass in module myapp``),
    the ``myapp`` portion is wrapped in a ``<span class="location">...</span>`` tag.

* Entries which don't fit into one of the above categories are not modified.
