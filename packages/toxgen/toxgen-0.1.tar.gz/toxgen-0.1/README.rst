Toxgen
======

Produces a tox.ini file from a template config file.

The template config file is a standard tox.ini file with additional sections.
Theses sections will be combined to create new testenv: sections if they do
not exists yet.

The added sections are:

[axes]
    options::

        axis1name = value1(*)[,value2(*)[, ...]]
        axis2name = value1(*)[,value2[, ...]]

    In this section, a list of test axes are given and for each of them a
    list of possible values.

    A tailing '*' on a value means it is this axis default value. Hence it can
    be set on only one value.
    The default value will create additional sections with this axis value
    removed from the section name (see below)

    Example:
        To test a lib against different python version with and without
        'lxml'::

            [axes]
            python = py25,py32
            lxml = lxml*,nolxml

        This will generate the following [testenv:] sections::

            [testenv:py25-lxml]
            # ...

            [testenv:py25]
            # A copy of testenv:py25-lxml

            [testenv:py25-nolxml]
            # ...

            [testenv:py32-lxml]
            # ...

            [testenv:py32]
            # A copy of testenv:py27-lxml

            [testenv:py32-nolxml]
            # ...

[axis:name]
    The default options for an axis.

    Any option can be added, and if not overridden for a specific value,
    combined with the same option in the other axis

[axis:name:value]
    Options for a specific axis value.

    The only option that will be interpreted by gentox is 'constraints', a
    multi-lines option that allow to exclude other axis values.

    For example, if we want not to test py25 without lxml::

        [axis:lxml:nolxml]
        constraints=
            !python:py25

    The other options will be combined.

Complete example::

    [tox]
    envlist = py25-nolxml,py32

    [axes]
    python = py25,py32
    lxml = lxml*,nolxml

    [axis:python]
    deps =
        six

    [axis:python:py25]
    basepython=python2.5

    [axis:python:py32]
    basepython=python3.2

    [axis:lxml:nolxml]
    constraints =
        !python:py25

    [axis:lxml:lxml]
    deps =
        lxml

This will generate the following tox file::

    [tox]
    envlist = py25-nolxml,py32

    [testenv:py25-lxml]
    deps = 
        six
        lxml
    basepython = python2.5

    [testenv:py25]
    deps = 
        six
        lxml
    basepython = python2.5

    [testenv:py32-lxml]
    deps = 
        six
        lxml
    basepython = python3.2

    [testenv:py32]
    deps = 
        six
        lxml
    basepython = python3.2

    [testenv:py32-nolxml]
    deps = 
        six
    basepython = python3.2


Running
-------

::

    Usage: toxgen.py [options]

    Options:
      -h, --help            show this help message and exit
      -i FILE, --input=FILE
                            input template file to process [default: tox-tmpl.ini]
      -o FILE, --output=FILE
                            output file to generate [default: tox.ini]
      -r, --rewrite         rewrite [tox] envlist [default: False]
    
    Produce a tox.ini file from a template config file.  The template config file
    is a standard tox.ini file with additional sections. Theses sections will be
    combined to create new testenv: sections if they do not exists yet.
