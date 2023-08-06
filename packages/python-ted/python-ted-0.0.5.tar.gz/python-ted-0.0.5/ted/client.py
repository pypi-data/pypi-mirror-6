from collections import namedtuple
import logging
import re


from datetime import datetime, timedelta
from daterange import DateRange
from icalendar import Calendar, Event
from lxml import html
from requests import Session

from .aspx_session import ASPXSession
from .course import Course


class Client:
    """
    Main interface for interacting with T@Ed.

    Attributes:

    Client.session
    Client.aspx_session
    Client.courses
    Client.week_dateranges

    >>> timetable = Client()
    >>> this_week = timetable.week_dateranges['Sem2 wk10']
    >>> course = timetable.course('INFR08015')
    >>> events = timetable.events(course)

    """

    base_url = 'https://www.ted.is.ed.ac.uk/UOE1314_SWS/default.aspx'
    weeklist_url = 'https://www.ted.is.ed.ac.uk/UOE1314_SWS/weeklist.asp'


    def __init__(self):
        """
        Initialise T@Ed session and download course list.
        """
        self.session = Session()

        # Get ASPX session variables from default page:
        response = self.session.get(Client.base_url, verify=False)
        index = html.document_fromstring(response.text)
        self.aspx_session = ASPXSession(index)

        logging.info('Fetching course list webpage...')
        parameters = {
            '__EVENTTARGET': 'LinkBtn_modules',
            'tLinkType': 'information',
        }
        course_page = self.post(Client.base_url, parameters=parameters)
        course_options = course_page.xpath('//select[@name="dlObject"]/option')

        logging.info('Building Course list')
        self.courses = []
        for option in course_options:
            try:
                title, identifier = option.text.strip().rsplit(' - ', 1)
            except ValueError as e:
                title = identifier = option.text.strip()
                logging.warning('Error in splitting {0}: {1}'.format(title, e))
                logging.info('Title and identifier will be the same for {0}'.format(title))
            code = identifier[:9]
            self.courses.append(Course(title=title,
                                       identifier=identifier,
                                       code=code))

        logging.info('Fetching academic-week/date conversion webpage...')
        week_date_page = self.get(Client.weeklist_url)

        logging.info('Building academic-week/date dictionary...')
        self.week_dateranges = dict()
        week_date_rows = week_date_page.xpath('/html/body/table[@class="weektable"]//tr[./td]')
        for row in week_date_rows:
            week_str, date_str = row.xpath('./td/text()')
            dtstart = datetime.strptime(date_str[4:], '%a %d %b %Y')
            dtend = dtstart + timedelta(days=7)
            self.week_dateranges[week_str] = DateRange(dtstart, dtend)

        return


    def get(self, url, parameters=None):
        """
        Get a webpage, returning HTML.
        """
        logging.debug('GET ' + url + '?' + str(parameters))
        if parameters:
            parameters.update(self.aspx_session.parameters())

        response = self.session.get(url, params=parameters, verify=False)
        page = html.document_fromstring(response.text)

        try:
            self.aspx_session = ASPXSession(page)
        except Exception as e:
            logging.warning(url + ' - ' + str(e))
        return page


    def post(self, url, parameters):
        """
        Post data to a webpage, returning HTML.
        """
        logging.debug('POST ' + url + '?' + str(parameters))
        parameters.update(self.aspx_session.parameters())
        response = self.session.post(url, data=parameters, verify=False)
        page = html.document_fromstring(response.text)

        try:
            self.aspx_session = ASPXSession(page)
        except Exception as e:
            logging.warning(url + ' - ' + str(e))

        return page


    def match(self, regex):
        """
        Returns a list of all courses which have an attribute matching the given regex.
        """
        return [c for c in self.courses if regex.match(c.title)
                                        or regex.match(c.code)
                                        or regex.match(c.identifier)]


    def course(self, course_code=None):
        for c in self.courses:
            if course_code in c.code:
                return c


    def dateranges_for_week_str(self, weeks_str):
        """
        >>> weeks('Sem2 wk3-Sem2 wk5,  Sem2 wk6-Sem2 wk11')
        ['Sem2 wk3', 'Sem2 wk4', 'Sem2 wk5', 'Sem2 wk6', 'Sem2 wk7', 'Sem2 wk8', 'Sem2 wk9', 'Sem2 wk10', 'Sem2 wk11']
        """
        week_ranges = weeks_str.split(',  ')
        date_ranges = []
        for week_range in week_ranges:
            first_week_str, last_week_str = week_range.split('-')
            first_week = self.week_dateranges[first_week_str]
            last_week = self.week_dateranges[last_week_str]
            date_ranges.append(DateRange(first_week.date, last_week.to))
        return date_ranges


    def events(self, course):
        parameters = {
            'tLinkType': 'modules',
            'dlFilter':  '',
            'tWildcard': '',
            'dlObject':  course.identifier,
            'lbWeeks':   't',
            'lbDays':    '1-7',
            'dlPeriod':  '1-32',
            'dlType':    'TextSpreadsheet;swsurl;SWSCUST Object TextSpreadsheet',
            'bGetTimetable': '',
        }
        timetable_page = self.post(Client.base_url, parameters=parameters)
        day_numbered_trs = enumerate(timetable_page.xpath('//table[@class="spreadsheet"]//tr[not(contains(@class, "columnTitles"))]'))

        events = []
        for (day_number, event_row) in day_numbered_trs:
            event_tds = event_row.xpath('./td')
            event = Event()
            event.uid = course.identifier + '-' + event_tds[0].text + '@timetab.benjeffrey.com'
            event.add('summary', event_tds[0].text)
            event.add('description', event_tds[1].text)
            event.add('dtstamp', datetime.now())

            start_time = datetime.strptime(event_tds[3].text.strip(), '%H:%M').time()
            end_time = datetime.strptime(event_tds[4].text.strip(), '%H:%M').time()
            weeks = self.dateranges_for_week_str(event_tds[5].text)
            event.add('dtstart',
                      datetime.combine(weeks[0].date + timedelta(days=day_number),
                                       start_time))
            event.add('dtend',
                      datetime.combine(weeks[0].date + timedelta(days=day_number),
                                       start_time))
            for week in weeks:
                event.add('rdate', week.date + timedelta(days=day_number))

            location = event_tds[7].text.strip() + ', ' + event_tds[6].xpath('./a/text()')[0].strip()
            event.add('location', location)

            event.add('categories', ['EDUCATION', event_tds[2].text])

            events.append(event)
        return events


    def calendar(self, events):
        """
        Build an icalendar Calendar containing all the given events.
        """
        cal = Calendar()
        cal.add('prodid', '-//Ben Jeffrey//NONSGML timetab//EN')
        cal.add('version', '2.0')
        for event in events:
            cal.add_component(event)
        return cal
