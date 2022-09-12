import datetime

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

from datetime import date, timedelta, datetime

# next 10 days
# for each day
# print date
# list course
# print good times
#
# be able to select desired date and list all times at all courses

# today_str = str(date.today())

# items needed for each course:
#     url start and end with variable for date
#     code that represents players in group
#     html tags and class/id for time

courses = [
    {
        "name": "Langara",
        "url_to_date": "https://secure.west.prophetservices.com/CityofVancouver/Home/nIndex?CourseId=1&Date=",
        "url_after_date_to_players": "&Time=AnyTime&Player=99&Hole=18",
        "outer_wrapper_selector": "div.divBoxText",
        "tee_time_selector": "span",
        "test_path": "test_files/langara.html",
        "max_advance": 30,
        "num_players_code": None
    },
    {
        "name": "Fraserview",
        "url_to_date": "https://secure.west.prophetservices.com/CityofVancouver/Home/nIndex?CourseId=2&Date=",
        "url_after_date_to_players": "&Time=AnyTime&Player=99&Hole=18",
        "outer_wrapper_selector": "div.divBoxText",
        "tee_time_selector": "span",
        "test_path": "test_files/langara.html",
        "max_advance": 30,
        "num_players_code": None

    },
    {
        "name": "McCleery",
        "url_to_date": "https://secure.west.prophetservices.com/CityofVancouver/Home/nIndex?CourseId=3&Date=",
        "url_after_date_to_players": "&Time=AnyTime&Player=99&Hole=18",
        "outer_wrapper_selector": "div.divBoxText",
        "tee_time_selector": "span",
        "test_path": "test_files/langara.html",
        "max_advance": 30,
        "num_players_code": None

    },
    {
        "name": "Burnaby Mtn",
        "url_to_date": "https://city-of-burnaby-golf.book.teeitup.com/?course=17605&date=",
        "url_after_date_to_players": "",
        "outer_wrapper_selector": "body#app-body div#app-container  div.jss123",
        "tee_time_selector": "p",
        "test_path": "test_files/bby_mtn.html",
        "max_advance": 3,
        "num_players_code": None
    }

]

course_groups = {

        "city":     ["Langara", "Fraserview", "McCleery"],
        "GVRD":     ["Burnaby Mtn", "Riverway", "University", "Greenacres", "Westwood", "Langara", "Fraserview", "McCleery"],
        "valley":   ["Redwoods", "Belmont", "Fort Langley", "Hazelmere", "Swaneset", "Northview"],
        "wcgg":     ["Belmont", "Hazelmere", "Swaneset"]
    }

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class Course:
    # name: str
    # url_to_date: str
    # url_after_date_to_players: str
    # num_players_code: int

    def __init__(self, name, url_to_date, url_after_date_to_players,
                 outer_wrapper_selector, tee_time_selector, test_path, max_advance, num_players_code=None):
        self.name = name
        self.url_to_date = url_to_date
        self.url_after_date_to_players = url_after_date_to_players
        self.outer_wrapper_selector = outer_wrapper_selector
        self.tee_time_selector = tee_time_selector
        self.test_path = test_path
        self.max_advance = max_advance
        self.num_players_code = num_players_code

    # url constructor
    def construct_url(self, date, num_players):
        full_url: str = self.url_to_date + date + self.url_after_date_to_players
        # players_code = ""
        if self.num_players_code is not None:
            full_url += self.format_players(num_players)
        return full_url

    # Format the url query string based on number of players; repeats a code(num_players_code) x times
    def format_players(self, num_players):
        code = str(self.num_players_code)
        players_str = ""
        for i in range(num_players):
            players_str += code + ","
            i += 1
        # remove last comma and return
        return players_str[:-1]


class Booking:
    course: Course

    def __init__(self, course_name: str, players: int, date_of_play: str):
        self.course_name = course_name
        self.players = players
        # self.time_selection = time_selection
        self.date_of_play = date_of_play
        self.course = self.new_course()
        self.tee_times = []
    def new_course(self):
        this_course = next(item for item in courses if item["name"] == self.course_name)

        course = Course(
            this_course["name"],
            this_course["url_to_date"],
            this_course["url_after_date_to_players"],
            this_course["outer_wrapper_selector"],
            this_course["tee_time_selector"],
            this_course["test_path"],
            this_course["max_advance"],
            this_course["num_players_code"]
        )
        return course

    def get_url(self):
        return self.course.construct_url(self.date_of_play, self.players)

    def find_times(self):
        url = self.get_url()
        # trying to not be detected as a bot
        # set up a proxy
        # find on https://free-proxy-list.net
        proxies = {'http': '130.41.55.190'}

        # set up user agent headers
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8",
            "Referer": "https: // www.google.com /",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15",
            "X-Amzn-Trace-Id": "Root=1-6316ba40-43cb593b411688715f5a55de"
            }
        print(url)
        response = requests.get(url, proxies=proxies, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup)
        full_tee_times = soup.select(self.course.outer_wrapper_selector)
        times = []
        for t in full_tee_times:
            self.tee_times.append(t.select_one(self.course.tee_time_selector).text)
        return self

    def test_find_times(self):

        # url = path
        # page =open(url)
        # soup = BeautifulSoup(page.read(), "html.parser")

        with open(self.course.test_path) as fp:
            soup = BeautifulSoup(fp, "html.parser")

        full_tee_times = soup.select(self.course.outer_wrapper_selector)

        times = []
        for t in full_tee_times:
            times.append(t.select_one(self.course.tee_time_selector).text)
        print(len(times))
        return times


