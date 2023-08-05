===================================================================================
:mod:`cloud_sptheme.ext.issue_tracker` - support for `issue` text role
===================================================================================

.. module:: cloud_sptheme.ext.issue_tracker
    :synopsis: quickly create links to project's issue tracker with ``:issue:`` role

Overview
========
This Sphinx extension adds a new text role, ``:issue:``, which will automatically
be converted into links to your project's issue tracker.

Issue roles should have the format ``:issue:`5``` or ``:issue:`Custom Title <5>```.
They will be converted into external references to the appropriate issue number
in your project's issue tracker.

Configuration
=============
This extension reads the following ``conf.py`` options:

    ``issue_tracker_url``

        This should provide a path to the project's issue tracker.
        It should have one of the following formats:

        * :samp:`bb:{user}/{project}` -- link to BitBucket issue tracker for specified project
        * :samp:`gh:{user}/{project}` -- link to GitHub issue tracker for specified project
        * :samp:`gc:{project}` -- link to Google Code issue tracker for specified project
        * string containng arbitrary url, the substring ``{issue}`` will be replaced with the relevant issue number,
          and ``{title}`` with the link title.

        If this option is not specified, all issue references will be converted
        into labels instead of links.

    ``issue_tracker_title``

        Template for generating default title for references that only
        specify the issue number (e.g. ``:issue:`5```). This defaults
        to ``Issue {issue}``.

``conf.py`` Usage Example::

    # add to list of extensions:
    extensions = [
        ...
        'cloud_sptheme.ext.issue_tracker',
    ]

    ...

    # set path to issue tracker:
    issue_tracker_url = "https://example.org/tracker/{issue}"

Internals
=========
.. note::

    For themeing purposes, the generated ``<a>`` tag
    will have an ``issue`` CSS class added to it.
