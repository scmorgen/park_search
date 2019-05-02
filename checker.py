#!/usr/bin/env python
"""This is a script for checking recreation.gov and reserveCalifornia.

To use you will need the selenium chrome driver for your version of chrome.
See instructions on how to install here: http://chromedriver.chromium.org/downloads

pip install virtualenv
virtualenv checker_env
checker_env/bin/install -r requirements.txt
"""
from __future__ import print_function
import datetime
import difflib
from functools import wraps
import json
import os
import re
import time
import multiprocessing as mp
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import ui
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common import keys
    from selenium.common import exceptions
    from selenium.webdriver.common.action_chains import ActionChains
    import fire
except ImportError as err:
    raise RuntimeError("One or more libraries are not installed. 'pip install -r requirements.txt' "
                       "to ensure environment is set up. Err: {}".format(str(err)))

BATCH_NUMBER = 5

CHROME_DRIVER_LOCATION = "/Users/soja-mariemorgens/python_projects/recreation_gov_checkert/chromedriver"
CALIFORNIA_URL = "https://www.reservecalifornia.com/CaliforniaWebHome/"
NATIONAL_URL_TEMPLATE = "https://www.recreation.gov/camping/campgrounds/{}/availability"

ALL_SITES_DICT = {
    "Wawona(Yosemite)": {"url": NATIONAL_URL_TEMPLATE.format(232446), "tags": ["yosemite", "weekend"]},
    "Hodgdon Meadows(Yosemite)": {"url": NATIONAL_URL_TEMPLATE.format(232451), "tags": ["yosemite", "weekend"]},
    "North Pines(Yosemite)": {"url": NATIONAL_URL_TEMPLATE.format(232449), "tags": ["yosemite", "weekend"]},
    "Lower Pines(Yosemite)": {"url": NATIONAL_URL_TEMPLATE.format(232450), "tags": ["yosemite", "weekend"]},
    "Upper Pines(Yosemite)": {"url": NATIONAL_URL_TEMPLATE.format(232447), "tags": ["yosemite", "weekend"]},
    "Tuolomne Meadows(Yosemite)": {"url": NATIONAL_URL_TEMPLATE.format(232448), "tags": ["yosemite", "weekend"]},
    "Crane Flat(Yosemite)": {"url": NATIONAL_URL_TEMPLATE.format(232452), "tags": ["yosemite", "weekend"]},
    "Dimond O(HetchHetchy)": {"url": NATIONAL_URL_TEMPLATE.format(233772), "tags": ["yosemite", "weekend"]},
    "South Campground(Zion)": {"url": NATIONAL_URL_TEMPLATE.format(272266), "tags": ["utah", "zion"]},
    "Watchman's Campground(Zion)": {"url": NATIONAL_URL_TEMPLATE.format(232445), "tags": ["utah", "zion"]},
    "Devil's Garden Campground (Arches)": {"url": NATIONAL_URL_TEMPLATE.format(234059), "tags": ["utah", "arches"]},
    "Needles District (Canyonlands)": {"url": NATIONAL_URL_TEMPLATE.format(251535), "tags": ["utah", "canyonlands"]},
    "Fruita Campground (Capitol Reef)": {"url": NATIONAL_URL_TEMPLATE.format(272245), "tags": ["utah", "capitol_reef"]},
    "Mather's Campground (Grand Canyon)": {"url": NATIONAL_URL_TEMPLATE.format(232490), "tags": ["utah", "grand_canyon", "south_rim"]},
    "North Rim Campground (Grand Canyon)": {"url": NATIONAL_URL_TEMPLATE.format(232489), "tags": ["utah", "grand_canyon", "north_rim"]},
    "Demotte (NR Grand Canyon)": {"url": NATIONAL_URL_TEMPLATE.format(234722), "tags": ["utah", "grand_canyon", "north_rim"]},
    "Ten-X Campground (Grand Canyon)": {"url": NATIONAL_URL_TEMPLATE.format(234488), "tags": ["utah", "grand_canyon", "north_rim"]},
    "Bicentenniel(Marin Headlands)": {"url": NATIONAL_URL_TEMPLATE.format(272229), "tags": ["weekend", "north_bay"]},
    "Kirby Cove(SF)": {"url": NATIONAL_URL_TEMPLATE.format(232491), "tags": ["weekend", "north_bay"]},
    "Point Reyes": {"url": NATIONAL_URL_TEMPLATE.format(233359), "tags": ["weekend", "point_reyes", "north_bay"]},
    "Samuel P. Taylor SP": {"url": CALIFORNIA_URL, "tags": ["weekend", "north_bay"]},
    "China Camp SP": {"url": CALIFORNIA_URL, "tags": ["weekend", "north_bay"]},
    "Mount Tamalpais SP": {"url": CALIFORNIA_URL, "tags": ["weekend", "north_bay"]},
    "Angel Island SP": {"url": CALIFORNIA_URL, "tags": ["weekend", "north_bay"]},
    "Henry Cowell Redwoods": {"url": CALIFORNIA_URL, "tags": ["weekend", "santa_cruz"]},
    "Plaskett Creek Campground(Big Sur)": {"url": NATIONAL_URL_TEMPLATE.format(231959), "tags": ["weekend", "big_sur"]},
    "Kirk Creek Campground(Big Sur)": {"url": NATIONAL_URL_TEMPLATE.format(233116), "tags": ["weekend", "big_sur"]},
    "Limekiln SP": {"url": CALIFORNIA_URL, "tags": ["weekend", "big_sur"]},
    "Pfeiffer": {"url": CALIFORNIA_URL, "tags": ["weekend", "big_sur"]},
    "Pfeiffer Big Sur": {"url": CALIFORNIA_URL, "tags": ["weekend", "big_sur"]},
    "Arroyo Seco (Los Padres)": {"url": NATIONAL_URL_TEMPLATE.format(231958), "tags": ["weekend", "big_sur"]},
    "Wishon Point (Bass Lake)": {"url": NATIONAL_URL_TEMPLATE.format(232911), "tags": ["bass_lake"]},
    "Cedar Bluff (Bass Lake)": {"url": NATIONAL_URL_TEMPLATE.format(232912), "tags": ["bass_lake"]},
    "Forks Campground (Bass Lake)": {"url": NATIONAL_URL_TEMPLATE.format(232878), "tags": ["bass_lake"]},
    "Spring Cover (Bass Lake)": {"url": NATIONAL_URL_TEMPLATE.format(232801), "tags": ["bass_lake"]},
    "Big Basin": {"url": CALIFORNIA_URL, "tags": ["weekend", "big_basin"]},
    "Little Basin": {"url": CALIFORNIA_URL, "tags": ["weekend", "big_basin"]},
    "Seacliff SB": {"url": CALIFORNIA_URL, "tags": ["weekend", "beach", "santa_cruz", "hwy1"]},
    "Manresa SB": {"url": CALIFORNIA_URL, "tags": ["weekend", "beach", "santa_cruz", "hwy1"]},
    "Sunset SB": {"url": CALIFORNIA_URL, "tags": ["weekend", "beach", "santa_cruz", "hwy1"]},
    "Half Moon Bay SB": {"url": CALIFORNIA_URL, "tags": ["weekend", "beach", "hwy1"]},
    "Russian Gulch": {"url": CALIFORNIA_URL, "tags": ["beach", "hwy1", "north_hwy1", "rg"]},
    "Van Damme": {"url": CALIFORNIA_URL, "tags": ["weekend", "northern_cal", "hwy1", "north_hwy1"]},
    "Prairie Creek Redwoods SP Elk": {"url": CALIFORNIA_URL, "tags": ["weekend", "northern_cal", "hwy1", "north_hwy1"]},
    "Prairie Creek Redwoods SP Gold": {"url": CALIFORNIA_URL, "tags": ["weekend", "northern_cal", "hwy1", "north_hwy1"]},
    "Patricks Point SP": {"url": CALIFORNIA_URL, "tags": ["northern_cal", "hwy1", "north_hwy1"]},
    "Mackerricher SP": {"url": CALIFORNIA_URL, "tags": ["northern_cal", "hwy1", "north_hwy1"]},
    "Grizzly Creek Redwoods SP": {"url": CALIFORNIA_URL, "tags": ["northern_cal"]},
    "Humboldt Redwoods SP": {"url": CALIFORNIA_URL, "tags": ["northern_cal"]},
}

