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
        return DateTime('%s 00:00:00' % min(including).replace('-', '/'))
    return start_date

@indexer(IMonetEvent)
def end(context):
    """When you have no end date, check for "including" field"""
    end_date = context.end()
    including = context.getIncluding()
    if not end_date and including:
        return DateTime('%s 23:55:00' % max(including).replace('-', '/'))
    return end_date
