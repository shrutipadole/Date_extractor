import re
import pprint
import datetime
import traceback
import regex
from dateutil.parser import _timelex, parser
from dateutil.relativedelta import relativedelta
from date_preprocessing import PreProcess


class DateExtractor(object):
    """
    This class captures dates in may formats.
    It will return a dictionary with three
    keys:
        delta:      no. of days/months/years to be added(if mentioned)
        start date: the starting date in case delta is mentioned
        fin date:   the final date. This is the main key wich will
                    always have the relevant date.
    """
    
    def __init__(self):
        self.p = parser()
        self.info = self.p.info
        self.prep = PreProcess()

    def timesplit(self, query):

        """
        This module will split query into tokens and filter out irrelevant words.
        It will only keep month names, and numbers that signify a date or a year.
        Params:
            Input:
                query - str
            Output:
                query - str
                split_query - list of lists
        """

        # import pdb;pdb.set_trace()
        split_query = list(_timelex(query))
        split_query = [x for x in split_query if x != ' ']
        year_jump = ['of', 'in', 'year', 'years']
        date_jump = ['to', 'of', '-']
        date_check = ['th', 'rd', 'st', 'nd', '.']
        llist = []
        print(split_query)
        now = datetime.datetime.now().year
        if len(split_query) > 1:
            for ind, each in enumerate(split_query):                
                if ind == 0:                    
                    if (split_query[ind].isdigit() and \
                        split_query[ind+1] in date_check) or \
                    self.info.month(split_query[ind]):
                        llist.append(split_query[ind])
                if ind == len(split_query) - 1:                    
                    if self.info.month(split_query[ind]):
                        llist.append(split_query[ind])
                    if split_query[ind].isdigit():
                        if split_query[ind - 1] in date_check + date_jump or \
                        self.info.month(split_query[ind - 1]) or \
                        (split_query[ind - 1] in year_jump and \
                        split_query[ind + 1] not in ["month", "months"]) or \
                        int(split_query[ind]) > 1000:
                            if int(split_query[ind]) > 1000:
                                llist.append(split_query[ind])
                            elif int(split_query[ind]) < 100:
                                future = int(split_query[ind]) + (datetime.datetime.now().year//100*100)
                                past = int(split_query[ind]) + (datetime.datetime.now().year//100*100 - 100)
                                rep = split_query[ind]
                                if (now - past) < (future - now):
                                    century = datetime.datetime.now().year//100*100 - 100
                                else:
                                    century = datetime.datetime.now().year//100*100
                                split_query[ind] = str(int(split_query[ind])+century)
                                query = query.replace(' '+rep+' ', ' '+split_query[ind]+' ')
                                split_query = [str(int(x)+century) if x == rep else x for x in split_query]
                                llist.append(split_query[ind])
                if ind > 0 and ind < len(split_query) - 1:
                    if self.info.month(split_query[ind]):
                        llist.append(split_query[ind])
                    elif split_query[ind].isdigit():
                        if split_query[ind + 1] in date_check and int(split_query[ind]) < 32:
                            llist.append(split_query[ind])
                        elif split_query[ind - 1] in date_check + date_jump or \
                        self.info.month(split_query[ind - 1]) or \
                        (split_query[ind - 1] in year_jump and \
                        split_query[ind + 1] not in ["month", "months"]) or \
                        int(split_query[ind]) > 1000:
                            if int(split_query[ind]) > 1000:
                                llist.append(split_query[ind])
                            elif int(split_query[ind]) < 100:
                                future = int(split_query[ind]) + (datetime.datetime.now().year//100*100)
                                past = int(split_query[ind]) + (datetime.datetime.now().year//100*100 - 100)
                                rep = split_query[ind]
                                if (now - past) < (future - now):
                                    century = datetime.datetime.now().year//100*100 - 100
                                else:
                                    century = datetime.datetime.now().year//100*100
                                split_query[ind] = str(int(split_query[ind])+century)
                                query = query.replace(' '+rep+' ', ' '+split_query[ind]+' ')
                                split_query = [str(int(x)+century) if x == rep else x for x in split_query]
                                llist.append(split_query[ind])
                    elif each not in year_jump + list(set(date_check)-set('.')) and not self.info.month(each) and \
                    (split_query[ind - 1].isdigit() or self.info.month(split_query[ind - 1]) or \
                     split_query[ind - 1] in list(set(date_check)-set('.')) + date_jump):
                        if each in ['and', 'to', '-']:
                            if split_query[ind - 1] not in list(set(date_check)-set('.')) and \
                            not split_query[ind + 1].isdigit():
                                llist.append('_')
                        elif each == '.':
                            if not (split_query[ind - 1].isdigit() and \
                                    self.info.month(split_query[ind + 1])) and \
                            not (self.info.month(split_query[ind - 1]) and \
                                 split_query[ind + 1].isdigit()):
                                llist.append('_')
                        else:
                            llist.append('_')
        else:
            if self.info.month(split_query[0]):
                llist.append(split_query[0])
        print(llist)
        split_query = []
        small = []
        for ind, each in enumerate(llist):
            if each == '_' or ind == len(llist)-1:
                if each != '_':
                    small.append(each)
                split_query.append(small)
                small = []
            else:
                small.append(each)
        split_query = [each for each in split_query if each != []]
        print(">>>>>>>",split_query)
        return split_query, query

    def date_format_reader(self, query, dayfirst=True, monthfirst=False, yearfirst=False):

        """
        This module catches dates in dd/mm/yy and dd/mm formats
        Params:
            Input:
                query - str
                dayfirst - bool(true by default)[optional]
                monthfirst - bool(false by default)[optional]
                yearfirst - bool(false by default)[optional]
            Output:
                query - str
        """

        if dayfirst:
            d_m = regex.compile(r"""(?<!((\.\s?|:\s?|\\\s?|\/\s?|-\s?)|\d\s?))
                                (3[01]|[12][0-9]|0?[1-9])(\s)?(\.|:|\\|\/|-)
                                (\s)?(0?[1-9]|1[0-2])
                                (?!((\s?\.|\s?:|\s?\\|\s?\/|\s?-)|\d|
                                \s?\b(month(s)?|day(s)?|y(ea)?r(s)?|h(ou)?r(s)?|night(s)?|
                                week(s)?|am|pm|min(ute)?(s)?|sec(ond)?(s)?)\b))""")
            d_m = d_m.pattern.replace('\n', '').replace(' ', '')            
            dmy = regex.compile(r"""(?<!\d\s?|:\s?|\/\s?|\.\s?|\\\s?|-\s?)
                                (3[01]|[12][0-9]|0?[1-9])(\s)?
                                (\.|-|:|\\|\/)(\s)?
                                (0?[1-9]|1[0-2])(\s)?
                                (\3)(\s)?
                                (\d{4}|[0-9]{2})
                                (?!(((\s)?\.|(\s)?:|(\s)?\\|(\s)?\/|(\s)?-)|\d))""")
            dmy = dmy.pattern.replace('\n', '').replace(' ', '')            
            ddmmyy = regex.findall(dmy, ' '+query+' ')
            start = datetime.datetime.today()
            if ddmmyy:
                for date in ddmmyy:
                    day = int(date[0])
                    month = int(date[4])
                    year = int(date[8])
                    if year < 100:
                        future = year + (datetime.datetime.now().year//100*100)
                        past = year + (datetime.datetime.now().year//100*100 - 100)
                        now = datetime.datetime.now().year
                        if (now - past) < (future - now):
                            century = datetime.datetime.now().year//100*100 - 100
                        else:
                            century = datetime.datetime.now().year//100*100
                        year = year + century
                    repl = datetime.date(year, month, day).strftime("%d.%B.%Y ")
                    rep = ''.join([str(x) for x in date]).strip()
                    query = query.replace(rep, repl)
                    start = datetime.datetime(year, month, day)

            ddmm = regex.findall(d_m, ' '+query+' ')
            if ddmm:
                for date in ddmm:
                    day = int(date[2])
                    month = int(date[6])
                    year = start.year
                    repl = datetime.date(year, month, day).strftime("%d.%B.%Y ")
                    rep = ''.join([str(x) for x in date]).strip()
                    query = query.replace(rep, repl)

        if monthfirst:
            d_m = regex.compile(r"""(?<!((\.\s?|:\s?|\\\s?|\/\s?|-\s?)|\d))
                               (0?[1-9]|1[0-2])(\s+)?
                               (\.|:|\\|\/|-)(\s)?
                               (3[01]|[12][0-9]|0?[1-9])
                               (?!((\s?\.|\s?:|\s?\\|\s?\/|\s?-)|\d|\s+?
                               \b(am|pm|h(ou)?r(s)?|day(s)?|month(s)?|y(ea)?r(s)?|
                               night(s)?|week(s)?|mintue(s)?|sec(ond)?(s)?)\b))""")
            d_m = d_m.pattern.replace('\n', '').replace(' ', '')            
            dmy = regex.compile(r"""(?<!\d\s?|:\s?|\/\s?|\.\s?|\\\s?|-\s?)
                                (0?[1-9]|1[0-2])(\s)?
                                (\.|-|:|\\|\/)(\s)?
                                (3[01]|[12][0-9]|0?[1-9])(\s)?
                                (\3)(\s)?(\d{4}|[0-9]{2})
                                (?!(((\s)?\.|(\s)?:|(\s)?\\|(\s)?\/|(\s)?-)|\d))""")
            dmy = dmy.pattern.replace('\n', '').replace(' ', '')            
            ddmmyy = regex.findall(dmy, ' '+query+' ')
            start = datetime.datetime.today()
            if ddmmyy:
                for date in ddmmyy:
                    day = int(date[4])
                    month = int(date[0])
                    year = int(date[8])
                    if year < 100:
                        future = year + (datetime.datetime.now().year//100*100)
                        past = year + (datetime.datetime.now().year//100*100 - 100)
                        now = datetime.datetime.now().year
                        if (now - past) < (future - now):
                            century = datetime.datetime.now().year//100*100 - 100
                        else:
                            century = datetime.datetime.now().year//100*100
                        year = year + century
                    repl = datetime.date(year, month, day).strftime("%d.%B.%Y ")
                    rep = ''.join([str(x) for x in date]).strip()
                    query = query.replace(rep, repl)
                    start = datetime.datetime(year, month, day)

            ddmm = regex.findall(d_m, ' '+query+' ')
            if ddmm:
                for date in ddmm:
                    day = int(date[6])
                    month = int(date[2])
                    year = start.year
                    repl = datetime.date(year, month, day).strftime("%d.%B.%Y ")
                    rep = ''.join([str(x) for x in date]).strip()
                    query = query.replace(rep, repl)

        if yearfirst:
            dmy = regex.compile(r"""(?<!\d\s?|:\s?|\/\s?|\.\s?|\\\s?|-\s?)
                                (\d{4}|[0-9]{2})(\s)?
                                (\.|-|:|\\|\/)(\s)?
                                (0?[1-9]|1[0-2])(\s)?
                                (\3)(\s)?(3[01]|[12][0-9]|0?[1-9])
                                (?!(((\s)?\.|(\s)?:|(\s)?\\|(\s)?\/|(\s)?-)|\d))""")
            dmy = dmy.pattern.replace('\n', '').replace(' ', '')           
            ddmmyy = regex.findall(dmy, ' '+query+' ')
            start = datetime.datetime.today()
            if ddmmyy:
                for date in ddmmyy:
                    day = int(date[8])
                    month = int(date[4])
                    year = int(date[0])
                    if year < 100:
                        future = year + (datetime.datetime.now().year//100*100)
                        past = year + (datetime.datetime.now().year//100*100 - 100)
                        now = datetime.datetime.now().year
                        if (now - past) < (future - now):
                            century = datetime.datetime.now().year//100*100 - 100
                        else:
                            century = datetime.datetime.now().year//100*100
                        year = year + century
                    repl = datetime.date(year, month, day).strftime("%d.%B.%Y ")
                    rep = ''.join([str(x) for x in date]).strip()
                    query = query.replace(rep, repl)
                    start = datetime.datetime(year, month, day)

        return query

    def weekday_reader(self, query):

        """
        This module converts weekdays to their respective dates
        Params:
            Input:
                query - str
            Output:
                query - str
        """

        wkday = r'\b(monday|mon|tuesday|tue|wednesday|wed|thursday|thu|friday|fri|saturday|sat|sunday|sun)\b'
        check_day = re.search(wkday, query, re.I)
        while check_day:
            start = datetime.datetime.today()
            this_day = start.weekday()            
            split_q = list(_timelex(query.lower()))
            split_q = [x for x in split_q if x != ' ']
            that_day = self.info.weekday(check_day.group(0))
            if that_day >= this_day:
                if len(split_q) > 1 and split_q[split_q.index(check_day.group(0)) - 1] == 'next':
                    diff = that_day - this_day + 7
                    diff = diff if diff < 7 + (6 - this_day) else diff - 7
                else:
                    diff = that_day - this_day
            else:
                diff = (6 - this_day) + (that_day + 1)
            repl = (start + relativedelta(days=diff))
            query = query.replace(check_day.group(0), repl.strftime("%d.%B.%Y"), 1)
            check_day = re.search(wkday, query, re.I)
        return query

    def preprocess(self, query, delta, dayfirst=True, monthfirst=False, yearfirst=False):

        """
        This module performs basic preprocessing on the input query
        It replaces 'this month' with the current month name
                    'next year' with the next year
                    'yesterday' with the previous day's date
                    'day after/day after tomorrow' with 2 days from today's date
        Params:
            Input:
                query - str
                delta - str
                dayfirst - bool(true by default)[optional]
                monthfirst - bool(false by default)[optional]
                yearfirst - bool(false by default)[optional]
            Output:
                query - str
                delta - str
        """

        ptn = re.compile("(th|rd|st|nd)"
                         "(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|"
                         "august|aug|september|sept|sep|october|oct|november|nov|december|dec)")
        ptn = ptn.pattern.replace('\n', '').replace(' ', '')
        srch = re.search(ptn, query.lower())
        while srch:
            query = re.sub(srch.group(0), srch.group(1)+" "+srch.group(2), query, flags=re.I)
            srch = re.search(ptn, query)
        query = re.sub(r'\b(a day(s)?|a night(s)?)\b', '1 day', query, flags=re.I)
        query = re.sub(r'\b(a week(s))\b', '1 week', query, flags=re.I)
        query = re.sub(r'\b(a month(s)?)\b', '1 month', query, flags=re.I)
        query = re.sub(r'\b(a year(s)?)\b', '1 year', query, flags=re.I)
        
        query = list(_timelex(query))
        query = [each for each in query if each != ' ']
        query = ' '.join(query)
        query = ' '+query+' '
        
        query = self.fixed_delta_search(query)
        
        reg1 = regex.compile(r"""(?<!(january|jan|february|feb|march|mar|april|apr|may|
                             june|jun|july|jul|august|aug|september|sept|sep|october|
                             oct|november|nov|december|dec))(\s)
                             (\d+)(\s)
                             (\b(th|st|rd|nd)\b(\s))?
                             (-|\bto\b|\band\b|&)(\s)
                             (\d+)(\s)
                             (\b(th|st|rd|nd)\b(\s))?
                             (\bof\s\b)?
                             \b(january|jan|february|feb|march|mar|april|apr|may|june|
                             jun|july|jul|august|aug|september|sept|sep|october|oct|
                             november|nov|december|dec)\b""")
        reg1 = reg1.pattern.replace('\n', '').replace(' ', '')
        query = regex.sub(reg1, r" \3 th - \10 th \16 ", query, flags=re.I)

        reg2 = re.compile(r"""(?<!\d)(\s)
                          \b(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|
                          august|aug|september|sept|sep|october|oct|november|nov|december|dec)\b
                          (\s)(\d+)(\s)
                          (\b(th|st|rd|nd)\b(\s))?
                          (\bto\b|\band\b|-|&)(\s)
                          (\d+)(\s)
                          (\b(th|st|rd|nd)\b(\s))?
                          (?!(\.|:|\\|\/|-))""")
        reg2 = reg2.pattern.replace('\n', '').replace(' ', '')
        query = re.sub(reg2, r" \4 th - \11 th \2 ", query, flags=re.I)

        reg3 = re.compile(r"""(?<!(\d\s\.|\d\s:|\d\s\\|\d\s\/|\d\s-))(\s)
                          (\d+)(\s)(\bof\s\b)?\b(january|jan|february|feb|
                          march|mar|april|apr|may|june|jun|july|jul|august|aug|september|
                          sept|sep|october|oct|november|nov|december|dec)\b""")
        reg3 = reg3.pattern.replace('\n', '').replace(' ', '')
        query = re.sub(reg3, r" \3 th \6 ", query, flags=re.I)

        reg4 = regex.compile(r"""(?<!(\d\s|\bst\b\s|\bth\b\s|\brd\b\s|\bnd\b\s|\bof\b\s))
                             \b(january|jan|february|feb|march|mar|april|apr|may|june|jun|
                             july|jul|august|aug|september|sept|sep|october|oct|november|nov|
                             december|dec)\b(\s)(\d+)(\s)""")
        reg4 = reg4.pattern.replace('\n', '').replace(' ', '')
        query = regex.sub(reg4, r" \2 \4 th ", query, flags=re.I)

        query = self.date_format_reader(query, dayfirst, monthfirst, yearfirst)

        reg5 = re.compile(r"""(\d+)(\s+)?\b(nd|st|rd|th)\b(\s+)?
                          \b(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|
                          august|aug|september|sept|sep|october|oct|november|nov|december|dec|
                          of next month|next month|of this month|this month)\b
                          (\s+)?(\bto\b|\band\b|-)(\s+)?
                          (\d+)(\s+)?\b(nd|st|rd|th)\b(\s+)?
                          \b(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|
                          august|aug|september|sept|sep|october|oct|november|nov|december|dec|
                          of next month|next month|of this month|this month)\b(\s+)?(\d+)""")
        reg5 = reg5.pattern.replace('\n', '').replace(' ', '')
        query = re.sub(reg5, r"\1 \3 \5 \15 \7 \9 \11 \13 \15", query, flags=re.I)

        query = self.weekday_reader(query)

        this_year = datetime.datetime.now().year
        query = re.sub(r'(of this year|this year)', 'year ' + str(this_year), query, flags=re.I)
        
        next_year = datetime.datetime.now().year + 1
        query = re.sub(r'(of next year|next year)', 'year ' + str(next_year), query, flags=re.I)
        
        last_year = datetime.datetime.now().year - 1
        query = re.sub(r'(of (l|p)ast year|(l|p)ast year|of prev year|of previous year|prev year|previous year)',
                       'year ' + str(last_year), query, flags=re.I)
        print(query)
        
        this_month = datetime.datetime.now().strftime("%B")
        query = re.sub(r'(of this month|this month)', this_month, query, flags=re.I)
        
        next_month = (datetime.date.today() + relativedelta(months=1)).strftime("%B")
        query = re.sub(r'(of next month|next month)', next_month, query, flags=re.I)
        
        last_month = (datetime.date.today() - relativedelta(months=1)).strftime("%B")
        query = re.sub(r'(of last month|last month|of previous month|of prev month|previous month|prev month)',
                       last_month, query, flags=re.I)        
        
        temporal = [r'now', r'today', r'tonight', r'(?<!after\s)tomorrow', r'yesterday']
        days = re.findall(r'\b' + r'\b|\b'.join(temporal) + r'\b', query)
        if days:
            for day in days:
                if day == 'today' or day == 'now' or day == 'tonight':
                    query = query.replace(day, datetime.datetime.now().date().strftime("%d.%B.%Y"))
                if day == 'tomorrow':
                    query = re.sub(r'(?<!after\s)tomorrow', (datetime.date.today()
                                                             + relativedelta(days=1)).strftime("%d.%B.%Y"), query, flags=re.I)
                if day == 'yesterday':
                    query = query.replace(day, (datetime.date.today()
                                                - relativedelta(days=1)).strftime("%d.%B.%Y"))

        next_day = re.search(r'day after tomorrow|day after', query, re.I)
        if next_day:
            query = query[:next_day.span()[0]] + ((datetime.datetime.now()
                                                   + relativedelta(days=2)).date()).strftime("%d.%B.%Y") + query[next_day.span()[1]:]

        return (query, delta)

    def parse_dates(self, items, fin):

        """
        This is the main module that actually parses
        a list of relevant nmubers and month names into
        meaningful dates.
        Params:
            Input:
                items - list
                fin - final dictionary of dictionary
            Output:
                fin - final dictionary of dictionary
        """
        
        day1 = day2 = month1 = month2 = year1 = year2 = ''
        for ind, each in enumerate(items):            
            if each.isdigit():
                if int(each) < 32:
                    if day1 == '':
                        day1 = int(each)
                    elif day2 == '':
                        day2 = int(each)
                elif int(each) > 1000:
                    if year1 == '':
                        year1 = int(each)
                    elif year2 == '':
                        year2 = int(each)
            elif self.info.month(each):
                if month1 == '':
                    month1 = each
                elif month2 == '':
                    month2 = each            
            if ind == len(items) - 1:                
                if day1 == '' and month1 != '':
                    day1 = datetime.datetime.now().day
                if month1 == '':
                    month1 = datetime.datetime.now().strftime("%B")
                if year1 == '':
                    year1 = datetime.datetime.now().year
                if day1 != '' and month1 != '' and year1 != '':
                    item = ' '.join([str(day1), month1, str(year1)])
                    key = self.p.parse(item).date().strftime("%d.%B.%Y")
                    # print (key)
                    updt = {key:{"start date":'', "delta":'', "fin date":self.p.parse(item).date()}}
                    fin.update(updt)
                    if day2 != '':
                        if month2 != '':
                            if year2 != '':
                                item = ' '.join([str(day2), month2, str(year2)])
                            else:
                                year2 = year1
                                item = ' '.join([str(day2), month2, str(year2)])
                        else:
                            month2 = month1 if day1 <= day2 else (datetime.date(2000, self.info.month(month1), 1)
                                                                  + relativedelta(months=1)).strftime("%B")
                            year2 = year1 if self.info.month(month1) <= self.info.month(month2) else year1 + 1
                            item = ' '.join([str(day2), month2, str(year2)])
                        key = self.p.parse(item).date().strftime("%d.%B.%Y")
                        # print (key)
                        updt = {key:{"start date":'', "delta":'', "fin date":self.p.parse(item).date()}}
                        fin.update(updt)

        return fin

    def delta_srch(self, query, fin):

        """
        This module contains regex that catch delta
        eg:
            today plus 5 days
            a week from tomorrow
            yesterday + 2 weeks
        This delta is then added to 'start date' key
        and set in 'fin date' key of the fin dict
        The delta is also stored in 'delta' key of the fin dict
        Params:
            Input:
                query - str
                fin - final dictionary of dictionary
        """

        try:
            delta_reg = re.compile(r"""(\d{1,2}\.\w+\.\d{4})(\s+)?
                                   (\bplus\b|\bminus\b|-|\+)(\s+)?
                                   (\d+)(\s+)?(days|day|years|year|months|month)""")
            delta_reg = delta_reg.pattern.replace('\n', '').replace(' ', '')
            delta_search = re.search(delta_reg, query, re.I)
            while delta_search:
                start = delta_search.group(1)
                delta = delta_search.group(5)
                action = delta_search.group(3)
                fin[start]["start date"] = self.p.parse(start.replace('.', ' ')).date()
                if delta_search.group(7) in ['years', 'year']:
                    fin[start]["delta"] = str(delta) + " years"
                if delta_search.group(7) in ['months', 'month']:
                    fin[start]["delta"] = str(delta) + " months"
                if delta_search.group(7) in ['days', 'day']:
                    fin[start]["delta"] = str(delta) + " days"
                if action in ["plus", "+"]:
                    if delta_search.group(7) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(years=int(delta))).date()
                    if delta_search.group(7) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(months=int(delta))).date()
                    if delta_search.group(7) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(days=int(delta))).date()
                else:
                    if delta_search.group(7) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(years=int(delta))).date()
                    if delta_search.group(7) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(months=int(delta))).date()
                    if delta_search.group(7) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(days=int(delta))).date()
                query = re.sub(delta_reg, fin[start]["fin date"].strftime("%d %B %Y"), query, count=1, flags=re.I)
                delta_search = re.search(delta_reg, query, re.I)
                

            delta_reg = re.compile(r"""(\d+)(\s+)?(days|day|years|year|month|months)(\s+)?
                                   (\bfrom\b|\bafter\b|\bbefore\b)(\s+)?
                                   (\d{1,2}\.\w+\.\d{4})""")
            delta_reg = delta_reg.pattern.replace('\n', '').replace(' ', '')
            delta_search = re.search(delta_reg, query, re.I)
            while delta_search:
                start = delta_search.group(7)
                delta = delta_search.group(1)
                action = delta_search.group(5)
                fin[start]["start date"] = self.p.parse(start.replace('.', ' ')).date()
                if delta_search.group(3) in ['years', 'year']:
                    fin[start]["delta"] = str(delta) + " years"
                if delta_search.group(3) in ['months', 'month']:
                    fin[start]["delta"] = str(delta) + " months"
                if delta_search.group(3) in ['days', 'day']:
                    fin[start]["delta"] = str(delta) + " days"
                if action in ["from", "after"]:
                    if delta_search.group(3) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(years=int(delta))).date()
                    if delta_search.group(3) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(months=int(delta))).date()
                    if delta_search.group(3) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(days=int(delta))).date()
                else:
                    if delta_search.group(3) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(years=int(delta))).date()
                    if delta_search.group(3) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(months=int(delta))).date()
                    if delta_search.group(3) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(days=int(delta))).date()
                query = re.sub(delta_reg, fin[start]["fin date"].strftime("%d %B %Y"), query, count=1, flags=re.I)
                delta_search = re.search(delta_reg, query, re.I)

            
            delta_reg = re.compile(r"""(\d+)(\s+)\b(days|day|years|year|months|month)\b(\s+)
                                   \b(from|after|before)\b(\s+)
                                   (\d+){1,2}(\s+)
                                   \b(th|rd|st|nd|of)\b
                                   ((\s+)\b(january|jan|february|feb|march|mar|april|apr|may|
                                   june|jun|july|jul|august|aug|september|sept|sep|october|oct|
                                   november|nov|december|dec)\b
                                   ((\s+)(\d+))?)?""")
            delta_reg = delta_reg.pattern.replace('\n', '').replace(' ', '')
            delta_search = re.search(delta_reg, query, re.I)
            while delta_search:
                delta = int(delta_search.group(1))
                action = delta_search.group(5)
                day = int(delta_search.group(7))
                if delta_search.group(12):
                    month = self.info.month(delta_search.group(12))
                    if delta_search.group(15):
                        year = int(delta_search.group(15))
                        if year < 100:
                            future = year + (datetime.datetime.now().year//100*100)
                            past = year + (datetime.datetime.now().year/100*100 - 100)
                            now = datetime.datetime.now().year
                            if (now - past) < (future - now):
                                century = datetime.datetime.now().year//100*100 - 100
                            else:
                                century = datetime.datetime.now().year//100*100
                            year = year + century
                    else:
                        year = datetime.datetime.now().year
                else:
                    month = datetime.datetime.now().month
                    year = datetime.datetime.now().year
                if day and month and year:
                    start = datetime.datetime(year, month, day).strftime("%d.%B.%Y")
                fin[start]["start date"] = self.p.parse(start.replace('.', ' ')).date()
                if delta_search.group(3) in ['years', 'year']:
                    fin[start]["delta"] = str(delta) + " years"
                if delta_search.group(3) in ['months', 'month']:
                    fin[start]["delta"] = str(delta) + " months"
                if delta_search.group(3) in ['days', 'day']:
                    fin[start]["delta"] = str(delta) + " days"
                if action in ["from", "after"]:
                    if delta_search.group(3) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(years=int(delta))).date()
                    if delta_search.group(3) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(months=int(delta))).date()
                    if delta_search.group(3) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(days=int(delta))).date()
                else:
                    if delta_search.group(3) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(years=int(delta))).date()
                    if delta_search.group(3) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(months=int(delta))).date()
                    if delta_search.group(3) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(days=int(delta))).date()
                query = re.sub(delta_reg, fin[start]["fin date"].strftime("%d %B %Y"), query, count=1, flags=re.I)
                delta_search = re.search(delta_reg, query, re.I)
                

            delta_reg = re.compile(r"""(\d+){1,2}(\s+)
                                   \b(th|rd|st|nd|of)\b
                                   ((\s+)\b(january|jan|february|feb|march|mar|april|apr|may|
                                   june|jun|july|jul|august|aug|september|sept|sep|october|oct|
                                   november|nov|december|dec)\b((\s+)(\d+))?)?
                                   (\s+)(\bplus\b|\bminus\b|\+)(\s+)
                                   (\d+)(\s+)
                                   \b(days|day)\b""")
            delta_reg = delta_reg.pattern.replace('\n', '').replace(' ', '')
            delta_search = re.search(delta_reg, query, re.I)
            while delta_search:
                delta = int(delta_search.group(13))
                action = delta_search.group(11)
                day = int(delta_search.group(1))
                if delta_search.group(6):
                    month = self.info.month(delta_search.group(6))
                    if delta_search.group(9):
                        year = int(delta_search.group(9))
                        if year < 100:
                            future = year + (datetime.datetime.now().year//100*100)
                            past = year + (datetime.datetime.now().year//100*100 - 100)
                            now = datetime.datetime.now().year
                            if (now - past) < (future - now):
                                century = datetime.datetime.now().year//100*100 - 100
                            else:
                                century = datetime.datetime.now().year//100*100
                            year = year + century
                    else:
                        year = datetime.datetime.now().year
                else:
                    month = datetime.datetime.now().month
                    year = datetime.datetime.now().year
                if day and month and year:
                    start = datetime.datetime(year, month, day).strftime("%d.%B.%Y")
                fin[start]["start date"] = self.p.parse(start.replace('.', ' ')).date()
                fin[start]["delta"] = str(delta) + " days"
                if action in ["plus", "+"]:
                    if delta_search.group(15) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(years=int(delta))).date()
                    if delta_search.group(15) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(months=int(delta))).date()
                    if delta_search.group(15) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  + relativedelta(days=int(delta))).date()
                else:
                    if delta_search.group(15) in ['years', 'year']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(years=int(delta))).date()
                    if delta_search.group(15) in ['months', 'month']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(months=int(delta))).date()
                    if delta_search.group(15) in ['days', 'day']:
                        fin[start]["fin date"] = (self.p.parse(start.replace('.', ' '))
                                                  - relativedelta(days=int(delta))).date()
                query = re.sub(delta_reg, fin[start]["fin date"].strftime("%d %B %Y"), query, count=1, flags=re.I)
                delta_search = re.search(delta_reg, query, re.I)
        except KeyError:
            print("Restrucure your query")

        return query, fin

    def fixed_delta_search(self, query):
        # import pdb; pdb.set_trace()
        reg = re.compile(r"""((\bin\b|\bof\b)\s)?\b(last|prev(ious)?|since|from|past|next|coming)\b(\s)
                         ((\d+\s?(-|\bto\b)\s?)?(\d+))(\s)\b(y(ea)?r(s)?|month(s)?|day(s)?)\b
                         (?!\sfrom|\sbefore|\safter)""")
        reg = reg.pattern.replace('\n', '').replace(' ', '')
        reg_srch = re.search(reg, query, re.I)
        while reg_srch:
            delta = reg_srch.group(9)
            action = reg_srch.group(3)
            unit = reg_srch.group(11)
            if action in ['next', 'coming']:
                repl = ' '.join([delta, unit, 'from now'])
            else:
                repl = ' '.join([delta, unit, 'before now'])
            query = re.sub(reg, repl, query, count=1, flags=re.I)
            reg_srch = re.search(reg, query, re.I)
        return query
    
    def get_dates(self, input_query, dayfirst=True, monthfirst=False, yearfirst=False):

        """
        This module makes calls to all other modules
        It also performs some minor preprocessing
        Params:
            Input:
                input_query - str
                dayfirst - bool(true by default)[optional]
                monthfirst - bool(false by default)[optional]
                yearfirst - bool(false by default)[optional]
            Output:
                query - str
                fin - final dictionary of dictionary
        """

        query = input_query
        fin = {}
        delta = 0
        try:                
            query, delta = self.preprocess(query, delta, dayfirst, monthfirst, yearfirst)
            
            no_of_weeks = re.search(r'(\d+)(\s+)?(weeks|week)', query, re.I)
            while no_of_weeks:
                no_of_weeks = int(no_of_weeks.group(1))
                rep = str(no_of_weeks*7)+' days'
                query = re.sub(r'(\d+)(\s+)?(weeks|week)', rep, query, flags=re.I)
                no_of_weeks = re.search(r'(\d+)(\s+)?(weeks|week)', query, re.I)
                
            query = re.sub(r'(\d+)(\s+)?(nights|night)', r'\1 days', query, flags=re.I)            
                       
            items, query = self.timesplit(query)
            
            for item in items:                
                fin = self.parse_dates(item, fin)                         

            query, fin = self.delta_srch(query, fin)            

        except ValueError:
            print(traceback.format_exc())

        return fin, query

    def extract_data(self, query, dayfirst=True, monthfirst=False, yearfirst=False):

        """
        This module calls the get_dates module
        Params:
            Input:
                query - str
                dayfirst - bool(true by default)[optional]
                monthfirst - bool(false by default)[optional]
                yearfirst - bool(false by default)[optional]
            Output:
                query - fin
                dates - list of dictionaries. This is the final output
        """

        query = ' ' + query + ' '
        query = self.prep.word2nummain(query)
        dates, query = self.get_dates(query, dayfirst, monthfirst, yearfirst)
        try:
            dates = [v for k, v in dates.iteritems()]
            dates = [{k:v.strftime("%d %B %Y") if isinstance(v, datetime.date) else v for k, v in x.iteritems()} for x in dates]
        except AttributeError:
            dates = [v for k, v in dates.items()]
            dates = [{k:v.strftime("%d %B %Y") if isinstance(v, datetime.date) else v for k, v in x.items()} for x in dates]
        # pprint.pprint(dates)
        return dates, query

if __name__ == '__main__':
    OBJ = DateExtractor()
    DAYFIRST = True
    MONTHFIRST = False
    YEARFIRST = False
    while True:
        try:
            QUERY = raw_input("\nEnter: ")
        except NameError:
            QUERY = input("\nEnter: ")
        START_TIME = datetime.datetime.now()
        if QUERY == 'exit':
            break
        DATES, QUERY = OBJ.extract_data(QUERY, DAYFIRST, MONTHFIRST, YEARFIRST)
        END_TIME = datetime.datetime.now()
        print(END_TIME - START_TIME)
        print(QUERY)
        pprint.pprint(DATES)
