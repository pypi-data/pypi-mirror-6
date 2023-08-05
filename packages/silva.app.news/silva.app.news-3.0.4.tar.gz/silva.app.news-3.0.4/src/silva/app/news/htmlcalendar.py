# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from calendar import Calendar, January
from datetime import date
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('silva_news')

month_name = [None,
              _('January'),
              _('February'),
              _('March'),
              _('April'),
              _('May'),
              _('June'),
              _('July'),
              _('August'),
              _('September'),
              _('October'),
              _('November'),
              _('December')]

day_abbr = [_('Mon'),
            _('Tue'),
            _('Wed'),
            _('Thu'),
            _('Fri'),
            _('Sat'),
            _('Sun')]


class HTMLCalendar(Calendar):
    """
    This calendar returns complete HTML pages.
    """

    # CSS classes for the day <td>s
    cssclasses = ["mon", "tue", "wed", "thu", "fri", "sat we", "sun we"]

    def __init__(self, first_weekday=0, prev_link=None, next_link=None,
            current_day=None, today=None, day_render_callback=None):
        super(HTMLCalendar, self).__init__(first_weekday)
        self.prev_link = prev_link
        self.next_link = next_link
        self.current_day = current_day
        self.today = today
        self.day_render_callback = day_render_callback

    def __get_classes(self, year, month, day):
        classes = []
        try:
            current = date(year, month, day)
        except ValueError:
            return []
        if current == self.current_day:
            classes.append('calendar_current')
        if current == self.today:
            classes.append('calendar_today')
        return " ".join(classes)

    def formatday(self, day, weekday, week, year, month):
        """
        Return a day as a table cell.
        """
        classes = self.__get_classes(year, month, day)
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        else:
            extra_classes, content = self.day_render_callback(
                day, weekday, week, year, month)
            return '<td class="%s %s event">%s</td>' % \
                (self.cssclasses[weekday], classes, content,)

    def formatweek(self, week, year, month):
        """
        Return a complete week as a table row.
        """
        s = ''.join(
            self.formatday(d, wd, week, year, month) for (d, wd) in week)
        return '<tr>%s</tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s">%s</th>' % (self.cssclasses[day], day_abbr[day])

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th>%s</th><th colspan="5" class="month">%s</th>' \
            '<th>%s</th></tr>' % (
            self.prev_link or "", s, self.next_link or "",)

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, theyear, themonth))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def formatyear(self, theyear, width=3):
        """
        Return a formatted year as a table of tables.
        """
        v = []
        a = v.append
        width = max(width, 1)
        a('<table border="0" cellpadding="0" cellspacing="0" class="year">')
        a('\n')
        a('<tr><th colspan="%d" class="year">%s</th></tr>' % (width, theyear))
        for i in range(January, January+12, width):
            # months in this row
            months = range(i, min(i+width, 13))
            a('<tr>')
            for m in months:
                a('<td>')
                a(self.formatmonth(theyear, m, withyear=False))
                a('</td>')
            a('</tr>')
        a('</table>')
        return ''.join(v)


