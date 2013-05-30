# -*- coding: UTF-8 -*-
## Copyright 2012-2013 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

#~ print '20130219 lino.modlib.school 1'  


import logging
logger = logging.getLogger(__name__)

import os
import cgi
import datetime

from django.db import models
from django.db.models import Q
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from django.utils.encoding import force_unicode 
from django.utils.functional import lazy

#~ import lino
#~ logger.debug(__file__+' : started')
#~ from django.utils import translation


#~ from lino import reports
from lino import dd
#~ from lino import layouts
#~ from lino.utils import printable
from lino import mixins
#~ from lino import actions
#~ from lino import fields
#~ from lino.modlib.contacts import models as contacts
#~ from lino.modlib.notes import models as notes
#~ from lino.modlib.links import models as links
#~ from lino.modlib.uploads import models as uploads
#~ from lino.modlib.cal import models as cal
#~ from lino.modlib.users import models as users
#~ from lino.modlib.contacts.utils import Gender
#~ from lino.modlib.properties.models import HowWell
#~ from lino.utils.choicelists import HowWell, Gender
#~ from lino.utils.choicelists import ChoiceList
#~ from lino.modlib.properties.utils import KnowledgeField #, StrengthField
#~ from lino.modlib.uploads.models import UploadsByPerson
from lino.utils.choosers import chooser
from lino.utils import mti
from lino.mixins.printable import DirectPrintAction, Printable
#~ from lino.mixins.reminder import ReminderEntry
from lino.core.dbutils import obj2str

#~ from lino.modlib.countries.models import CountryCity
#~ from lino.modlib.cal import models as cal
#~ from lino.modlib.contacts.models import Partner

#~ # not used here, but these modules are required in INSTALLED_APPS, 
#~ # and other code may import them using 

#~ from lino.modlib.properties.models import Property
#~ # from lino.modlib.notes.models import NoteType
#~ from lino.modlib.countries.models import Country, City

#~ if settings.SITE.user_model:
    #~ User = dd.resolve_model(settings.SITE.user_model,strict=True)



users = dd.resolve_app('users')
cal = dd.resolve_app('cal')
contacts = dd.resolve_app('contacts')
#~ Company = dd.resolve_model('contacts.Company',strict=True)
#~ print '20130219 lino.modlib.school 2'  
Person = dd.resolve_model('contacts.Person',strict=True)
#~ print '20130219 lino.modlib.school 3'  



#~ class PresenceStatus(dd.BabelNamed):
    #~ class Meta:
        #~ verbose_name = _("Presence Status")
        #~ verbose_name_plural = _("Presence Statuses")
        
#~ class PresenceStatuses(dd.Table):
    #~ model = PresenceStatus
    
class Topic(dd.BabelNamed,dd.SimplyPrintable):
    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _('Topics')
        
    #~ print_eid_content = DirectPrintAction(_("eID sheet"),'eid-content',icon_name='x-tbar-vcard')
        
class Topics(dd.Table):
    model = Topic
    detail_layout = """
    id name
    school.LinesByTopic
    school.CoursesByTopic
    """
    
class Line(dd.BabelNamed):
    class Meta:
        verbose_name = _("Course Line")
        verbose_name_plural = _('Course Lines')
    topic = models.ForeignKey(Topic)
    
    #~ def __unicode__(self):
        #~ return "%s (%s)" % (dd.BabelNamed.__unicode__(self),self.topic)
          
        
class Lines(dd.Table):
    model = Line
    required = dd.required(user_level='manager')
    detail_layout = """
    id name
    school.CoursesByLine
    """
    
class LinesByTopic(Lines):
    master_key = "topic"

        
#~ class Room(dd.BabelNamed):
    #~ class Meta:
        #~ verbose_name = _("Classroom")
        #~ verbose_name_plural = _("Classrooms")
        
#~ class Rooms(dd.Table):
    #~ model = Room
        
        
class Teacher(Person):
    class Meta:
        #~ app_label = 'school'
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")
    
    def __unicode__(self):
        #~ return self.get_full_name(salutation=False)
        return self.last_name
      
#~ site.modules.contacts.Persons.add_detail_tab('school.CoursesByTeacher')

class TeacherDetail(contacts.PersonDetail):
    general = dd.Panel(contacts.PersonDetail.main,label = _("General"))
    box5 = "remarks" 
    main = "general school.EventsByTeacher school.CoursesByTeacher"

    #~ def setup_handle(self,lh):
      
        #~ lh.general.label = _("General")
        #~ lh.notes.label = _("Notes")

