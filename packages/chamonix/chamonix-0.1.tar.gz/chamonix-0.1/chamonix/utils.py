# -*- coding: utf-8 -*-
from functools import partial
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os
import datetime
from threading import Thread
import uuid

from icalendar import Calendar, Event
import web

from chamonix.config import settings


__all__ = [
    'memoize',
    'threaded',
    'gmail',
    'make_ics',
    'make_one_event',
    'ical_to_mimetype',
    'simple_msg',
    'multipart_msg',
    'to_mimehtml',
    'to_mimetext',
    'seeother_on_error',
    'email_it_on_error'
]


class memoize(object):
    ## {{{ http://code.activestate.com/recipes/577452/ (r1), modified by Chaobin Tang
    """cache the return value of a method

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.

    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:
    class Obj(object):
        @memoize
        def add_to(self, arg):
            return self + arg
    Obj.add_to(1) # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached
    """
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)
    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            # Cache slot set on obj.__class__
            cache = obj.__class__.__cache
        except AttributeError:
            cache = obj.__class__.__cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res

def seeother_on_error(func_or_link):
    def wrapper(*args, **kwargs):
        try:
            result = func_or_link(*args, **kwargs)
        except:
            if callable(func_or_link):
                link = web.ctx.env.get('HTTP_REFERER', '/')
            else:
                link = func_or_link
            raise web.seeother(link)
        return result
    def decorator(func):
        def inner_wrapper(*args, **kwargs):
            return wrapper(*args, **kwargs)
        return inner_wrapper
    #If used directly without arguments
    if callable(func_or_link):
        return wrapper
    #If used with arguments
    return decorator

def email_it_on_error(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception, e:
            if not isinstance(e, (web.seeother, web.redirect)):
                body = 'error: %s\nfunc: %s\nargs: %s\nkwargs:%s\nuser data: %s' % (str(e), str(func), str(args), str(kwargs), str(web.input()))
                threaded(email)(settings.ADMIN[0], settings.ADMIN[1], 'Error On Alpes Transport', body)
                # bubble the exception
            raise e
    return wrapper

def email(sender, recipient, subject, body):
    msg = simple_msg(sender, recipient, subject, body)
    gmail(sender, recipient, msg.as_string())

def gmail(sender, recipient, msg):
    session = smtplib.SMTP(settings.EMAIL['host'], settings.EMAIL['port'])
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(settings.EMAIL['user'], settings.EMAIL['passwd'])
    session.sendmail(sender, recipient, msg)

def threaded(func):
    def wrapper(*args, **kwargs):
        task = Thread(
            target=func,
            args=args,
            kwargs=kwargs
        )
        task.start()
    return wrapper

def multipart_msg(**kwargs):
    msg = MIMEMultipart('mixed')
    for k, v in kwargs.iteritems():
        msg[k] = v
    return msg

def simple_msg(sender, recipient, subject, body):
    msg = to_mimetext(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    return msg

def make_uid():
    return str(uuid.uuid4())

def make_ics(prodid, version, events):
    cal = Calendar()
    cal.add('prodid', prodid)
    cal.add('version', version)
    for event in events:
        cal.add_component(event)
    return cal

def make_one_event(summary, dtstart, dtend=None, dtstamp=None, priority=3, **kwargs):
    event = Event()
    event.add('summary', summary)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    event.add('dtstamp', dtstamp)
    event['uid'] = make_uid()
    event.add('priority', priority)
    for k, v in kwargs.iteritems():
        event.add(k, v)
    return event

def ical_to_mimetype(ical):
    ical = ical.to_ical()
    ical_atch = MIMEBase('application/ics',' ;name="%s"'%("transport.ics"))
    ical_atch.set_payload(ical)
    ical_atch.add_header('Content-Disposition', 'attachment; filename="%s"'%("transport.ics"))
    return ical_atch

def to_mimehtml(ustring):
    part = MIMEText(ustring.encode('utf-8'), 'html', 'utf-8')
    return part

def to_mimetext(ustring):
    part = MIMEText(ustring.encode('utf-8'), 'plain', 'utf-8')
    return part
