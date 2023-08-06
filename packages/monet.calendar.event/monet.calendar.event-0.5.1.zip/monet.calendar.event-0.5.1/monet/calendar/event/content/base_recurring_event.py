# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.event import ATEventSchema, ATEvent
from Products.ATContentTypes.lib.calendarsupport import ICS_EVENT_START, ICS_EVENT_END, VCS_EVENT_END
from Products.ATContentTypes.lib.calendarsupport import rfc2445dt, vformat, foldLine
from Products.ATContentTypes.permission import ChangeEvents
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from cStringIO import StringIO
from datetime import datetime, timedelta
from monet.calendar.event import eventMessageFactory as _
from monet.calendar.event import utils
from rt.calendarinandout.widget import CalendarInAndOutWidget
from types import StringType
import time

try:
    # turn off
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

VCS_EVENT_START = """\
BEGIN:VEVENT
DTSTART:%(startdate)s
DTEND:%(enddate)s
UID:ATEvent-%(uid)s
SEQUENCE:0
LAST-MODIFIED:%(modified)s
SUMMARY:%(summary)s
"""


RECURRING_EVENT_SCHEMA = atapi.Schema((
         
        LinesField(
            'cadence',
            required= False,
            vocabulary='_get_days_vocab',
            widget = MultiSelectionWidget(
                format = 'checkbox',
                label=_("label_cadence", default=u"Cadence"),
                description=_("description_cadence",
                              default=u"You can set the actual days of the event in the date range specified above.\n"
                                      u"If you don't set this field the event takes place every day of the week."),
                ),
            enforceVocabulary=True,
            languageIndependent=True
        ),
                                     
        LinesField(
            'except',
            required= False,
            widget = CalendarInAndOutWidget(
                label=_("label_except", default=u"Except"),
                description=_("description_field_except",
                              default=u"In this field you can set the list of days on which the event is not held.\n"
                                      u"Enter dates in the form yyyy-mm-dd."),
                auto_add=True,
                ),
            languageIndependent=True
        ),

        LinesField(
            'including',
            required= False,
            widget = CalendarInAndOutWidget(
                label=_("label_including", default=u"Including"),
                description=_("description_field_including",
                              default=u"In this field you can set the list of days on which the event is additionally held, even if excluded by other filters.\n"
                                      u"Enter dates in the form yyyy-mm-dd.\n"
                                      u"This field became required if you don't provide any From/To dates of the event."),
                auto_add=True,
                ),
            languageIndependent=True
        ),

))


EventSchema = ATEventSchema.copy() + RECURRING_EVENT_SCHEMA.copy()

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

EventSchema['title'].storage = atapi.AnnotationStorage()
EventSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(EventSchema, moveDiscussion=False)
EventSchema.moveField('cadence', after='endDate')
EventSchema.moveField('except', after='cadence')
# finalizeATCTSchema moves 'location' into 'categories', we move it back:
EventSchema.changeSchemataForField('location', 'default')
EventSchema.moveField('location', before='startDate')

EventSchema['subject'].widget.visible = {'edit': 'visible'}
EventSchema['subject'].mode = 'wr'

del EventSchema['startDate'].default_method
del EventSchema['endDate'].default_method


class RecurringEvent(ATEvent):
    """Description of the Example Type"""

    schema = EventSchema
    
    security = ClassSecurityInfo()
    
    def _get_days_vocab(self):
        return DisplayList([('0',_('Monday')),
                           ('1',_('Tuesday')),
                           ('2',_('Wednesday')),
                           ('3',_('Thursday')),
                           ('4',_('Friday')),
                           ('5',_('Saturday')),
                           ('6',_('Sunday'))])

    def _smart_start_date(self):
        if self.start():
            return self.start().asdatetime()
        return DateTime(self.getIncluding()[0]).asdatetime()

    def _smart_end_date(self):
        if self.end():
            return self.end().asdatetime() 
        return DateTime(self.getIncluding()[-1]).asdatetime()

    security.declareProtected(permissions.View, 'getDates')
    def getDates(self, day=None):
        """Main method that return all day in which the event occurs"""
        event_days = []

        if self.start() and self.end():
            _start_date = self._smart_start_date()
            _end_date = self._smart_end_date()

            exceptions = set(self.getExcept())

            blacklist = []                
            for black in sorted(exceptions):
                black = black.split('-')
                datee = datetime(int(black[0]), int(black[1]), int(black[2]))
                blacklist.append(datee.date())
    
            if day:
                if ((not self.getCadence() or str(day.weekday()) in self.getCadence()) 
                     and not day in blacklist):
                    event_days.append(day)
                return event_days
    
            duration = (_end_date.date() - _start_date.date()).days
            while(duration > 0):
                day = _end_date - timedelta(days=duration)
                if (not self.getCadence() or str(day.weekday()) in self.getCadence()) and not day.date() in blacklist:
                    event_days.append(day.date())
                duration = duration - 1
            if (not self.getCadence() or str(_end_date.weekday()) in self.getCadence()) and not _end_date.date() in blacklist:
                event_days.append(_end_date.date())

        # now includings additional days
        includings = set([datetime.strptime(a ,'%Y-%m-%d').date() for a in self.getIncluding()])
        includings.update(set(event_days))
        return tuple(includings)

    def getISODates(self):
        event_days = self.getDates()
        return [d.strftime('%Y-%m-%d') for d in event_days]
    
    security.declareProtected(permissions.View, 'getVCal')
    def getVCal(self):
        """get vCal data
        """
        
        _start_date = self._smart_start_date()
        _end_date = self._smart_end_date()
        event_start = _start_date.date()
        event_end = _end_date.date()
        event_days = self.getDates()
        
        duration = (event_end - event_start).days
        intervals = []
        interval = []
        
        while(duration > 0):
            day = event_end - timedelta(days=duration)
            if day in event_days:
                if day == event_start:
                    interval.append(_start_date)
                else:
                    interval.append(day)
            else:
                if interval:
                    intervals.append(interval)
                    interval = []
            duration = duration - 1

        if event_end in event_days:
            interval.append(_end_date)
        if interval:
            intervals.append(interval)

        out = StringIO()
        for interval in intervals:
            startTime = interval[0]
            endTime = interval[-1]
            if not endTime == _end_date:
                endTime = datetime(endTime.year, endTime.month, endTime.day, 23, 59, 00)
            if not startTime == _start_date:
                startTime = datetime(startTime.year, startTime.month, startTime.day, 00, 00, 00)
