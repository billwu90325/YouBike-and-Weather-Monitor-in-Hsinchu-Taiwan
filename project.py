from urllib.request import urlopen
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import datetime
import json
import ssl
import googlemaps
import sys
from PIL import Image
from io import BytesIO 

context = ssl._create_unverified_context()
google_key = 'AIzaSyCbQ1CF7ReVjmlY-w3XTyEip_fmPcps94I'

determine = 1

while(determine == 1):
    # GoogleMaps Geocoding API
    while(True):
        try:
            address = input('Enter a place:')
            location_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + google_key
            location_response = requests.get(location_url).json()
            # acquire information of specific location
            lat = str(location_response['results'][0]['geometry']['location']['lat'])
            lng = str(location_response['results'][0]['geometry']['location']['lng'])
            break
        except:
            print('Invalid location.')


    # Time
    now = str(datetime.datetime.now())
    print('- current time:' + now)
    
    times = []
    for item in now.split():
        times.append(item)
        
    start = int(int(times[1][:2])/3+1)*3
    if start == 24:
        start = '00'
        tmp = str(int(times[0][-2:])+1)
        times[0] = times[0][:8] + tmp
    starttime = times[0] + 'T' + str(start).zfill(2) + ':00:00+08:00'
    # modify time into the pattern of 'Center Weather Bureau'


    # YouBike Station Map
    options = Options()
    options.add_argument("--disable-notifications")
     
    chrome = webdriver.Chrome('./chromedriver', options=options)
    chrome.get("https://hccg.youbike.com.tw/station/list?_id=5cb7e42b083e7b4572793fa2")
    # open 'Hsinchu' YouBike website with selenium & Chrome 

    soup = BeautifulSoup(chrome.page_source, 'html.parser')
    results = soup.find_all('tr', class_='page')
    stations = re.findall('<a href="javascript:center.eventShowmap\(.+?\);">(.+?)</a>', str(soup))
    lng_list = re.findall('<a href="javascript:center.eventShowmap\(\'(.+?)\',', str(soup))
    lat_list = re.findall('<a href="javascript:center.eventShowmap\(.+?,\'(.+?)\',', str(soup))
    area_list = re.findall('data-area="(.+?)">', str(soup))
    numbers = re.findall('<td style="">(.+?)</td><td style="">(.+?)</td>', str(soup))
    # collecting information with BeautifulSoup & Regular Expression

    chrome = webdriver.Chrome('./chromedriver', options=options)
    chrome.get("https://sipa.youbike.com.tw/station/list?_id=5cb7e42b083e7b4572793fa2")
    # open 'Hsinchu Science Park' YouBike website with selenium & Chrome 

    soup2 = BeautifulSoup(chrome.page_source, 'html.parser')
    results2 = soup.find_all('tr', class_='page')
    stations2 = re.findall('<a href="javascript:center.eventShowmap\(.+?\);">(.+?)</a>', str(soup2))
    lng_list2 = re.findall('<a href="javascript:center.eventShowmap\(\'(.+?)\',', str(soup2))
    lat_list2 = re.findall('<a href="javascript:center.eventShowmap\(.+?,\'(.+?)\',', str(soup2))
    area_list2 = re.findall('data-area="(.+?)">', str(soup2))
    numbers2 = re.findall('<td style="">(.+?)</td><td style="">(.+?)</td>', str(soup2))
    # collecting information with BeautifulSoup & Regular Expression
    
    for index in range(len(area_list2)):
        area_list2[index] = 'East District, Hsinchu City'
        
    results.extend(results2)
    stations.extend(stations2)
    lng_list.extend(lng_list2)
    lat_list.extend(lat_list2)
    area_list.extend(area_list2)
    numbers.extend(numbers2)
    
    min_dist = int('inf')
    result = ''
    lat2 = ''
    lng2 = ''
    areaname = ''
    rest = 0
    available = 0
    counter = 0

    for index in range(len(stations)):
        lat_station = lat_list[index]
        lng_station = lng_list[index]

        dist_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='+lat+','+lng+'&destinations='+lat_station+','+lng_station+'&mode=walking&key='+google_key
        dist_response = urlopen(dist_url, context=context).read().decode()
        dist_data = json.loads(dist_response)
        # acquire distance with 'googlemaps distance matrix' API 
        
        try:
            dist = dist_data['rows'][0]['elements'][0]['distance']['value']
            if dist < min_dist:
                if int(numbers[index][0]) > 0:
                    available = numbers[index][0]
                    rest = numbers[index][1]
                    min_dist = dist
                    result = stations[index]
                    lat2 = lat_station
                    lng2 = lng_station
                    areaname = area_list[index]
                else:
                    pass
        except:
            counter += 1
            
        
    if counter == len(stations):
        print('Can\'t find a suitable station.')
        
    else:
        print('- best spot:' + result)
        print('  available bike :' + str(available), 'available space:' + str(rest))

        min_dist_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='+str(lat)+','+str(lng)+'&destinations='+lat2+','+lng2+'&mode=walking&key='+google_key
        min_dist_response = urlopen(min_dist_url, context=context).read().decode()
        min_dist_data = json.loads(min_dist_response)
        # acquire distance & walking distance with 'googlemaps distance matrix' API

        print('  distance:' + min_dist_data['rows'][0]['elements'][0]['distance']['text'])
        print('  time of walking:' + min_dist_data['rows'][0]['elements'][0]['duration']['text'])
        
        station_url =  'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=YouBike'+ result +'&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key='+google_key
        station_response = requests.get(station_url).json()
        reference = station_response['candidates'][0]['photos'][0]['photo_reference']
        # acquire photo-reference with 'googlemaps places' API
        
        photo_url = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=' + reference + '&key=' + google_key
        photo = requests.get(photo_url)
        image = Image.open(BytesIO(photo.content)) 
        image.show()
        # show pictures of stations with 'googlemaps places' API & PIL
        
        print()


    # Weather
    weather_dataid = 'F-D0047-053'
    weather_apikey = 'CWB-D58BA36B-59B7-429B-AC5A-A624166D16C6'
    weather_format = 'JSON'

    weather_url = 'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/'+weather_dataid+'?Authorization='+weather_apikey+'&format='+weather_format
    weather_response = urlopen(weather_url, context=context).read().decode()
    weather_data = json.loads(weather_response)
    # acquire weather forecast of 'Hsinchu' area with opendata API

    area = weather_data['cwbopendata']['dataset']['locations']['locationsName']
    for region in weather_data['cwbopendata']['dataset']['locations']['location']:
        WE = []
        datermine_area = area + region['locationName']
        if datermine_area == areaname:
            print('- weather region:' + areaname)
            for factor in region['weatherElement']:
                if factor['description'] == 'weather summary':
                    for select in factor['time']:
                        if select['startTime'] == starttime:
                            WEI = str(select['elementValue'])
                            for item in WEI.split('。'):
                                WE.append(item)
                            WE.remove(WE[0])
                            WE.remove(WE[2])
                            WE.remove(WE[4])
                            WE.remove(WE[3])
                            for item in WE:
                                print('  '+item)
                            # ouput the weather elements
                                
            print()
            percentage = re.findall('probability of precipitation(.+?)%', WE[0])
            temperature = re.findall('(.+?) celsius', WE[1])
            windspeed = re.findall('(.+?) meter per second', WE[2])

            description = ''
            counter = 0
            
            if int(percentage[0]) > 80:
                description = 'high probability of precipitation'
                counter = 1
            if int(temperature[0]) < 15:
                description += 'low temperature'
                counter = 1 
            if int(windspeed[0]) > 10:
                description += 'strong wind'
                counter = 1
                
            if counter == 1:
                print('- advice:'+ description + 'not recommend')
            else:
                print('- advice: good weather, recommend')
            # output recommendations of system
        else:
            pass


    # Interaction
    while(True):
        print('-Enter Q to quit, R to refresh')
        command = input('command:')
        if command == 'Q':
            sys.exit()
        if command == 'R':
            determine = 1
            break
        else:
            determine = 0