class Teachers(contacts.Persons):
    model = Teacher
    #~ detail_layout = TeacherDetail()
  

class Pupil(Person):
    class Meta:
        #~ app_label = 'courses'
        verbose_name = _("Pupil")
        verbose_name_plural = _("Pupils")
    
class PupilDetail(contacts.PersonDetail):
    box5 = "remarks" 
    general = dd.Panel(contacts.PersonDetail.main,label = _("General"))
    
    school = dd.Panel("""
    EnrolmentsByPupil 
    # PresencesByPupil
    # cal.GuestsByPartner
    """,label = _("School"))
    
    main = "general school"

    #~ def setup_handle(self,lh):
      
        #~ lh.general.label = _("General")
        #~ lh.school.label = _("School")
        #~ lh.notes.label = _("Notes")

class Pupils(contacts.Persons):
    model = Pupil
    #~ detail_layout = PupilDetail()




class StartEndTime(dd.Model):
    class Meta:
        abstract = True
    start_time = models.TimeField(
        blank=True,null=True,
        verbose_name=_("Start Time"))
    end_time = models.TimeField(
        blank=True,null=True,
        verbose_name=_("End Time"))
    
 
class Slot(mixins.Sequenced,StartEndTime):
    """
    """
    class Meta:
        verbose_name = _("Timetable Slot") # Zeitnische
        verbose_name_plural = _('Timetable Slots')
        
    name = models.CharField(max_length=200,
          blank=True,
          verbose_name=_("Name"))
  
    def __unicode__(self):
        return self.name or "%s-%s" % (self.start_time,self.end_time)
        
class Slots(dd.Table):
    model = Slot
    required = dd.required(user_level='manager')
    insert_layout = """
    start_time end_time 
    name
    """
    detail_layout = """
    name start_time end_time 
    school.CoursesBySlot
    """
    
class EventsByTeacher(cal.Events):
    help_text = _("Shows events of courses of this teacher")
    master = Teacher
    
    @classmethod
    def get_request_queryset(self,ar):
        teacher = ar.master_instance
        if teacher is None: return []
        qs = super(EventsByTeacher,self).get_request_queryset(ar)
        qs = qs.filter(project__in = teacher.course_set.all())
        return qs
  
#~ def on_event_generated(self,course,ev):
def unused_setup_course_event(self,course,ev):
    if not course.slot: 
        return
    if not ev.start_date: 
        #~ raise Exception("20120403 %s" % obj2str(ev))
        return
        
    ev.start_time = course.slot.start_time
    ev.end_time = course.slot.end_time
    
    #~ start_time = datetime.time(16)
    #~ skip = datetime.timedelta(minutes=60)
    #~ if wd in (1,2,4,5):
        #~ pass
    #~ elif wd == 3:
        #~ start_time = datetime.time(13)
    #~ else:
        #~ return
    #~ start_time = datetime.datetime.combine(ev.start_date,start_time)
    #~ start_time = start_time + skip * (course.slot - 1)
    #~ ev.set_datetime('start',start_time)
    #~ ev.set_datetime('end',start_time + skip)

#~ if not hasattr(settings.SITE,'setup_course_event'):
    #~ settings.SITE.__class__.setup_course_event = setup_course_event
    
    
class CourseStates(dd.Workflow):
    required = dd.required(user_level='admin')

add = CourseStates.add_item
add('10', _("Draft"),'draft')
add('20', _("Scheduled"),'scheduled')
add('30', _("Started"),'started')
add('40', _("Ended"),'ended')
add('50', _("Cancelled"),'cancelled')
    
    
    
