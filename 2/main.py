from html.parser import HTMLParser
import requests
import json
import re

list_to_json= []
template = {}  

def generate_phone_formate(phone_list):
    new_phone_list = []
    phone_first = re.sub(r'[^0-9]+', r'', phone_list[0])
    try:
        if phone_list[1][0] == '+':
            phone_list[1] = phone_list[1][2:10]
        phone_second = re.sub(r'[^0-9]+', r'', phone_list[1]) 
        code_numbers = " (" + phone_second[1:4] + ") "
        three_numbers = phone_second[4:7]
        two_two_numbers = phone_second[7:9] + '-' + phone_second[9:11]
        phone_second = "8" + code_numbers + three_numbers + '-' + two_two_numbers
        new_phone_list.append(phone_second)
    except IndexError:
        pass
    if phone_first[0] == '+':
        phone_first = phone_first[2:10]
    code_numbers = " (" + phone_first[1:4] + ") "
    three_numbers = phone_first[4:7]
    two_two_numbers = phone_first[7:9] + '-' + phone_first[9:11]
    phone_first = "8" + code_numbers + three_numbers + '-' + two_two_numbers
    new_phone_list.append(phone_first)
    return(new_phone_list)

def date_formate(hoursOfOperation):
    work_date = []
    workdays = ""
    saturday = ""
    sunday = ""
    hours_workdays = hoursOfOperation["workdays"]
    hours_saturday = hoursOfOperation["saturday"]
    hours_sunday = hoursOfOperation["sunday"] 
    sat_start = str(hours_saturday["start"])
    sun_start = str(hours_sunday["start"])
    sat_end = str(hours_saturday["end"])
    sun_end = str(hours_sunday["end"])

    if (hours_saturday["isDayOff"] == False & hours_sunday["isDayOff"] == False) & (sun_start == sat_start) | (sat_end == sun_end):
        workdays = "пн - пт " + hours_workdays["startStr"] + " - " + hours_workdays["endStr"]
        saturday = "cб - вс " + sat_start[:-3] + " - " + sat_end[:-3] 
        sunday = ""
    if (hours_saturday["isDayOff"] == False & hours_sunday["isDayOff"] == False) & (sun_start != sat_start):
        workdays = "пн - пт " + hours_workdays["startStr"] + " - " + hours_workdays["endStr"]
        saturday = "cб " + sat_start[:-3] + " - " + sat_end[:-3] 
        sunday = "вс " + sun_start[:-3] + " - " + sun_end[:-3]
    if (hours_saturday["isDayOff"] == False) & (hours_sunday["isDayOff"]):
        workdays = "пн - пт " + hours_workdays["startStr"] + " - " + hours_workdays["endStr"]
        saturday = "cб " + sat_start[:-3] + " - " + sat_end[:-3]
        sunday = "вс выходной"
    if (hours_saturday["isDayOff"]) & (hours_sunday["isDayOff"]):
        workdays = "пн - пт " + hours_workdays["startStr"] + " - " + hours_workdays["endStr"]
        saturday = "cб - вс выходной"
        sunday = ""

    work_date.append(workdays)
    work_date.append(saturday)
    if sunday != "":
        work_date.append(sunday)

    return(work_date)

    

def add(a, l, n, p, w):  
    template = {
        "address": a,
        "latlon": l,
        "name": n,
        "phones": generate_phone_formate(p),
        "working_hours": date_formate(w)
    }
    list_to_json.append(template)

def create_list_phones(phones_object):
    phone_numbers = []
    phone_object = phones_object[0]
    phone_numbers.append(phone_object["phone"])
    try:
        phone_object = phones_object[1]
        phone_numbers.append(phone_object["phone"])
    except IndexError:
        pass
    return(phone_numbers)

response_cities = requests.get('https://www.tui.ru/api/office/cities/')
response_cities.encoding = 'utf-8'
list_of_cities = json.loads(response_cities.text)
i = 0
for city in list_of_cities:
    response_offices = requests.get('https://www.tui.ru/api/office/list/' +
                                    '?cityId=' + str(city["cityId"]))
    response_offices.encoding = 'utf-8'
    list_of_offices = json.loads(response_offices.text)
    for office in list_of_offices:
        add(office["address"], [office["latitude"], office["longitude"]],
            office["name"], create_list_phones(office["phones"]), 
            office["hoursOfOperation"])
    




def output(list_to_json):
    f = open('task2.json', "w",
             encoding='utf-8')
    output = json.dumps(list_to_json,
                        indent=4, sort_keys=False,
                        ensure_ascii=False,  separators=(',', ': '))
    # в одну строку
    output2 = re.sub(r'": \[\s+', '": [', output)
    output3 = re.sub(r'\d{1},\s+', ',', output2)
    output4 = re.sub(r'\d{1}\s+]', ']', output3)
    output5 = re.sub(r'(?P<name0>-\d{2}",)\s+', r'\g<name0> ', output4)
    output6 = re.sub(r'(?P<name1>:\d{1}0",)\s+',r'\g<name1> ', output5)
    output7 = re.sub(r'"\s+\]', '"]', output6)
    # сокращение координат
    output8 = re.sub(r'(?P<name2>\d{2}.\d{6})\d*,', r'\g<name2>,', output7)
    output9 = re.sub(r'(?P<name3>\d{2}.\d{6})\d*]', r'\g<name3>]', output8)
    # округление до 0.000001
    output10 = re.sub(r'(?P<name4>\d{2}.\d{3}),', r'\g<name4>000,', output9)
    output11 = re.sub(r'(?P<name5>\d{2}.\d{3})]', r'\g<name5>000]', output10)
    output12 = re.sub(r'(?P<name6>\d{2}.\d{4}),', r'\g<name6>00,', output11)
    output13 = re.sub(r'(?P<name7>\d{2}.\d{4})]', r'\g<name7>00]', output12)
    output14 = re.sub(r'(?P<name8>\d{2}.\d{5}),', r'\g<name8>0,', output13)
    output_format = re.sub(r'(?P<name9>\d{2}.\d{5})]', r'\g<name9>0]', output14)
    f.write(output_format)

output(list_to_json)