NUM_PARALLEL_JOB = 5  # I dont recommend above 5 if using reservecalifornia
SLEEP_BETWEEN_JOBS = 20  # I dont recommend below 20
CAMPSITE_URL = "https://www.recreation.gov/camping/campsites/"
OUTPUT_FILE = "availability_{}_{}_to_{}.txt"

# Recreation.gov variables
DATE_PICKER_ID = "single-date-picker"
LOAD_MORE_XPATH = '//*[@id="rec-campground-availability-main"]/div[2]/div[4]/div[2]/div/button'
ROW_PATH = '//*[@id="availability-table"]/tbody/tr'
ANOTHER_XPATH = '//*[@id="campsite-filter-search"]'

# Reserve California variables
# First Page
SITE_PICKER_ID = "txtSearchparkautocomplete"
DATE_ARRIVAL_ID = "mainContent_txtArrivalDate"
NUMBER_OF_NIGHTS_ID = "ddlHomeNights"
DROPDOWN_TYPE_ID = "ddl_homeCategories"
DROPDOWN_CAMPING_TYPE = "ddl_homeCampingUnit"

# Second Page
DATE_ARRIVAL_ID2 = "mainContent_SearchUnitAvailbity_txtArrivalDate"
SEND_BUTTON_XPATH = '//*[@id="divMainSearchControl"]/div[1]/div[4]/div/a'
SECOND_SITE_PICKER_ID = "txtCityParkSearch"
SECOND_SEND_BUTTON_XPATH = '//*[@id="divPlaceSearchParameter"]/div/div[2]/div[1]/div[4]/a'
SECOND_AVAILABILITY_ROW_PATH = '//*[@id="divUnitGridlist"]/div/table/tbody/tr'