#~ class Course(StartEndTime,cal.EventGenerator,cal.RecurrenceSet,mixins.Printable):
class Course(contacts.ContactRelated,cal.EventGenerator,cal.RecurrenceSet,mixins.Printable):
    """
    A Course is a group of pupils that regularily 
    meet with a given teacher in a given place.
    """
    
    FILL_EVENT_GUESTS = False
    
    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _('Courses')
        
    workflow_state_field = 'state'
    
    line = models.ForeignKey('school.Line')
    teacher = models.ForeignKey(Teacher)
    #~ place = models.ForeignKey(Place,verbose_name=_("Place"),null=True,blank=True) # iCal:LOCATION
    #~ room = models.ForeignKey(Room,blank=True,null=True)
    place = models.ForeignKey(cal.Place,blank=True,null=True)
    slot = models.ForeignKey(Slot,blank=True,null=True)
    
    state = CourseStates.field(default=CourseStates.draft)
    
    #~ slot = models.PositiveSmallIntegerField(_("Time slot"),
        #~ blank=True,null=True)
    
    def __unicode__(self):
        return u"%s (%s, %s)" % (self.line,self.company.city or self.company,self.start_date)
          
    def update_cal_rset(self):
        return self
        
    def update_cal_from(self):
        if self.state in (CourseStates.draft,CourseStates.cancelled): 
            return None
        if self.start_date is None:
            return None
        # if every is per_weekday, actual start may be later than self.start_date
        return self.get_next_date(self.start_date+datetime.timedelta(days=-1))
        
    def update_cal_until(self):
        return self.end_date
        
    def update_cal_calendar(self,i):
        return self.calendar
        
    def update_cal_subject(self,i):
        return _("Lesson %d") % i
        
    @dd.displayfield(_("Info"))
    def info(self,ar):
        return ar.obj2html(self)
        
    @dd.requestfield(_("Requested"))
    def requested(self,ar):
        #~ return ar.spawn(EnrolmentsByCourse,master_instance=self,param_values=dict(state=EnrolmentStates.requested))
        return EnrolmentsByCourse.request(self,param_values=dict(state=EnrolmentStates.requested))
        
    @dd.requestfield(_("Confirmed"))
    def confirmed(self,ar):
        return EnrolmentsByCourse.request(self,param_values=dict(state=EnrolmentStates.confirmed))
        
dd.update_field(Course,'contact_person',verbose_name = _("Contact person"))
          
          
@dd.receiver(dd.pre_save, sender=cal.Event,dispatch_uid="setup_event_from_course")
def setup_event_from_course(sender=None,instance=None,**kw):
    #~ logger.info("20130528 setup_event_from_course")
    if settings.SITE.loading_from_dump: return
    event = instance
    if event.is_user_modified(): return
    if not event.is_editable_state(): return
    if not isinstance(event.owner,Course): return
    course = event.owner
    event.project = course
    #~ settings.SITE.setup_course_event(course,event)
    
    if course.slot: 
        event.start_time = course.slot.start_time
        event.end_time = course.slot.end_time
    else:
        event.start_time = course.start_time
        event.end_time = course.end_time
    
       
if Course.FILL_EVENT_GUESTS:
    
    @dd.receiver(dd.post_save, sender=cal.Event,dispatch_uid="fill_event_guests_from_course")
    def fill_event_guests_from_course(sender=None,instance=None,**kw):
        #~ logger.info("20130528 fill_event_guests_from_course")
        if settings.SITE.loading_from_dump: return
        event = instance
        if event.is_user_modified(): return
        if not event.is_editable_state(): return
        if not isinstance(event.owner,Course): return
        course = event.owner
        if event.guest_set.count() > 0: return
        for e in course.enrolment_set.all():
            cal.Guest(partner=e.pupil,event=event).save()
    
  

class CourseDetail(dd.FormLayout):
    #~ start = "start_date start_time"
    #~ end = "end_date end_time"
    #~ freq = "every every_unit"
    #~ start end freq
    main = "general school.EnrolmentsByCourse cal.EventsByController"
    general = dd.Panel("""
    id:8 user state calendar
    summary line place slot
    company contact_person teacher
    start_date max_occurences end_date every every_unit
    monday tuesday wednesday thursday friday saturday sunday
    description
    """,label=_("General"))
    
    #~ def setup_handle(self,dh):
        #~ dh.start.label = _("Start")
        #~ dh.end.label = _("End")
        #~ dh.freq.label = _("Frequency")
  
