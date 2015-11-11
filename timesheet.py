#!/usr/bin/env python

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
    #print job_options

    #for index, entry in enumerate(poorly_scoped_table_classes):
    option_index = 0
    for entry in poorly_scoped_table_classes:
        try:
            #print prettify_job(entry.text) + ' | ' + job_options[option_index]
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

    #jobs_form['Jobs'] = job_options[0]
    job_code = job_options[job_choice]
    print 'Chose {}'.format(job_code)
    #jobs_form['Jobs'] = job_code
    job_fields[0]._value = None
    job_fields[job_choice] = 0
    br.submit_form(jobs_form)

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
