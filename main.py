import lxml.html
import requests
import csv
from collections import defaultdict
import time
import re
import logging

logging.basicConfig(filename='runtime.log',level=logging.DEBUG)

# Make the city dictionary
cities = defaultdict(list)
with open('cities.txt', 'r') as File:
    reader = csv.reader(File, delimiter = ',', lineterminator = '\n')
    for row in reader:
        # dictionary with format:
        #   key: city name
        #   first value: population
        #   second value: number of times city referenced in song
        cities[row[1]] = [row[3], 0]

print (cities)

# Loop through music found on azlyrics.com
baseurl = 'https://www.azlyrics.com/'

html = requests.get(baseurl+'g.html') # checks all artists starting with G
doc = lxml.html.fromstring(html.content)
time.sleep(5)
artist_list = doc.xpath('//div[contains(@class,"artist-col")]/a')
for link in artist_list:
    try:
        time.sleep(5)
        artist_url = link.get('href')
        artist_html = requests.get(baseurl+artist_url)
        artist_doc = lxml.html.fromstring(artist_html.content)
        song_list = artist_doc.xpath('//div[contains(@class,"listalbum-item")]/a')
        for song in song_list:
            try:
                time.sleep(5)
                song_link_temp = song.get('href')
                song_url = song_link_temp.replace('../', '')
                song_html = requests.get(baseurl+song_url)
                song_doc = lxml.html.fromstring(song_html.content)
                text = song_doc.xpath("//div/text()")
                lyrics = []
                for line in text:
                    lyrics.append(line.strip()) # Cleans up lyrics
                for line in lyrics:
                    for city in cities.keys():
                        if re.search(r'\b'+city+r'\b', line): # optionally use .upper()
                            print ('city found '+city+' at: '+baseurl+song_url)
                            logging.info('city found '+city+' at: '+baseurl+song_url)
                            cities[city][1] = cities[city][1] + 1
            except:
                print ("Song link failed: "+song_url)
                logging.warning("Song link failed: "+song_url)
    except:
        print ("Artist link failed: "+artist_url)
        logging.warning("Artist link failed: "+artist_url)

with open('citysong_G.csv', 'w') as f:
    f.write("%s,%s,%s\n"%('City','Population', 'Reference Count'))
    for key in cities.keys():
        f.write("%s,%s,%s\n"%(key,int(cities[key][0]),cities[key][1]))