class Courses(dd.Table):
    model = Course
    #~ order_by = ['date','start_time']
    detail_layout = CourseDetail() 
    column_names = "line teacher place slot summary *"
    order_by = ['start_date']
    
    parameters = dd.ObservedPeriod(
        company = models.ForeignKey('contacts.Company',blank=True,null=True),
        teacher = models.ForeignKey('school.Teacher',blank=True,null=True),
        line = models.ForeignKey('school.Line',blank=True,null=True),
        state = CourseStates.field(blank=True),
        )
    params_layout = """line company teacher state"""
    
    simple_param_fields = 'teacher company line state'.split()
    
    @classmethod
    def get_request_queryset(self,ar):
        qs = super(Courses,self).get_request_queryset(ar)
        if isinstance(qs,list): return qs
        for n in self.simple_param_fields:
            v = ar.param_values.get(n)
            if v:
                qs = qs.filter(**{n:v})
                #~ print 20130530, qs.query
        
        #~ if ar.param_values.teacher is not None: 
            #~ qs = qs.filter(teacher=ar.param_values.teacher)
            #~ 
        #~ if ar.param_values.line is not None: 
            #~ qs = qs.filter(line=ar.param_values.line)
            #~ 
        #~ if ar.param_values.state is not None:
            #~ qs = qs.filter(state=ar.param_values.state)
            
        return qs
        
    @classmethod
    def get_title_tags(self,ar):
        for t in super(Courses,self).get_title_tags(ar):
            yield t
            
        for n in self.simple_param_fields:
            v = ar.param_values.get(n)
            if v:
                yield unicode(v)
                
    

class CoursesByTeacher(Courses):
    master_key = "teacher"
    column_names = "line place slot summary *"

class CoursesByLine(Courses):
    master_key = "line"
    column_names = "what_text weekdays_text where_text times_text teacher place summary"

class CoursesByTopic(Courses):
    master = Topic
    order_by = ['start_date']
    column_names = "what_text weekdays_text where_text times_text teacher place summary"
    
    @classmethod
    def get_request_queryset(self,ar):
        topic = ar.master_instance
        if topic is None: return []
        return Course.objects.filter(line__topic=topic)

class CoursesBySlot(Courses):
    master_key = "slot"

class CoursesByCompany(Courses):
    master_key = "company"
    
    
class ActiveCourses(Courses):
    
    label = _("Active courses")
    column_names = 'info teacher company place requested confirmed'
    @classmethod
    def param_defaults(self,ar,**kw):
        kw = super(ActiveCourses,self).param_defaults(ar,**kw)
        kw.update(state=CourseStates.started)
        return kw

    
    
class EnrolmentStates(dd.Workflow):
    required = dd.required(user_level='admin')

add = EnrolmentStates.add_item
add('10', _("Requested"),'requested')
add('20', _("Confirmed"),'confirmed')
add('30', _("Certified"),'certified')
add('40', _("Cancelled"),'cancelled')
    

#~ class Enrolment(dd.Model):
class Enrolment(dd.UserAuthored,dd.SimplyPrintable):
  
    class Meta:
        verbose_name = _("Enrolment")
        verbose_name_plural = _('Enrolments')

    #~ teacher = models.ForeignKey(Teacher)
    course = models.ForeignKey(Course)
    pupil = models.ForeignKey(Pupil)
    request_date = models.DateField(_("Date of request"),default=datetime.date.today)
    state = EnrolmentStates.field(default=EnrolmentStates.requested)


class Enrolments(dd.Table):
    required = dd.required(user_level='manager')
    model = Enrolment
    parameters = dd.ObservedPeriod(
        author = dd.ForeignKey(settings.SITE.user_model,blank=True,null=True),
        state = EnrolmentStates.field(blank=True,null=True),
        )
    params_layout = """start_date end_date author state"""
    order_by = ['request_date']
    column_names = 'request_date course pupil state workflow_buttons user *'
        
    @classmethod
    def get_request_queryset(self,ar):
        qs = super(Enrolments,self).get_request_queryset(ar)
        if ar.param_values.user is not None:
            qs = qs.filter(user=ar.param_values.user)
            
        if ar.param_values.state:
            qs = qs.filter(state=ar.param_values.state)
            
        if ar.param_values.start_date is None or ar.param_values.end_date is None:
            period = None
        else:
            period = (ar.param_values.start_date, ar.param_values.end_date)
        if period is not None:
            qs = qs.filter(dd.inrange_filter('request_date',period))
                
        return qs
        
    @classmethod
    def get_title_tags(self,ar):
        for t in super(Enrolments,self).get_title_tags(ar):
            yield t
            
        if ar.param_values.state:
            yield unicode(ar.param_values.state)
        if ar.param_values.user:
            yield unicode(ar.param_values.user)
        

class RequestedEnrolments(Enrolments):
    
    label = _("Requested enrolments")
    
    @classmethod
    def param_defaults(self,ar,**kw):
        kw = super(RequestedEnrolments,self).param_defaults(ar,**kw)
        kw.update(state=EnrolmentStates.requested)
        return kw
        
