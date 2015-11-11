#!/usr/bin/env python

from pprint import pprint

import requests
requests.packages.urllib3.disable_warnings()
import re
import sys
import getpass
from robobrowser import RoboBrowser

def at_cas_login(br):
    return br.url.startswith("https://websso.wwu.edu/cas/login")

def auth():
    username = raw_input('Universal username: ')
    password = getpass.getpass('Universal password: ')
    return (username, password)

# job_text == br.select('td.dedefault')[0].text == 'Computer Assistant 5, S99554-00UR - Business Operations, 8050'
def prettify_job(job_text):
    regex_str = 'S[0-9]+-[0-9]+'
    delimiter = ' | '
    job_code = re.search(regex_str, job_text).group()
    job_components = re.compile(regex_str).split(job_text)
    return str(job_code + delimiter).join(job_components)

def prepare_screwed_up_form(br, form, submit=None):
    """Modified (part of) RoboBrowser.submit_form().
       Returns method, url, and the serialized form so the caller can tweak it."""
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

if __name__ == '__main__':
    username, password = auth()
    cas_url = 'https://admin.wwu.edu/pls/wwis/bwpktais.P_SelectTimeSheetRoll'
    br = RoboBrowser(history=True, parser='html.parser')

    # Log in via CAS
    print
    print 'Loading timesheet choices...'
    br.open(cas_url)
    cas_form = br.get_form(0)
    cas_form['username'] = username
    cas_form['password'] = password
    br.submit_form(cas_form)

    if at_cas_login(br):
        print "Username/password combination is incorrect, account is locked out, or something funky is happening with redirects."
        sys.exit(1)

    # Contend with nasty-ass timesheet html
    jobs_form = br.get_forms()[-1]
    poorly_scoped_table_classes = br.select('td.dedefault')

    job_fields = jobs_form.fields.getlist('Jobs')
    job_options = [entry.options[0] for entry in job_fields]

    option_index = 0
    for entry in poorly_scoped_table_classes:
        try:
            print '[{}] {} | {}'.format(option_index, prettify_job(entry.text), job_options[option_index])
            option_index += 1
        except:
            pass

    job_choice = -1
    while job_choice not in range(len(job_options)):
        try:
            job_choice = int(raw_input('Select a job from above (index in square brackets): '))
        except:
            pass

    job_code = job_options[job_choice]

    method, url, serialized = prepare_screwed_up_form(br, jobs_form)
    """serialized is like:
       {'data': [(u'Jobs', u'1,S99554,00,T,8050,1'),
                 (u'PayPeriod', u'2015,SM,22,I'),
                 (u'Jobs', ''),
                 (u'PayPeriod', u'2015,SM,22,I'),
                 (u'Jobs', ''),
                 (u'PayPeriod', u'2015,SM,22,I')]}
    """
    
    bs = []
    job_count = 0
    for entry in serialized['data']:
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
        bs.append((key, value))

    form_details = {'data': bs}
    submit_screwed_up_form(br, method, url, form_details)

    regex_str = '[0-9]{2}/[0-9]{2}/[0-9]{4}'

    days = []
    page = 0
    while True:
        try:
            # In one week of selected job's timesheet
            hours_table = br.find_all('table')[-3]

            top_line = hours_table.find_all('tr')[0].find_all('td')
            for index, entry in enumerate(top_line):
                try:
                    date = re.search(regex_str, str(entry)).group()
                    days.append({'date': date, 'index': index, 'page': page})
                except:
                    # Table entry outside of the region where hours are entered
                    pass

            hourly_regular = hours_table.find_all('tr')[1].find_all('td')
            for index, entry in enumerate(hourly_regular):
                date = None

                # Eww
                for day in days:
                    if day['index'] == index and day['page'] == page:
                        date = day['date']

                        contents = entry.text
                        if contents == 'Enter Hours':
                            contents = float(0)
                        else:
                            contents = float(contents)

                        day['hours'] = contents
                        break
    
            button_form = br.get_forms()[1]
            submit_buttons = button_form.fields.getlist('ButtonSelected')
            next_button = submit_buttons[-1]
            if next_button.value != 'Next':
                break

            # Go to next page
            br.submit_form(form=button_form, submit=next_button)
            page += 1
        except:
            break

    # Finally
    from pprint import pprint
    print
    print 'Hourly Regular Time:'
    pprint(days)

    hours_sum = 0
    for day in days:
        hours_sum += day['hours']
    
    print 'Total hours: {}'.format(hours_sum)
