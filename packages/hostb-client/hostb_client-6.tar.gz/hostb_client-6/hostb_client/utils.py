#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2014
from __future__ import division, with_statement

import math

def format_thousands(number, separator = ','):
    """
    Return the number with separators (1,000,000)
    
    >>> format_thousands(1)
    '1'
    >>> format_thousands(1000)
    '1,000'
    >>> format_thousands(1000000)
    '1,000,000'
    """
    string = str(number).split('.')
    l = []
    for i, character in enumerate(reversed(string[0])):
        if i and (not (i % 3)):
            l.insert(0, separator)
        l.insert(0, character)
    string[0] = ''.join(l)
    return '.'.join(string)

def plural(amount, unit, plural='s'):
    '''
    >>> plural(1, 'unit')
    '1 unit'
    >>> plural(2, 'unit')
    '2 units'
    '''
    if abs(amount) != 1:
        if plural == 's':
            unit = unit + plural
        else: unit = plural
    return "%s %s" % (format_thousands(amount), unit)

def format_duration(seconds, verbosity=0, years=True, hours=True, milliseconds=True):
    '''
    verbosity
        0: D:HH:MM:SS
        1: Dd Hh Mm Ss
        2: D days H hours M minutes S seconds
    years
        True: 366 days are 1 year 1 day
        False: 366 days are 366 days
    hours
        True: 30 seconds are 00:00:30
        False: 30 seconds are 00:30
    milliseconds
        True: always display milliseconds
        False: never display milliseconds
    >>> format_duration(60 * 60 * 24 * 366)
    '1:001:00:00:00.000'
    >>> format_duration(60 * 60 * 24 * 366, years=False)
    '366:00:00:00.000'
    >>> format_duration(60 * 60 * 24 * 365 + 2003, verbosity=2)
    '1 year 2 seconds 3 milliseconds'
    >>> format_duration(30, hours=False, milliseconds=False)
    '00:30'
    '''
    if not seconds and seconds != 0:
        return ''
    ms = seconds * 1000
    if years:
        y = int(ms / 31536000000)
        d = int(ms % 31536000000 / 86400000)
    else:
        d = int(ms / 86400000)
    h = int(ms % 86400000 / 3600000)
    m = int(ms % 3600000 / 60000)
    s = int(ms % 60000 / 1000)
    ms = ms % 1000
    if verbosity == 0:
        if years and y:
            duration = "%d:%03d:%02d:%02d:%02d" % (y, d, h, m, s)
        elif d:
            duration = "%d:%02d:%02d:%02d" % (d, h, m, s)
        elif hours or h:
            duration = "%02d:%02d:%02d" % (h, m, s)
        else:
            duration = "%02d:%02d" % (m, s)
        if milliseconds:
            duration += ".%03d" % ms
    else:
        if verbosity == 1:
            durations = ["%sd" % d, "%sh" % h,  "%sm" % m, "%ss" % s]
            if years:
                durations.insert(0, "%sy" % y)
            if milliseconds:
                durations.append("%sms" % ms)
        else:
            durations = [plural(d, 'day'), plural(h,'hour'),
                plural(m, 'minute'), plural(s, 'second')]
            if years:
                durations.insert(0, plural(y, 'year'))
            if milliseconds:
                durations.append(plural(ms, 'millisecond'))
        durations = filter(lambda x: not x.startswith('0'), durations)
        duration = ' '.join(durations)
    return duration

def format_bytes(number):
    return format_number(number, 'byte', 'B')

def format_number(number, longName, shortName):
    """
    Return the number in a human-readable format (23 KB, 23.4 MB, 23.42 GB)
    
    >>> format_number(123, 'Byte', 'B')
    '123 Bytes'

    >>> format_number(1234, 'Byte', 'B')
    '1 KB'

    >>> format_number(1234567, 'Byte', 'B')
    '1.2 MB'

    >>> format_number(1234567890, 'Byte', 'B')
    '1.15 GB'

    >>> format_number(1234567890123456789, 'Byte', 'B')
    '1,096.5166 PB'

    >>> format_number(-1234567890123456789, 'Byte', 'B')
    '-1,096.5166 PB'

    """
    if abs(number) < 1024:
        return '%s %s%s' % (format_thousands(number), longName, number != 1 and 's' or '')
    prefix = ['K', 'M', 'G', 'T', 'P']
    for i in range(5):
        if abs(number) < math.pow(1024, i + 2) or i == 4:
            n = number / math.pow(1024, i + 1)
            return '%s %s%s' % (format_thousands('%.*f' % (i, n)), prefix[i], shortName)
