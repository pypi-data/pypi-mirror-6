"""Date and time resources."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import csv as _csv
from StringIO import StringIO as _StringIO
from textwrap import dedent as _dedent

import bedframe as _bedframe
import bedframe.webtypes as _webtypes
import spruce.datetime as _datetime


class DatetimeDifference(_bedframe.WebResource):

    @_bedframe.webmethod(_webtypes.timedelta, start=_webtypes.datetime,
                         end=_webtypes.datetime)
    def get(self, start, end):
        return end - start

    @get.type('text/html')
    def get(self, difference, start, end):
        html = '''\
               <!DOCTYPE html>
               <html>

               <head>
                 <title>Date and time difference</title>
               </head>

               <body>
                 <p>
                   The difference between {start} and {end} is {difference}.
                 </p>
               </body>

               </html>
               '''
        html = _dedent(html)
        html = html.format(start=start.native(), end=end.native(),
                           difference=difference.native())
        return html


class DatetimeEcho(_bedframe.WebResource):

    @_bedframe.webmethod(_webtypes.datetime, dt=_webtypes.datetime)
    def get(self, dt):
        return dt

    @get.type('text/csv')
    def get(self, echo_dt, dt):
        dt_native = echo_dt.native()
        strio = _StringIO()
        csv_writer = _csv.writer(strio)
        csv_writer.writerow((dt_native.year,
                             dt_native.month,
                             dt_native.day,
                             dt_native.hour,
                             dt_native.minute,
                             dt_native.second,
                             dt_native.microsecond,
                             dt_native.strftime('%z'),
                             ))
        return strio.getvalue()

    @get.type('text/html')
    def get(self, echo_dt, dt):
        html = '''\
               <!DOCTYPE html>
               <html>

               <head>
                 <title>Date and time echo</title>
               </head>

               <body>
                 <p>
                   {echo_dt}
                 </p>
               </body>

               </html>
               '''
        html = _dedent(html)
        html = html.format(echo_dt=echo_dt.native())
        return html


class DatetimeNow(_bedframe.WebResource):

    @_bedframe.webmethod(_webtypes.datetime)
    def get(self):
        return _datetime.now()

    @get.type('text/html')
    def get(self, now):
        html = '''\
               <!DOCTYPE html>
               <html>

               <head>
                 <title>Current date and time</title>
               </head>

               <body>
                 <p>It is currently {time} on {date} in the time zone {tz}.</p>
               </body>

               </html>
               '''
        html = _dedent(html)
        now_dt = now.native()
        tz_str = now_dt.tzname() or now_dt.strftime('%z')
        html = html.format(date=now_dt.date(),
                           time=now_dt.time().replace(microsecond=0),
                           tz=tz_str)
        return html


class DatetimeSum(_bedframe.WebResource):

    @_bedframe.webmethod(_webtypes.datetime, start=_webtypes.datetime,
                         offset=_webtypes.timedelta)
    def get(self, start, offset):
        return start + offset

    @get.type('text/html')
    def get(self, sum, start, offset):
        html = '''\
               <!DOCTYPE html>
               <html>

               <head>
                 <title>Date and time sum</title>
               </head>

               <body>
                 <p>Offsetting {start} by {offset} yields {sum}.</p>
               </body>

               </html>
               '''
        html = _dedent(html)
        html = html.format(start=start.native(), offset=offset.native(),
                           sum=sum.native())
        return html
