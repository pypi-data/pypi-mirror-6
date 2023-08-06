# -*- coding: utf-8 -*-

from DateTime import DateTime
from plone.indexer import indexer
from .interfaces import IMonetEvent

@indexer(IMonetEvent)
def start(context):
    """When you have no start date, check for "including" field"""
    start_date = context.start()
    including = context.getIncluding()
    if not start_date and including:
        foo = DateTime()
        return DateTime('%s 00:00:00 %s' % (min(including), foo.timezone()))
    return start_date

@indexer(IMonetEvent)
def end(context):
    """When you have no end date, check for "including" field"""
    end_date = context.end()
    including = context.getIncluding()
    if not end_date and including:
        foo = DateTime()
        return DateTime('%s 23:55:00 %s' % (max(including), foo.timezone()))
    return end_date