YEAR = 2019


def retry(exception_to_check, tries=2, delay=.2, dont_raise_error=False):
    """Retry calling the function if there is an error.

    Args:
        exception_to_check(Exception): the exception or tuple of them to check
        tries (int): number of times to try (not retry) before giving up
        delay (float): initial delay between retries in seconds
        dont_raise_error(bool): don't raise final_error
    """
    def deco_retry(func):
        @wraps(func)
        def func_retry(*args, **kwargs):
            for _ in range(tries - 1):
                try:
                    return func(*args, **kwargs)
                except exception_to_check:
                    # msg = "Warning: %s. Retrying..." % (str(e))
                    # print(msg)
                    time.sleep(delay)
            try:
                return func(*args, **kwargs)
            except exception_to_check as err:
                if dont_raise_error:
                    msg = "Warning: %s. Not retrying." % (str(err))
                    print(msg)
                else:
                    raise err

        return func_retry  # true decorator

    return deco_retry


def _get_date_list(year, start_tuple, end_tuple, weekday=None):
    weekdays_dict = {"saturday": 5,
                     "sunday": 6,
                     "monday": 0,
                     "tuesday": 1,
                     "wednesday": 2,
                     "thursday": 3,
                     "friday": 4}
    delta = 1
    dates = []
    day = datetime.date(year,
                        int(start_tuple[0]),
                        int(start_tuple[1]))
    if weekday:
        if weekday.lower() not in weekdays_dict:
            raise ValueError(
                "weekday {} is not recognized. Possible: {}".format(
                    weekday, weekdays_dict.keys()))

        day += datetime.timedelta(days=weekdays_dict[weekday.lower()] - day.weekday())
        delta = 7

    while day <= datetime.date(year, int(end_tuple[0]), int(end_tuple[1])):
        dates.append(day.strftime('%m-%d-%Y'))
        day += datetime.timedelta(days=delta)
    return dates


def get_valid_tags():
    tags = []
    for _, value in ALL_SITES_DICT.items():
        tags += value["tags"]
    return list(set(tags))


def get_sites_dict_from_tag(tag):
    sites_dict = {}
    for site, value in ALL_SITES_DICT.items():
        if tag in value['tags']:
            sites_dict[site] = value["url"]
    return sites_dict


def get_sites_dict(tag, park):
    if park:
        if park not in ALL_SITES_DICT.keys():
            raise ValueError(
                "park {} not in parks. Closest match: {}".format(
                    park, difflib.get_close_matches(
                        park, ALL_SITES_DICT.keys())))
        return {park: ALL_SITES_DICT[park]['url']}, park
    valid_tags = get_valid_tags()
    if tag not in valid_tags:
        raise ValueError(
            "tag {} not found. Closest match: {}".format(
                tag, difflib.get_close_matches(
                    tag, valid_tags)))
    return get_sites_dict_from_tag(tag), tag


def check_one_date(date, tag="yosemite", park=None, output_file=None):
    if not re.match(r"\d+-\d+", str(date)):
        raise ValueError("expecting date to look like this: 5-11")
    dates = [date + "-" + str(YEAR)]
    sites_dict, tag = get_sites_dict(tag, park)
    if not output_file:
        output_file = OUTPUT_FILE.format(tag, date, date)
    available = check_sites(dates, sites_dict)
    _print_to_file(available, output_file)


