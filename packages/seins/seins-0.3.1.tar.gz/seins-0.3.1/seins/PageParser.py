__author__ = 'mackaiver'

import logging

from bs4 import BeautifulSoup

from seins.HtmlFetcher import DBHtmlFetcher


logger = logging.getLogger(__name__)


class PageContentError(Exception):
    def __init__(self, messages):
        self.messages = messages


class PageParser(object):
    _html = None
    _soup = None

    def __init__(self, dep, arr, day=None, departure_time=None):
        fetcher = DBHtmlFetcher()
        self._html = fetcher.get_efa_html(dep, arr, day, departure_time)
        self._soup = BeautifulSoup(self._html)

    @property
    def connections(self):
        raise NotImplementedError

    @property
    def errors(self):
        raise NotImplementedError


class DBPageParser(PageParser):
    _errormessages = []
    _connections = []

    def __init__(self, dep, arr, day=None, departure_time=None):
        super(DBPageParser, self).__init__(dep, arr, day, departure_time)

    @classmethod
    def from_html(cls, html):
        cls._html = html
        cls._soup = BeautifulSoup(cls._html)

    @classmethod
    def from_html_fetcher(cls, fetcher, dep, arr, day=None, departure_time=None):
        cls._html = fetcher.get_efa_html(dep, arr, day, departure_time)
        cls._soup = BeautifulSoup(cls._html)

    #returns a tuple of the form (departuretime, arrivaltime, delay, traintype)
    @property
    def connections(self):
        if self.errors:
            raise PageContentError(self.errors)

        if not self._connections:
            self._connections = self._parse_trains_()

        return self._connections

    #returns a list of strings hopefully containing meaningfull erromessages from the webpage we parsed
    @property
    def errors(self):
        if self._errormessages:
            return self._errormessages

        errortags = self._soup.find_all("div", {"class": "fline errormsg"})
        logger.debug('Error tags:  ' + str(errortags))
        self._errormessages = [e.text for e in errortags]
        return self._errormessages

    @property
    def html(self):
        return self._html

    def _parse_trains_(self):
        trains = []
        arrivals = self._soup.select("tr.ovConLine")
        logger.debug('table rows with trains:  ' + str(arrivals))

        for t in arrivals:
            trains.append(self._parse_row(t))

        return trains

    def _parse_row(self, row):
        #print(str(row))
        dep = None
        arr = None
        delay = None
        traintype = None

        cell1 = row.select("td.timelink  a")
        if cell1:
            dep = cell1[0].text[:5]
            arr = cell1[0].text[5:]
        cell2 = row.select("td.tprt  span")
        if cell2:
            delay = cell2[0].text
        cell3 = row.select("td.iphonepfeil")
        if cell3:
            traintype = cell3[0].text

        return dep, arr, delay, traintype
