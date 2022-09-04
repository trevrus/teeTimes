import datetime

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

from datetime import date, timedelta

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
        "num_players_code": None
    },
    {
        "name": "Fraserview",
        "url_to_date": "https://secure.west.prophetservices.com/CityofVancouver/Home/nIndex?CourseId=2&Date=",
        "url_after_date_to_players": "&Time=AnyTime&Player=99&Hole=18",
        "outer_wrapper_selector": "div.divBoxText",
        "tee_time_selector": "span",
        "test_path": "test_files/langara.html",
        "num_players_code": None

    },
    {
        "name": "McCleery",
        "url_to_date": "https://secure.west.prophetservices.com/CityofVancouver/Home/nIndex?CourseId=3&Date=",
        "url_after_date_to_players": "&Time=AnyTime&Player=99&Hole=18",
        "outer_wrapper_selector": "div.divBoxText",
        "tee_time_selector": "span",
        "test_path": "test_files/langara.html",
        "num_players_code": None

    },
    {
        "name": "Burnaby Mtn",
        "url_to_date": "https://city-of-burnaby-golf.book.teeitup.com/?course=17605&date=",
        "url_after_date_to_players": "",
        "outer_wrapper_selector": "body#app-body div#app-container  div.jss123",
        "tee_time_selector": "p",
        "test_path": "test_files/bby_mtn.html",
        "num_players_code": None
    }

]

course_groups = {

        "city":     ["Langara", "Fraserview", "McCleery"],
        "GVRD":     ["Burnaby Mtn", "Riverway", "University", "Greenacres", "Westwood", "Langara", "Fraserview", "McCleery"],
        "valley":   ["Redwoods", "Belmont", "Fort Langley", "Hazelmere", "Swaneset", "Northview"],
        "wcgg":     ["Belmont", "Hazelmere", "Swaneset"]
    }


class Course:
    # name: str
    # url_to_date: str
    # url_after_date_to_players: str
    # num_players_code: int

    def __init__(self, name, url_to_date, url_after_date_to_players,
                 outer_wrapper_selector, tee_time_selector, test_path, num_players_code=None):
        self.name = name
        self.url_to_date = url_to_date
        self.url_after_date_to_players = url_after_date_to_players
        self.outer_wrapper_selector = outer_wrapper_selector
        self.tee_time_selector = tee_time_selector
        self.test_path = test_path
        self.num_players_code = num_players_code

    # url constructor
    def construct_url(self, date, num_players):
        full_url: str = self.url_to_date + date + self.url_after_date_to_players
        # players_code = ""
        if self.num_players_code is None:
            print("no num_players_code")
        else:
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

    def new_course(self):
        this_course = next(item for item in courses if item["name"] == self.course_name)

        course = Course(
            this_course["name"],
            this_course["url_to_date"],
            this_course["url_after_date_to_players"],
            this_course["outer_wrapper_selector"],
            this_course["tee_time_selector"],
            this_course["test_path"],
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
        proxies = {'http': 'http://208.113.134.223'}

        # set up user agent headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15"}

        response = requests.get(url, proxies=proxies, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # print(self.course)
        full_tee_times = soup.select(self.course.outer_wrapper_selector)
        times = []
        for t in full_tee_times:
            times.append(t.select_one(self.course.tee_time_selector).text)
        return times

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

    def __init__(self, course_list: [], dates: [], players=2):
        self.course_list = course_list
        self.dates = dates
        self.players = players

    def get_times_for_course(self, course, date) -> []:
        booking = Booking(course, self.players, date)
        return booking.find_times()

    def all_times_for_all_courses_on_all_dates(self):
        # June 3: Langara(12:10, 12:15, 1:45), Fraserview(8:37, 14:52)
        # [{dates: [{course: [times]}]}]
        these_dates = []
        for d in self.dates:
            courses = []
            these_dates.append({d: courses})
            for c in self.course_list:
                times = self.get_times_for_course(c, d)
                courses.append({c: times})
        return these_dates

    def course_group(self, group: str, dates):
        pass

    def course_group_this_saturday(self, group):
        pass

    def all_courses_this_saturday(self):
        pass

    def next_5_saturdays(self):
        pass



# Returns formatted text


class Formatter:
    def __init__(self):
        pass


#             time = t.find(class_="timeDiv").find('span').text
#             location = t.find('p').text
#             # print(time + " at " + location)

base_path = Path(__file__).parent
bby_file_path = (base_path / "test_files/bby_mtn.html").resolve()
langara_file_path = (base_path / "test_files/langara.html").resolve()

test = Search(["Langara", "Fraserview"],["2022-09-05", "2022-09-06"])
print(test.all_times_for_all_courses_on_all_dates())
print(course_groups["city"])

# book = Booking("Burnaby Mtn", 3, "2022-09-05")
# print(book.get_url())
# print(book.test_find_times())

# book = Booking("Langara", 2, "2022-09-05")
# print(book.get_url())
# # print(book.test_find_times(langara_file_path))
# print(book.find_times())

# ---------------IP has been blocked!!!------------------
# accidentally used van golf tags
# book = Booking(bby_mtn, 3, "2022-09-02")
# print(book.get_url())
# print(book.find_times())


# https://www.chronogolf.ca/club/university-golf-club#?date=2022-09-05&course_id=525&nb_holes=18&affiliation_type_ids=2897,2897
# class="widget-teetimes"
# <div class="widget-teetime-tag ng-binding" ng-class="{ active : vm.teetime.id == vm.selectedTeetime.id }">
#     6:40 PM
#   </div>
# uni = Course("University Golf", "https://www.chronogolf.ca/club/university-golf-club#?date=",
#     "&course_id=525&nb_holes=18&affiliation_type_ids=", 2897)

# print(bby_mtn.name)
# print(bby_mtn.url_after_date_to_players)
# print(bby_mtn.construct_url("2022-09-05", 3))

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
# i = 0
# while i < 30:
#     today = date.today()
#     current_day: date = today + timedelta(i)
#     if datetime.datetime.weekday(current_day) == 5:
#         url = "https://secure.west.prophetservices.com/CityofVancouver/Home/nIndex?CourseId=2,1,3&Date=" + str(
#             current_day) + "&Time=AnyTime&Player=99&Hole=18"
#         # print(i)
#         # print(url)
#         response = requests.get(url)
#
#         soup = BeautifulSoup(response.text, "html.parser")
#
#         langara = []
#         fraserview = []
#         mccleery = []
#
#         print(current_day.strftime('%A'))
#         print(datetime.datetime.weekday(current_day))
#         print(current_day)
#
#         fullTeeTimes = soup.findAll(class_="divBoxText")
#
#     # print([t.span.text for t in times])
#         for t in fullTeeTimes:
#             time = t.find(class_="timeDiv").find('span').text
#             location = t.find('p').text
#             # print(time + " at " + location)
#             if location == "Langara GC":
#                 langara.append(time)
#             elif location == "McCleery GC":
#                 mccleery.append(time)
#             elif location == "Fraserview GC":
#                 fraserview.append(time)
#         # print(date.today())
#         print("Langara Times: " + str(len(langara)))
#
#         # print([t for t in langara])
#
#         print([t for t in good_times(langara)])
#
#         print("Fraserview Times: " + str(len(fraserview)))
#         # print([t for t in fraserview])
#         print([t for t in good_times(fraserview)])
#
#         print("McCleery Times: " + str(len(mccleery)))
#         # print([t for t in mccleery])
#         print([t for t in good_times(mccleery)])
#         print('\n')
#
#
#     i += 1
