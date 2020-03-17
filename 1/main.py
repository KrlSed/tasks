from html.parser import HTMLParser
import requests
import json
import re

list_of_offices = []

response = requests.get('https://www.mebelshara.ru/contacts')
response.encoding = 'utf-8'

def add(name, address, wh1, wh2, lat, lon, 
        city_name, phone_number):
    workin_hours = []
    latlon = [float(lat),float(lon)]
    if wh1[:3] == "Без":
        wh1 = 'пн-вс'
        workin_hours.append(wh1 + ' ' + wh2)
    else:
        workin_hours.append(wh1)
        workin_hours.append(wh2)
    address_format = city_name + ", " + address    
    list_of_offices.append({
        "address": address_format,
        "latlon": latlon,
        "name": name,
        "phones": [phone_number],
        "working_hours": workin_hours
    })
    output(list_of_offices)


def output(list_of_offices):
    f = open('task1.json', "w", encoding='utf-8')
    output = json.dumps(list_of_offices,
                        sort_keys=False, indent=4, ensure_ascii=False,  separators=(',', ': '))
    output2 = re.sub(r'": \[\s+', '": [', output)
    output3 = re.sub(r'\d{1},\s+', ',', output2)
    output4 = re.sub(r'\d{1}\s+]', ']', output3)
    output5 = re.sub(r'"\s+\]', '"]', output4)
    output6 = re.sub(r'(?P<name>:\d{2}",)\s+', r'\g<name> ', output5)
    output7 = re.sub(r'(?P<name2>\d{2}.\d{3}),', r'\g<name2>00,', output6)
    output8 = re.sub(r'(?P<name3>\d{2}.\d{3})]', r'\g<name3>00]', output7)
    output9 = re.sub(r'(?P<name4>\d{2}.\d{4}),', r'\g<name4>0,', output8)
    output_format = re.sub(r'(?P<name5>\d{2}.\d{4})]', r'\g<name5>0]', output9)
    f.write(output_format)



class MyHTMLParser(HTMLParser):
    city_start = False
    phone_start = False
    city_name = ""
    phone_number = ""

    def handle_starttag(self, tag, attrs):  
        try:
            if attrs[0][1] == "phone-num zphone":
                self.phone_start = True
            if attrs[0][1] == "js-city-name":
                self.city_start = True
            if attrs[0][1] == "shop-list-item":
                name = attrs[1][1]
                address = attrs[2][1]
                work_hours_1 = attrs[3][1]
                work_hours_2 = attrs[4][1]
                lat = attrs[5][1]
                lon = attrs[6][1]
                add(name, address, work_hours_1, work_hours_2, lat, lon,
                    self.city_name, self.phone_number)
        except IndexError:
            pass

    def handle_data(self, data):
        if self.city_start:
            self.city_name = data
            self.city_start = False
        if self.phone_start:
            self.phone_number = data
            self.phone_start = False

parser = MyHTMLParser()
parser.feed(response.text)
 
  