#            if len(intervals) == 1:
#                startTime = self._start_date()
            map = {
                'dtstamp'   : rfc2445dt(DateTime()),
                'created'   : rfc2445dt(DateTime(self.CreationDate())),
                'uid'       : self.UID() + utils.dstartformat(interval[0]),
                'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
                'summary'   : vformat(self.Title()),
                'startdate' : rfc2445dt(utils.toDateTime(startTime)),
                'enddate'   : rfc2445dt(utils.toDateTime(endTime)),
                }
            out.write(VCS_EVENT_START % map)
            
            description = self.Description()
            if description:
                out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
    
            location = self.getLocation()
            if location:
                out.write('LOCATION:%s\n' % vformat(location))
                
            out.write(VCS_EVENT_END)
        
        return out.getvalue()
    
    security.declareProtected(permissions.View, 'getICal')
    def getICal(self):
        """get iCal data
        """
        _start_date = self._smart_start_date()
        _end_date = self._smart_end_date()
        event_start = _start_date.date()
        event_end = _end_date.date()
        event_days = self.getDates()
        
        duration = (event_end - event_start).days
        intervals = []
        interval = []
        
        while(duration > 0):
            day = event_end - timedelta(days=duration)
            if day in event_days:
                if day == event_start:
                    interval.append(_start_date)
                else:
                    interval.append(day)
            else:
                if interval:
                    intervals.append(interval)
                    interval = []
            duration = duration - 1
 
        if event_end in event_days:
            interval.append(_end_date)
        if interval:
            intervals.append(interval)
            
        out = StringIO()
        for interval in intervals:
            startTime = interval[0]
            endTime = interval[-1]
            if not endTime == _end_date:
                endTime = datetime(endTime.year, endTime.month, endTime.day, 23, 59, 00)
            if not startTime == _start_date:
                startTime = datetime(startTime.year, startTime.month, startTime.day, 00, 00, 00)
#            if len(intervals) == 1:
#                startTime = self._start_date()
            map = {
                'dtstamp'   : rfc2445dt(DateTime()),
                'created'   : rfc2445dt(DateTime(self.CreationDate())),
                'uid'       : self.UID() + utils.dstartformat(interval[0]),
                'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
                'summary'   : vformat(self.Title()),
                'startdate' : rfc2445dt(utils.toDateTime(startTime)),
                'enddate'   : rfc2445dt(utils.toDateTime(endTime)),
                }
            out.write(ICS_EVENT_START % map)
            
            description = self.Description()
            if description:
                out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
    
            location = self.getLocation()
            if location:
                out.write('LOCATION:%s\n' % vformat(location))
    
            eventType = self.getEventType()
            if eventType:
                out.write('CATEGORIES:%s\n' % ','.join(eventType))
    
            # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
            #ORGANIZER;CN=%(name):MAILTO=%(email)
            #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)
    
            cn = []
            contact = self.contact_name()
            if contact:
                cn.append(contact)
            phones = self.contact_phone()
            for phone in phones:
                cn.append(phone)
            emails = self.contact_email()
            for email in emails:
                cn.append(email)
            if cn:
                out.write('CONTACT:%s\n' % ', '.join(cn))
                
            url = self.event_url()
            if url:
                out.write('URL:%s\n' % ', '.join(url))
    
            out.write(ICS_EVENT_END)
        
        return out.getvalue()
    
    
    security.declareProtected(ChangeEvents, 'setEventType')
    def setEventType(self, value, alreadySet=False, **kw):
        """CMF compatibility method

        Changing the event type.
        """
        if type(value) is StringType:
            value = (value,)
        elif not value:
            # mostly harmless?
            value = ()
        f = self.getField('eventType')
        f.set(self, value, **kw) # set is ok

    security.declareProtected(permissions.ModifyPortalContent, 'setSubject')
    def setSubject(self, value, **kw):
        """CMF compatibility method

        Changing the subject.
        """
        f = self.getField('subject')
        f.set(self, value, **kw) # set is ok

    def _set_lines_field_values(self, fieldname, value, **kw):
        if value is None:
            return
        if not isinstance(value,list):
            value = [value,]
        f = self.getField(fieldname)
        f.set(self, sorted(set(value)), **kw) # set is ok

    security.declareProtected(permissions.ModifyPortalContent, 'setExcept')
    def setExcept(self, value, **kw):
        """
        Setting exception the clean way:
         - remove dups
         - sort elements
        """
        self._set_lines_field_values('except', value, **kw)

    security.declareProtected(permissions.ModifyPortalContent, 'setIncluding')
    def setIncluding(self, value, **kw):
        """
        Setting include the clean way:
         - remove dups
         - sort elements
        """
        self._set_lines_field_values('including', value, **kw)

    security.declareProtected(permissions.ModifyPortalContent, 'setEndDate')
    def setEndDate(self, value):
        field = self.getField('endDate')
        if value and isinstance(value, basestring):
            value = value.split(" ")[0] + " 23:55:00"
        field.set(self, value)