def check_date_range(start_date="8-20", end_date="9-1",
                     tag="yosemite", park=None, output_file=None, weekday=None):
    if not re.match(r"\d+-\d+", str(start_date)) and re.match(r"\d+-\d+", str(end_date)):
        raise ValueError("Expecting date to look like this: 5-11")
    dates = _get_date_list(YEAR, start_date.split("-"), end_date.split("-"), weekday)
    sites_dict, tag = get_sites_dict(tag, park)
    if not output_file:
        output_file = OUTPUT_FILE.format(tag, start_date, end_date)
    available = check_sites(dates, sites_dict)
    _print_to_file(available, output_file)


def check_saturdays_in_range(start_date="8-20", end_date="9-1",
                             tag="yosemite", output_file=None):
    check_date_range(start_date, end_date, tag, output_file, weekday="saturday")


def check_sites(dates_list, sites_dict):
    start_time = time.time()
    if not os.path.exists(CHROME_DRIVER_LOCATION):
        raise ValueError("{} is not a viable location for the chrome driver."
                         " Please change CHROME_DRIVER_LOCATION in this script to point to your chrome driver."
                         "You can download the Chrome Driver here: http://chromedriver.chromium.org/downloads")

    manager = mp.Manager()
    available_sites = manager.dict()
    available_sites = {date: [] for date in dates_list}

    jobs = []
    sites = sorted(sites_dict.keys())
    print("Checking dates {}".format(", ".join(dates_list)))

    # Runs up to NUM_PARALLEL_JOB in parallel and returns results in a dictionary
    batches = [sites[i:i + NUM_PARALLEL_JOB] for i in range(0, len(sites), NUM_PARALLEL_JOB)]
    for a_batch in batches:
        print("Checking {}".format(", ".join(a_batch)))
        queue_end = mp.Queue()
        for name in a_batch:

            proc = mp.Process(
                target=_subprocess_check_site, args=(
                    name, sites_dict[name], dates_list, queue_end))
            jobs.append(proc)
            proc.start()
        start_time = time.time()
        end_time = start_time + 2 * 60  # Ensure processes dont hang
        while time.time() < end_time:
            if not any(proc.is_alive() for proc in jobs):
                break
            time.sleep(.5)
        for proc in jobs:
            proc.terminate()
            proc.join()
        while not queue_end.empty():
            try:
                a_dict = json.loads(queue_end.get(timeout=1))
                for date, a_list in a_dict.iteritems():
                    available_sites[date] += a_list
            except Exception:
                pass

        print("Sleeping 20s between batches to slow down calls")
        time.sleep(SLEEP_BETWEEN_JOBS)
    total_time = time.time() - start_time
    print("This took {} min".format(int(total_time / 60)))
    return available_sites


def _subprocess_check_site(name, url, dates_list, send_end):
    try:
        driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
        date_availability = {date: [] for date in dates_list}
        a_dict = {}
        if "recreation" in url:
            driver.get(url)
            a_dict = _check_gov_sites(
                driver, name, dates_list, date_availability)

        else:

            for date in dates_list:
                driver.get(url)
                a_dict = _check_california_sites(
                    driver, name, date, date_availability)

    finally:
        driver.close()
        driver.quit()
        send_end.put(json.dumps(a_dict))


def _check_california_sites(driver, name, date, available_sites):
    # Starting page
    time.sleep(.2)
    _enter_value(driver, SITE_PICKER_ID, name, select_on_dropdown=True)
    time.sleep(1)
    for i in ["Camping", "Remote Camping"]:
        try:
            _select_dropdown_visible_text(driver, DROPDOWN_TYPE_ID, i)
        except Exception:
            pass
    time.sleep(.8)
    _enter_value(driver, DATE_ARRIVAL_ID, date)
    time.sleep(.1)
    _select_dropdown_visible_text(driver, NUMBER_OF_NIGHTS_ID, "1")
    time.sleep(1.2)
    _click_element(driver, SEND_BUTTON_XPATH)
    time.sleep(2)
    # Page 2
    return _get_available_sites_in_california_table(
        driver, name, date, available_sites)


@retry(Exception)
def _enter_value(driver, field_id, value, scroll_into_view=False, select_on_dropdown=False):
    field = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, field_id)))
    if scroll_into_view:
        driver.execute_script("arguments[0].scrollIntoView();", field)
        ActionChains(driver).move_to_element(field).perform()
        field.click()
    field.click()
    field.send_keys(value)
    time.sleep(.5)
    if select_on_dropdown:
        field.send_keys(keys.Keys.DOWN)
        time.sleep(.2)
        field.send_keys(keys.Keys.RETURN)


