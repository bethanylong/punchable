# punchable
Slightly less-shitty timesheet interface.

*Warning*: This tool does the equivalent of navigating to web pages and pushing buttons. It is not perfect, and the pages it expects to see are subject to change. If you're at all worried about something going wrong and having your timesheet messed up, keep a record of your hours (like a screenshot) before using this.

```
$ python timesheet.py
Universal username: longb4
Universal password: 

Loading timesheet choices...
[0] Computer Assistant 5, S99554-00 | UR - Business Operations, 8050 | 1,S99554,00,T,8050,1
[1] Computer Assistant 5, S50000-00 | Enterprise Infrastructure Svcs-Tel, 5370 | 2,S50000,00,T,5370,1
[2] Program Support Staff 2, S99429-00 | Computer Science Department, 3360 | 3,S99429,00,T,3360,1
[3] All of the above
Select a job from above (index in square brackets): 3

Getting hours for job 0...

Total hours on this timesheet: 4.5

Pay week 46, starting from 2015-11-16: 4.0 hours
Mon 2015-11-16: 0.0 hours
Tue 2015-11-17: 0.0 hours
Wed 2015-11-18: 0.0 hours
Thu 2015-11-19: 0.0 hours
Fri 2015-11-20: 0.5 hours
Sat 2015-11-21: 3.5 hours
Sun 2015-11-22: 0.0 hours

Pay week 47, starting from 2015-11-23: 0.0 hours
Mon 2015-11-23: 0.0 hours
Tue 2015-11-24: 0.0 hours
Wed 2015-11-25: 0.0 hours
Thu 2015-11-26: 0.0 hours
Fri 2015-11-27: 0.0 hours
Sat 2015-11-28: 0.0 hours
Sun 2015-11-29: 0.0 hours

Pay week 48, starting from 2015-11-30: 0.5 hours
Mon 2015-11-30: 0.5 hours

Getting hours for job 1...

Total hours on this timesheet: 3.5

Pay week 46, starting from 2015-11-16: 1.5 hours
Mon 2015-11-16: 0.0 hours
Tue 2015-11-17: 0.0 hours
Wed 2015-11-18: 0.0 hours
Thu 2015-11-19: 0.0 hours
Fri 2015-11-20: 1.5 hours
Sat 2015-11-21: 0.0 hours
Sun 2015-11-22: 0.0 hours

Pay week 47, starting from 2015-11-23: 2.0 hours
Mon 2015-11-23: 0.0 hours
Tue 2015-11-24: 0.0 hours
Wed 2015-11-25: 0.0 hours
Thu 2015-11-26: 0.0 hours
Fri 2015-11-27: 0.0 hours
Sat 2015-11-28: 0.0 hours
Sun 2015-11-29: 2.0 hours

Pay week 48, starting from 2015-11-30: 0.0 hours
Mon 2015-11-30: 0.0 hours

Getting hours for job 2...

Total hours on this timesheet: 30.5

Pay week 46, starting from 2015-11-16: 13.5 hours
Mon 2015-11-16: 0.0 hours
Tue 2015-11-17: 5.5 hours
Wed 2015-11-18: 0.0 hours
Thu 2015-11-19: 0.0 hours
Fri 2015-11-20: 0.5 hours
Sat 2015-11-21: 0.0 hours
Sun 2015-11-22: 7.5 hours

Pay week 47, starting from 2015-11-23: 17.0 hours
Mon 2015-11-23: 0.0 hours
Tue 2015-11-24: 0.5 hours
Wed 2015-11-25: 2.0 hours
Thu 2015-11-26: 0.0 hours
Fri 2015-11-27: 6.5 hours
Sat 2015-11-28: 5.0 hours
Sun 2015-11-29: 3.0 hours

Pay week 48, starting from 2015-11-30: 0.0 hours
Mon 2015-11-30: 0.0 hours

Hours by pay week over all jobs:
{46: 19.0, 47: 19.0, 48: 0.5}
```