# Takes a list of courses that you want to search
# It takes a list of the day/s that you want to search
# It scrapes the appropriate sites and fetches the data
# It prints the formatted output


class Search:

    def __init__(self, players=2):
        self.players = players

    def _get_times_for_course(self, course, date) -> []:
        if date is not str:
            date = str(date)
        booking = Booking(course, self.players, date)
        return booking.find_times()

    def all_times_for_courses_on_dates(self, course_list: [], dates: []):
        these_dates_tee_times = []
        # [{date: [Booking()]}]
        for d in dates:
            bookings = []
            these_dates_tee_times.append({d: bookings})
            for c in course_list:
                booking = self._get_times_for_course(c, d)
                bookings.append(booking)
        return these_dates_tee_times




    def course_group_times(self, group: str, dates):
        search_group = course_groups[group]
        return self.all_times_for_courses_on_dates(search_group, dates)

    def course_group_times_this_saturday(self, group):
        return self.course_group_times(group, [self.this_saturday()])

    def all_courses_times_this_saturday(self):
        return self.all_times_for_courses_on_dates(courses, [self.this_saturday()])

    def get_date_n_days(self, num_days):
        future_date = date.today() + timedelta(num_days)
        print(future_date.strftime("%A, %B %d, %Y"))
        return future_date

    def int_weekday_in_n_days(self, num_days):
        today = date.today()
        today_int = datetime.weekday(today)
        return (today_int + num_days) % 7

    def next_weekday_occurance_after_n_days(self, weekday: str, num_days):
        day = weekdays.index(weekday)
        weekday_in_n_days = self.int_weekday_in_n_days(num_days)
        today = date.today()
        days_from_n_days = (day - weekday_in_n_days) % 7
        print(days_from_n_days)
        return today + timedelta(num_days + days_from_n_days)

    def get_date_to_advance_book(self, weekday, num_days_advance):
        date_to_book = self.next_weekday_occurance_after_n_days(weekday, num_days_advance)
        return date_to_book - timedelta(num_days_advance)

    def days_til_next(self, weekday: str):
        today = date.today()
        day_int = datetime.weekday(today)
        return (weekdays.index(weekday) - day_int) % 7

    def this_saturday(self):
        return date.today() + timedelta(self.days_til_next("Saturday"))

    def next_n_saturdays(self, n):
        saturdays = []
        this_saturday = self.this_saturday()
        for s in range(n):
            next_saturday = this_saturday + timedelta(s * 7)
            saturdays.append(next_saturday)
        return saturdays




# Returns formatted text

class Formatter:
    def __init__(self, search):
        self.results = search

    def for_console(self):
        results = self.results
        for r in results:
            [this_date] = list(r.keys())
            print()
            # Date string to date type
            date_time = datetime.strptime(this_date, '%Y-%m-%d')
            print(date_time.strftime("%A, %B %d, %Y"))
            [these_bookings] = list(r.values())
            for b in these_bookings:
                print(b.course_name)
                print(', '.join(b.tee_times))
        # print(these_dates)
        # print(these_bookings)


search = Search()
search.get_date_n_days(3)
search.next_weekday_occurance_after_n_days("Monday", 33)
print(f'this saturday is:',search.this_saturday())
print(f'days till next Saturday:',search.days_til_next("Saturday"))
print(f'weekday int in 1 day:', search.int_weekday_in_n_days(1))
print(f'next Saturday after 30 days:', search.next_weekday_occurance_after_n_days("Saturday", 30))
print(f'Date to book the next Saturday 30 days out:', search.get_date_to_advance_book("Saturday", 3))

# search = Search()
# this_search = search.course_group_times("city", ["2022-09-15", "2022-09-16"])
# format = Formatter(this_search)
# print(format.for_console())

# for test files of saved source code
# base_path = Path(__file__).parent
# bby_file_path = (base_path / "test_files/bby_mtn.html").resolve()
# langara_file_path = (base_path / "test_files/langara.html").resolve()


# book = Booking("Burnaby Mtn", 3, "2022-09-05")
# print(book.get_url())
# print(book.test_find_times())



# https://www.chronogolf.ca/club/university-golf-club#?date=2022-09-05&course_id=525&nb_holes=18&affiliation_type_ids=2897,2897
# class="widget-teetimes"
# <div class="widget-teetime-tag ng-binding" ng-class="{ active : vm.teetime.id == vm.selectedTeetime.id }">
#     6:40 PM
#   </div>
# uni = Course("University Golf", "https://www.chronogolf.ca/club/university-golf-club#?date=",
#     "&course_id=525&nb_holes=18&affiliation_type_ids=", 2897)

# print(uni.construct_url("2022-09-05", 3))

#
# def good_times(times):
#     earliest_time = 9
#     latest_time = 14
#     good = []
#     for time in times:
#         realtime = datetime.datetime.strptime(time, '%H:%M').time()
#         if datetime.time(latest_time, 00) > realtime > datetime.time(earliest_time, 00):
#             good.append(time)
#
#     return good
#
#