@retry(Exception)
def _select_dropdown_visible_text(driver, field_id, value):
    menu = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, field_id)))
    dropdown = ui.Select(menu)
    dropdown.select_by_visible_text(value)


@retry(Exception)
def _click_element(driver, xpath):
    elem = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].scrollIntoView();", elem)
    time.sleep(.1)
    elem.click()


def _check_out_california_campsite_page(driver, name, date, available_sites):
    time.sleep(.2)
    rows = driver.find_elements_by_css_selector("table>tbody>tr")
    for row in rows:
        children = row.find_elements_by_xpath(".//*")
        if children[2].get_attribute("class") == "blue_brd_box":
            driver.execute_script("arguments[0].scrollIntoView();", children[2])
            site_name = children[1].text
            if not any(adj in site_name for adj in ["ADA", "Group", "Day"]):
                msg = "{}: {} is available".format(name, site_name)
                if msg not in available_sites[date]:
                    available_sites[date].append(msg)
    time.sleep(.2)
    _click_element(driver, '//*[@id="aHomeBlueiconh"]')

    return available_sites


def _check_gov_sites(driver, name, dates_list, available_sites):
    """Automation for checking teh recreation.gov website."""
    for _ in range(10):
        try:
            _click_element(driver, LOAD_MORE_XPATH)
        except exceptions.NoSuchElementException:
            break
    for date in dates_list:
        _enter_value(driver, DATE_PICKER_ID, 12 * keys.Keys.BACKSPACE + date)
        _click_element(driver, ANOTHER_XPATH)
        _get_available_sites_in_gov_table(driver, name, date, available_sites)

        time.sleep(.2)
    return available_sites


def _get_available_sites_in_california_table(driver, name, date, available_sites):
    original_length = len(available_sites[date])
    children = driver.find_elements_by_class_name("btn_green")
    bad_children = driver.find_elements_by_class_name("btn_green_brd")
    good_children = [child for child in children if child not in bad_children]
    if good_children:
        for i in range(len(good_children)):
            children = driver.find_elements_by_class_name("btn_green")
            bad_children = driver.find_elements_by_class_name("btn_green_brd")
            good_children = [child for child in children if child not in bad_children]
            try:
                time.sleep(.3)
                ActionChains(driver).move_to_element(good_children[i]).perform()
                good_children[i].click()
                _check_out_california_campsite_page(driver, name, date, available_sites)
            except Exception as err:
                pass
            time.sleep(1)
    final_length = len(available_sites[date])
    num_new_sites = final_length - original_length
    if num_new_sites:
        print("\tFound {} sites for {} ({})".format(num_new_sites, date, name))
    return available_sites


@retry(Exception, dont_raise_error=True)
def _get_available_sites_in_gov_table(driver, name, date, available_sites):
    sites = 0
    rows = driver.find_elements_by_xpath(ROW_PATH)
    driver.execute_script("arguments[0].scrollIntoView();", rows[-1])
    for row in rows:
        children = row.find_elements_by_xpath(".//*")
        if "A" in children[3].text:

            if not any(blocked_value in children[1].text
                       for blocked_value in ["HRS", "ADA", "GROUP"]):
                site_num = row.get_attribute("id")
                msg = "{}: {}{}".format(name, CAMPSITE_URL, site_num)
                sites += 1
                available_sites[date].append(msg)
    if sites:
        print("\tFound {} sites for {} ({})".format(sites, date, name))


def _print_to_file(available_sites_dict, output_file=OUTPUT_FILE):
    print("Site IDs and dates saved to {}".format(output_file))
    with open(output_file, "w") as open_file:
        for date in sorted(available_sites_dict.keys()):
            value = available_sites_dict[date]
            msg = "{} has {} available".format(date, len(value))
            print(msg)
            if value and len(value) < 5:
                print("\n\t".join(value))
            open_file.write(msg)
            for msg in available_sites_dict[date]:
                open_file.write("\t{}\n".format(msg))


if __name__ == '__main__':
    fire.Fire({
        "check_dates_in_range": check_date_range,
        "check_saturdays_in_range": check_saturdays_in_range,
        "check_one_date": check_one_date,
        "show_supported_tags": get_valid_tags,
        "show_supported_parks": sorted(ALL_SITES_DICT.keys())
    })
