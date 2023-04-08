Personalised Life Calendar Generator
====================================

I'm a fan of the
`Life Calendars <https://store.waitbutwhy.com/collections/life-calendars>`_ that
can be found on Tim Urban's website www.waitbutwhy.com. It's basically a
calendar for your whole life on a single poster, with a single box representing
a week, a single row represrenting a year (52 boxes), and 90 rows for a total
of 90 years.

I liked having it on my wall, and for a while I tried using it to mark
significant past events, as well as future goals & plans. There are a couple of
practical problems with this, however, because of the current design of the
Life Calendars. The main problem is that there are no real date references on
the poster, unless you write them in yourself, so honing in on a specific box
(say, the week you're currently in right now) is tedious and error-prone.

The reason for this is obvious; the dates shown would be specific to your own
birthday, so you can't make one poster for everybody if there are dates on it.
The minimalist design of the poster kind of compensates for this, since you are
left with plenty of room to write/draw whatever you want. Fair enough.

I'm lazy, though. I don't want to write all those dates in. Plus, if I lose or
damage the poster, I'd have to do all that work again. So I did this instead.

This script takes your birthday as an argument, and generates a .pdf file
containing a life calendar annotated with your personal dates. (Document size
is 29x40 inches, for best printing results)

Several additional features make navigation through the calendar a bit easier;

1. Rather than just starting exactly on your birthday, it starts on the last
   Monday before your birthday (i.e. the first day of the week you were born).
   This makes it much easier to identify which box holds a particular date, since
   every box starts with a Monday and represents "the week starting on <date>"

2. For each row, the date of the first day of the first box in the row is
   printed on the right hand side. This date is always a Monday, as explained in
   #1.

3. Boxes containing your birthday are shaded

4. Boxes containing the first day of the year are shaded (a different shade)

5. Number of calendar rows (years) is configurable between 90-100

Installation
============

Dependencies
------------

You must install ``pycairo`` before you can generate a
Life Calendar:

* `PyCairo <https://pypi.python.org/pypi/pycairo>`_ (Python library for drawing
  stuff & generating documents/images)

  ::

      pip install pycairo

  Or if you're running something like Debian/Ubuntu:

  ::

      sudo apt-get install python-cairo

If you are getting ``Error: out of memory`` when running pycairo on windows after installing with pip,
try instead installing from `this archive of pre-built pycairo wheels for windows <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo>`_.
Make sure to pick the right wheel for your system, i.e. if you are using 64-bit python 3.11,
you should pick ``pycairo-1.21.0-cp311-cp311-win_amd64.whl``.

Download
--------

Clone this repo to get the ``generate_life_calendar.py`` script

::

    $> git clone https://github.com/eriknyquist/generate_life_calendar

Usage
=====

After cloning this repo, run the script, passing in your birth date (format
can be either dd-mm-yyyy or dd/mm/yyyy)

::

    $> cd generate_life_calendar
    $> python generate_life_calendar.py "23/10/1990"

    Created life_calendar.pdf

By default, the output will be a file called ``life_calendar.pdf``. You can
change the output filename with the ``-f`` option

::

    $> python generate_life_calendar.py "23/10/1990" -f my_life_calendar.pdf

    Created my_life_calendar.pdf

If you would like to fill in the squares for past weeks but don't want to do
this by hand, just pass the ``-d`` option to darken past weeks

::

    $> python generate_life_calendar.py "23/10/1990" -d

    Created life_calendar.pdf