class ConfirmedEnrolments(Enrolments):
    label = _("Confirmed enrolments")
    @classmethod
    def param_defaults(self,ar,**kw):
        kw = super(ConfirmedEnrolments,self).param_defaults(ar,**kw)
        kw.update(state=EnrolmentStates.confirmed)
        return kw
        
    
class EnrolmentsByPupil(Enrolments):
    required = dd.required()
    master_key = "pupil"

class EnrolmentsByCourse(Enrolments):
    required = dd.required()
    master_key = "course"


def get_todo_tables(ar):
    yield (RequestedEnrolments, _("%d enrolments to confirm.")) 



#~ class Lesson(models.Model,mixins.Printable):
#~ class Event(cal.EventBase):
    #~ class Meta:
        #~ app_label = 'cal'
        #~ verbose_name = _("Lesson")
        #~ verbose_name_plural = _('Lessons')
        
    #~ def __unicode__(self):
        #~ return u"%s %s (%s)" % (
          #~ babel.dtos(self.start_date),
          #~ self.start_time,
          #~ self.user)
  


#~ class Events(dd.Table):
    #~ model = Event
    #~ order_by = ['start_date','start_time']
    #~ detail_layout = EventDetail()

#~ class EventsByTeacher(Events):
    #~ master_key = "user"

#~ class EventsByCourse(Events):
    #~ master_key = "course"


#~ class Presence(dd.Model):
  
    #~ class Meta:
        #~ verbose_name = _("Presence")
        #~ verbose_name_plural = _('Presences')

    #~ # teacher = models.ForeignKey(Teacher)
    #~ event = models.ForeignKey(cal.Event)
    #~ pupil = models.ForeignKey(Pupil)
    #~ absent = models.BooleanField(_("Absent"))
    #~ excused = models.BooleanField(_("Excused"))
    #~ remark = models.CharField(_("Remark"),max_length=200,blank=True)
    #~ # status = models.ForeignKey(PresenceStatus,null=True,blank=True)
    
    #~ def save(self,*args,**kw):
        #~ if self.excused and not self.absent:
            #~ self.absent = True
        #~ super(Presence,self).save(*args,**kw)
        
    #~ def absent_changed(self,rr):
        #~ if not self.absent:
            #~ self.excused = False

#~ class Presences(dd.Table):
    #~ model = Presence
    #~ order_by = ['event__start_date','event__start_time']

#~ class PresencesByPupil(Presences):
    #~ master_key = "pupil"

#~ class PresencesByEvent(Presences):
    #~ master_key = "event"
    



#~ from lino.ui.models import SiteConfig

dd.inject_field(Person,
    'is_teacher',
    mti.EnableChild(Teacher,verbose_name=_("is a teacher")),
    """Whether this Person is also a Teacher."""
    )
dd.inject_field(Person,
    'is_pupil',
    mti.EnableChild(Pupil,verbose_name=_("is a pupil")),
    """Whether this Person is also a Pupil."""
    )

MODULE_LABEL = _("School")
    
def setup_main_menu(site,ui,profile,main):
    m = main.get_item("contacts")
    m.add_action(Teachers)
    m.add_action(Pupils)
    m = main.add_menu("school",MODULE_LABEL)
    m.add_action(Courses)
    m.add_action(Teachers)
    m.add_action(Pupils)
    m.add_action(RequestedEnrolments)
    m.add_action(ConfirmedEnrolments)
  
def unused_setup_master_menu(site,ui,profile,m): 
    #~ m = m.add_menu("school",_("School"))
    m.add_action(Teachers)
    m.add_action(Pupils)
    #~ m.add_action(CourseOffers)
    #~ m.add_action(Courses)


def setup_my_menu(site,ui,profile,m): pass
  
def setup_config_menu(site,ui,profile,m):
    m = m.add_menu("school",MODULE_LABEL)
    #~ m.add_action(Rooms)
    m.add_action(Topics)
    m.add_action(Lines)
    m.add_action(Slots)
    #~ m.add_action(PresenceStatuses)
  
def setup_explorer_menu(site,ui,profile,m):
    m = m.add_menu("school",MODULE_LABEL)
    #~ m.add_action(Presences)
    #~ m.add_action(Events)
    m.add_action(Enrolments)
  
  
#~ print '20130219 lino.modlib.school ok'  
