
import requests
from bs4 import BeautifulSoup
import pandas
from pandas import ExcelWriter
import io
import re
import openpyxl


base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer AgYt97MWMyHbYAJxKNjhM83L_GTw-okHOBqMwUHJhzF1o-vQibgynXAzwK4nSc58'}
artist_name_df = pandas.read_excel('songs.xlsx', usecols=[0,0]).transpose()
song_title_df = pandas.read_excel('songs.xlsx', usecols=[1,1]).transpose()
artist_name = list(pandas.read_excel('songs.xlsx', usecols=[0,0]).values.flatten())
song_title = list(pandas.read_excel('songs.xlsx', usecols=[1,1]).values.flatten())
totallyrics = ""
count = 0
writer = pandas.ExcelWriter('wordcount.xlsx')
song_dates = []
song_lyrics = []

def lyrics_from_song_api_path(song_api_path):
  song_url = base_url + song_api_path
  response = requests.get(song_url, headers=headers)
  json = response.json()
  path = json["response"]["song"]["path"]
  #gotta go regular html scraping... come on Genius
  page_url = "http://genius.com" + path
  page = requests.get(page_url)
  html = BeautifulSoup(page.text, "html.parser")
  #remove script tags that they put in the middle of the lyrics
  [h.extract() for h in html('script')]
  #at least Genius is nice and has a tag called 'lyrics'!
  lyrics = html.find('div', { 'class' : 'lyrics' }).get_text()
  release_date = html.find_all('span', { 'class' : 'metadata_unit-info--text_only' })
  if (len(release_date) == 0):
    song_dates.append("NaN")
  for i in range(len(release_date)):
    release_date[i] = release_date[i].get_text()
    try:
        float(release_date[i][-4:])
        song_dates.append(release_date[i])
    except :
        pass
  
  return lyrics

def word_count(str):
  counts = dict()
  words = str.split()

  for word in words:
      if word in counts:
          counts[word] += 1
      else:
          counts[word] = 1

  return counts

for i in range(len(artist_name)):
  if __name__ == "__main__":
    search_url = base_url + "/search"
    data = {'q': song_title[i]}
    response = requests.get(search_url, params=data, headers=headers)
    json = response.json()
    song_info = None
    for hit in json["response"]["hits"]:
      if hit["result"]["primary_artist"]["name"] == artist_name[i]:
        song_info = hit
        break
    if song_info:
      song_api_path = song_info["result"]["api_path"]
      count = count + 1
      song_lyrics = lyrics_from_song_api_path(song_api_path)
      song_lyrics = song_lyrics.lower()
      song_result = re.sub("[\(\[].*?[\)\]]", "", song_lyrics)
      song_result = song_result.replace(',', '')
      song_wordcount_array = word_count(song_result)
      dftemp = pandas.DataFrame.from_dict(song_wordcount_array, orient='index')

      dftemp.to_excel(writer,'Sheet1', startrow=7, startcol=2*i+1, header=False)
      writer.save()

      totallyrics = totallyrics + song_lyrics
    else:
      song_dates.append("NaN")


for i in range(len(artist_name))




result = re.sub("[\(\[].*?[\)\]]", "", totallyrics)
result = result.lower()
result = result.replace(',', '')
# text_file = io.open("Output.txt", "w", encoding='utf8')
# text_file.write(result)
wordcount_array = word_count(result)
df = pandas.DataFrame.from_dict(wordcount_array, orient='index')

df.to_excel(writer,'Sheet1', startrow=7, startcol=101, header=False)
# artist_name_df.to_excel(writer, 'Sheet1', startrow=1, startcol=0)
# song_title_df.to_excel(writer, 'Sheet1', startrow=3, startcol=0)
df_dates = pandas.DataFrame(song_dates).transpose()
# df_dates.to_excel(writer, 'Sheet1', startrow=5, startcol=0)
big_df = artist_name_df.append(song_title_df, ignore_index=True)
big_df = big_df.append(df_dates, ignore_index=True)
big_df.to_excel(writer, 'Sheet1', startrow=1, startcol=0)
writer.save()



