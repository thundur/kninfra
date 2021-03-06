# vim: et:sta:bs=2:sw=4:
# Genereert config.agenda.php van de Karpe Noktem google calendar.
#  TODO  UTF?

import gdata.calendar.service
import gdata.calendar
import gdata.service
import locale
import sys
import re

from cStringIO import StringIO
from iso8601 import parse_date
from datetime import datetime, timedelta

try:
    # Nederlandse afkortingen voor data
    locale.setlocale(locale.LC_ALL, 'nl_NL')
except Exception:
    pass

default_cid = "vssp95jliss0lpr768ec9spbd8@group.calendar.google.com"

def parse_date_range(start, end):
    """ Ugly hack to properly parse gdata date ranges """
    hack_on_end = False
    if start.find('T') == -1:
        start += 'T00:00:00.000'
    if end.find('T') == -1:
        end += 'T23:59:59.000'
        hack_on_end = True
    if hack_on_end: the_end_date = parse_date(end) - timedelta(1,0,0)
    else: the_end_date = parse_date(end)
    return (parse_date(start),
            the_end_date )

def retreive(cid):
    """ Retreives the public future events on the calendar with id <cid> """
    r = []
    now = datetime.now()
    cs = gdata.calendar.service.CalendarService()
    q = gdata.calendar.service.CalendarEventQuery(cid, 'public', 'full')
    q.start_min = "%s-%s-%s" % (now.year,
                    str(now.month).zfill(2),
                    str(now.day).zfill(2))
    feed = cs.CalendarQuery(q)
    while True:
        for an_event in feed.entry:
            if len(an_event.when) == 0:
                continue
            r.append((an_event.title.text,
                an_event.content.text,)+
                parse_date_range(an_event.when[0].start_time,
                an_event.when[0].end_time))
        if feed.GetNextLink() is None:
            break
        feed = cs.Query(feed.GetNextLink().href,
                converter=gdata.calendar.CalendarEventFeedFromString)
    return r

def phpstr(s):
    """ Converts <s> to a php string literal """
    if isinstance(s, str):
        # FIXME why the difference?
        s = unicode(s, 'utf8')
    ret = '"%s"' % s.encode('utf8')
    return ret

def to_config_agenda_php(events):
    erepl = re.compile("([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})",
               re.IGNORECASE)
    villare = re.compile("(villa van schaeck)", re.IGNORECASE)
    o = StringIO()
    events.sort(lambda x,y: cmp(x[3], y[3]))
    o.write("<?php\n"+
            "// Autogenerated by utils/fetch-agenda.py\n"+
            "//  DO NOT EDIT BY HAND\n"+
            "// (generated on %s\n" % datetime.now() +
            "\n"+
            "$cfg['agenda'] = array(\n")
    first = True
    for title, content, start_time, end_time in events:
        if first: first = False
        else: o.write(',\n')
        if content == None: content = ""
        title = title.replace('"', '\\"')
        content = content.replace('"', '\\"')
        content = content.replace("\n", "<br/>")
        content = erepl.sub("\".email('\\1').\"", content)
        content = villare.sub(
            "<a href='\".auri('route').\"'>\\1</a>", content)
        # MAYDO, format content nicely
        o.write(" array(%s,\n" % phpstr(title) +
            "      '%s',\n" % (start_time.strftime('%%s %b') %
            start_time.day))
        if (end_time - start_time) < timedelta(1, 0, 0):
            t = "      '%s',\n" % start_time.strftime('%A %d %B')
        else:
            t = "      '%s&mdash;%s',\n" % (
                (start_time.strftime('%A %%s %B') %
                start_time.day),
                (end_time.strftime('%%s %B') %
                end_time.day))
        o.write(t + "      %s,\n" % phpstr(title))
        o.write(phpstr(content))
        o.write(")")
    o.write(");\n"+
        "?>")
    return o.getvalue()

def update_site_agenda(giedo):
    events = retreive(default_cid)
    php = to_config_agenda_php(events)
    with open("/srv/karpenoktem.nl/htdocs/site/config.agenda.php", "w") \
         as fh:
        fh.write(php)
    return {'success': True}

if __name__ == '__main__':
    if len(sys.argv) >= 2: cid = sys.argv[1]
    else: cid = default_cid
    events = retreive(cid)
    print to_config_agenda_php(events)
