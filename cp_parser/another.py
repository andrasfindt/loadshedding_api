import re
import json
import html2text
import time
from datetime import datetime
import requests

city_power_loadshedding_page = 'https://www.citypower.co.za/customers/Pages/Load_Shedding_Downloads.aspx'
response = requests.get(city_power_loadshedding_page)
# f = open("test.html", "r")
# html = f.read()
html = response.text
text = html2text.html2text(html)
# get part after 'Please note the Load Shedding Schedule below:'
schedule_part = text.split('Please note the Load Shedding Schedule below:')[1]
# get part before 'City Power customers are urged to check' and replace special blanks
schedule_part = schedule_part.split('City Power customers are urged to check')[0] \
    .replace('\u200d', '').replace('\u200c', '').replace('\u200b', '')
# filter out blank lines and things
lines = filter(lambda x: (x.strip() != '' and not x.startswith('---|---')), schedule_part.split('\n'))
schedule = []

schedule_sections = '\n'.join(lines).split('Stage ')

for section in filter(lambda x: x.strip() != '', schedule_sections):
    stage_holder = {}
    section_lines = section.split('\n')
    # find stage and date
    stage_and_date_line = section_lines[0]
    stage_and_date_line_regex = r'(\d) Load Shedding - (\d+)\w+ (\w+) (\d+) .*'
    match = re.search(stage_and_date_line_regex, stage_and_date_line)
    if match:
        stage = match.group(1)
        stage_holder['stage'] = stage
        date = f'{match.group(2)} {match.group(3)} {match.group(4)}'
        stage_holder['date'] = datetime.strptime(date, '%d %b %Y').date().isoformat()
    remaining_lines = ''.join(section_lines[1:len(section_lines)])
    s = remaining_lines.split('  ')
    timeslots = []
    for i in range(1, int((len(section_lines) - 1) / 2)):
        timeslot = {}
        time_and_blocks_line = f'{s[i * 2]} {s[i * 2 + 1]}'
        time_and_blocks_line_regex = r'(\d+:\d+) - (\d+:\d+).*Blocks? (.*)'
        match2 = re.search(time_and_blocks_line_regex, time_and_blocks_line)
        if match2:
            start_time = match2.group(1)
            start_datetime = datetime.strptime(f'{date} {start_time}', '%d %b %Y %H:%M')
            timeslot['start_time'] = round(time.mktime(start_datetime.timetuple()))

            end_time = match2.group(2)
            end_datetime = datetime.strptime(f'{date} {end_time}', '%d %b %Y %H:%M')
            timeslot['end_time'] = round(time.mktime(end_datetime.timetuple()))

            blocks = list(map(lambda x: (int(x)), match2.group(3).split(', ')))
            timeslot['blocks'] = blocks
        timeslots.append(timeslot)
    stage_holder['timeslots'] = timeslots
    schedule.append(stage_holder)

print(json.dumps(schedule, indent=2))
