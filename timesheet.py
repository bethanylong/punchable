#!/usr/bin/env python

from pprint import pprint

import requests
requests.packages.urllib3.disable_warnings()
import re
import sys
import getpass
from robobrowser import RoboBrowser

from datetime import datetime

class TimesheetError(Exception):
    pass

def at_cas_login(br):
    return br.url.startswith("https://websso.wwu.edu/cas/login")

def auth():
    try:
        username = raw_input('Universal username: ')
        password = getpass.getpass('Universal password: ')
        return (username, password)
    except KeyboardInterrupt:
        print
        sys.exit(0)

# job_text == br.select('td.dedefault')[0].text == 'Computer Assistant 5, S99554-00UR - Business Operations, 8050'
def prettify_job(job_text):
    regex_str = 'S[0-9]+-[0-9]+'
    delimiter = ' | '
    job_code = re.search(regex_str, job_text).group()
    job_components = re.compile(regex_str).split(job_text)
    return str(job_code + delimiter).join(job_components)

def prepare_screwed_up_form(br, form, submit=None):
    """Modified (part of) RoboBrowser.submit_form().
       Returns method, url, and the serialized form so the caller can tweak it.

       serialized is like:
       {'data': [(u'Jobs', u'1,S99554,00,T,8050,1'),
                 (u'PayPeriod', u'2015,SM,22,I'),
                 (u'Jobs', ''),
                 (u'PayPeriod', u'2015,SM,22,I'),
                 (u'Jobs', ''),
                 (u'PayPeriod', u'2015,SM,22,I')]}
    """
    method = form.method.upper()
    url = br._build_url(form.action) or br.url
    payload = form.serialize(submit=submit)
    serialized = payload.to_requests(method)
    return (method, url, serialized)

def submit_screwed_up_form(br, method, url, serialized_form, **kwargs):
    """Modified (part of) RoboBrowser.submit_form().
       Accepts method, url, and the tweaked form to send.."""
    send_args = br._build_send_args(**kwargs)
    send_args.update(serialized_form)
    response = br.session.request(method, url, **send_args)
    br._update_state(response)

def get_job_option(displayed_table_entries, job_options):
    option_index = 0
    for entry in displayed_table_entries:
        try:
            print '[{}] {} | {}'.format(option_index, prettify_job(entry.text), job_options[option_index])
            option_index += 1
        except:
            pass
    print '[{}] All of the above'.format(option_index)

    job_choice = -1
    while job_choice not in range(len(job_options) + 1):
        try:
            job_choice = int(raw_input('Select a job from above (index in square brackets): '))
        except KeyboardInterrupt:
            print
            sys.exit(0)
        except:
            pass
    return job_choice

def timesheet_selection_post_data(serialized_form, job_choice, job_code):
    post_data_to_send = []
    job_count = 0
    for entry in serialized_form['data']:
        key = entry[0]
        value = entry[1]

        if key == 'Jobs':
            if job_count != job_choice:
                value = ''
                job_count += 1
                continue #?
            else:
                value = job_code
                job_count += 1
        post_data_to_send.append((key, value))
    return post_data_to_send

def matching_date(days, table_index):
    """Iterate through list of seen days and return the index of a match if any.
       Match based on index and page from timesheet <table>."""
    for list_index, day in enumerate(days):
        if day['index'] == table_index:
            return list_index
    # No match returned
    raise ValueError("Unable to match this cell in the timesheet table with a date we've seen")

def hour_value(table_cell):
    if table_cell == 'Enter Hours':
        return float(0)
    else:
        return float(table_cell)

def parse_date(date_str):
    return datetime.strptime(date_str, "%m/%d/%Y").date()

def week_number(date):
    # %W has Monday as the first day of the week, just like pay weeks.
    return int(date.strftime("%W"))

def weekday_number(date):
    # %w has 0 as Sunday and 6 as Saturday, but we want 0 to be Monday
    # and 6 to be Sunday.
    canonical_weekday = int(date.strftime("%w"))
    our_weekday = canonical_weekday - 1
    if our_weekday == -1:
        our_weekday = 6
    return our_weekday

def weekday_name(date):
    return date.strftime("%a")