#    security.declareProtected(permissions.View, 'start')
#    def start(self, raw=False):
#        """Accessor for startDate field"""
#        field = self.getField('startDate')
#        including = self.getIncluding()
#        if not raw and not field.get(self) and including:
#            foo = DateTime()
#            return DateTime('%s 00:00:00 %s' % (min(including), foo.timezone()))
#        return field.get(self)
#
#    security.declareProtected(permissions.View, 'end')
#    def end(self, raw=False):
#        """Accessor for endDate field"""
#        field = self.getField('endDate')
#        including = self.getIncluding()
#        if not raw and not field.get(self) and including:
#            foo = DateTime()
#            return DateTime('%s 23:55:00 %s' % (max(including), foo.timezone()))
#        return field.get(self)

    def _validate_blacklist(self, errors, blacklist, startdate, enddate):
        for black in blacklist:
            try:
                black = black.split('-')
                datee = datetime(int(black[0]), int(black[1]), int(black[2])).date()
            except:
                errors['except'] = _("description_except",
                                     default=u'Enter the dates in the form yyyy-mm-dd')
                return errors

            if startdate and datee < startdate:
                errors['except'] = _("interval_except",
                                     default=u'One or more dates are not in the previous range [Start event - End event]')
                return errors
            if enddate and datee > enddate:
                errors['except'] = _("interval_except",
                                     default=u'One or more dates are not in the previous range [Start event - End event]')
                return errors

            if startdate and datee==startdate:
                errors['startDate'] = _("except_bound_except_start",
                                     default=u'The start date is not a valid date because an except entry invalidate it.')
                return errors

            if enddate and datee==enddate:
                errors['endDate'] = _("except_bound_except_end",
                                     default=u'The end date is not a valid date because an except entry invalidate it.')
                return errors


    def _validate_cadence(self, errors, cadence, startdate, enddate):
        startOk = False
        endOk = False
        if startdate and startdate.weekday() in cadence:
            startOk = True
        if enddate and enddate.weekday() in cadence:
            endOk = True
        if not startOk and startdate:
            errors['startDate'] = _("cadence_bound_except_start",
                                    default=u'The start date is not a valid date because is not in the cadence set.')
            return errors
        if not endOk and enddate:
            errors['endDate'] = _("cadence_bound_except_end",
                                  default=u'The end date is not a valid date because is not in the cadence set.')
            return errors

    def post_validate(self, REQUEST, errors):
        """Check to make sure that the user give date in the right format/range"""
        
        blacklist = set(REQUEST.get('except', []))
        cadence = [int(x) for x in REQUEST.get('cadence', []) if x]
        including = set(REQUEST.get('including', []))
        startdate = REQUEST.get('startDate', None)
        if startdate:
            startdate = startdate.split(' ')[0].split('-')
            startdate = datetime(int(startdate[0]),int(startdate[1]),int(startdate[2])).date()
        enddate = REQUEST.get('endDate', None)
        if enddate:
            enddate = enddate.split(' ')[0].split('-')
            enddate = datetime(int(enddate[0]),int(enddate[1]),int(enddate[2])).date()

        # Required field validation (there's an hack for LinguaPlone usage)
        if (not startdate or not enddate) and not including and '/translate_item' not in REQUEST.ACTUAL_URL:
            errors['startDate'] = errors['endDate'] = \
                    _("required_datefields_error",
                      default=u'Start and End date are required, or you must provide the "Include" field')
            return errors

        # blacklist validation
        blacklist_errors = self._validate_blacklist(errors, blacklist, startdate, enddate)
        if blacklist_errors:
            return blacklist_errors

        # Check if cadence fill event start and end
        if cadence and (startdate or enddate):
            cadence_errors = self._validate_cadence(errors, cadence, startdate, enddate)
            if cadence_errors:
                return cadence_errors