def get_days_and_hours(br):
    """Return a list of objects including date and number of hours for each day
       on the current page's timesheet table."""
    days = []

    # In one week of selected job's timesheet
    hours_table = br.find_all('table')[-3]

    # Look at top line of table (headings, including dates)
    # Add the dates we see to our list
    top_line = hours_table.find_all('tr')[0].find_all('td')
    for index, entry in enumerate(top_line):
        try:
            regex_str = '[0-9]{2}/[0-9]{2}/[0-9]{4}'
            date = re.search(regex_str, str(entry)).group()
            days.append({'date': parse_date(date), 'index': index})
        except:
            # Table entry outside of the region where hours are entered
            pass

    # Look at second line of table (hourly regular pay)
    hourly_regular = hours_table.find_all('tr')[1].find_all('td')

    for index, entry in enumerate(hourly_regular):
        # Check days we've seen, see if any matches this cell,
        # and set that list entry's hours if it does.
        try:
            days_index = matching_date(days, index)
            days[days_index]['hours'] = hour_value(entry.text)
        except:
            # Cell in hours table that doesn't store a day's hours
            pass

    return [{'date': day['date'],
             'week': week_number(day['date']),
             'weekday_number': weekday_number(day['date']),
             'weekday_name': weekday_name(day['date']),
             'hours': day['hours']}
            for day in days]

def hours_by_week(days_list):
    by_week = {}
    for day in days_list:
        if day['week'] not in by_week:
            by_week[day['week']] = float(0)
        by_week[day['week']] += day['hours']
    return by_week

def print_hours(days_list):
    hbw = hours_by_week(days_list)
    curr_week = None
    for day in days_list:
        if day['week'] != curr_week:
            curr_week = day['week']
            print
            print 'Pay week {}, starting from {}: {} hours'.format(day['week'], day['date'], hbw[day['week']])
        print '{} {}: {} hours'.format(day['weekday_name'], day['date'], day['hours'])

def go_to_timesheet_home():
    """Create a new browser object, log in via CAS, and return the object once
       it's at the job selection page."""
    br = RoboBrowser(history=True, parser='html.parser')

    # Log in via CAS
    timesheet_url = 'https://admin.wwu.edu/pls/wwis/bwpktais.P_SelectTimeSheetRoll'
    br.open(timesheet_url)
    cas_form = br.get_form(0)
    cas_form['username'] = username
    cas_form['password'] = password
    br.submit_form(cas_form)

    if at_cas_login(br):
        raise TimesheetError("Username/password combination is incorrect, account is locked out, or something funky is happening with redirects.")

    return br

def get_timesheet_choice():
    """Go to timesheet home page, gather list of timesheets/jobs, prompt user
       for input on which one to choose, and return the choice's index and code."""
    print
    print 'Loading timesheet choices...'

    br = go_to_timesheet_home()

    # Look at timesheet selection form
    jobs_form = br.get_forms()[-1]
    job_fields = jobs_form.fields.getlist('Jobs')

    # Get user's timesheet choice
    job_options = [entry.options[0] for entry in job_fields]
    poorly_scoped_table_classes = br.select('td.dedefault')
    job_choice = get_job_option(poorly_scoped_table_classes, job_options) # prompt

    #job_code = job_options[job_choice]
    #return (job_choice, job_code)

    jobs = []
    if job_choice == len(job_options):
        # "All of the above"
        for index, job_code in enumerate(job_options):
            jobs.append((index, job_code))
    else:
        jobs.append((job_choice, job_options[job_choice]))

    return jobs

def print_summary(job_choice, job_code):
    print
    print 'Getting hours for job {}...'.format(job_choice)
    br = go_to_timesheet_home()
    jobs_form = br.get_forms()[-1]

    # Manipulate timesheet form with user's job choice, and submit it
    method, url, serialized = prepare_screwed_up_form(br, jobs_form)
    post_data_to_send = timesheet_selection_post_data(serialized, job_choice, job_code)
    form_details = {'data': post_data_to_send}
    submit_screwed_up_form(br, method, url, form_details)

    days = []
    page = 0
    # Iterate through pages of timesheet and append each day's hours to list
    while True:
        # Get data from this page
        days += get_days_and_hours(br)

        # Find "next" button
        button_form = br.get_forms()[1]
        submit_buttons = button_form.fields.getlist('ButtonSelected')
        next_button = submit_buttons[-1]
        if next_button.value != 'Next':
            # On last page
            break

        # Go to next page
        br.submit_form(form=button_form, submit=next_button)
        page += 1

    hours_sum = 0
    for day in days:
        hours_sum += day['hours']
    
    print
    print 'Total hours on this timesheet: {}'.format(hours_sum)

    print_hours(days)


if __name__ == '__main__':
    username, password = auth()
    for job_choice, job_code in get_timesheet_choice():
        print_summary(job_choice, job_code)
