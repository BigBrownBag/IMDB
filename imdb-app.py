import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd

class PythonIMDB:

    def __init__(self, url):
        self.url = 'https://www.imdb.com'+url
        self.html = self.get_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def get_html(self):
        try:
            result = requests.get(self.url)
            result.raise_for_status()
            return result.text
        except(requests.RequestException, ValueError):
            print('Server error')
            return False

    def get_title(self):
        film_title = self.soup.select('div.title_wrapper h1')
        title = [tag.text for tag in film_title]
        return title[0].replace(u'\xa0', u' ')
    
    def get_genre(self):
        try:
            film_genre = self.soup.select('div.subtext a')
            genre_list = [tag.text for tag in film_genre]
            st = ''
            for i in range(0,len(genre_list)-1):
                st += genre_list[i] + ' '
            return st
        except IndexError:
            return '-'

    def get_rating(self):
        try:
            film_rating = self.soup.select('div.ratingValue strong span')
            rating = [tag.text for tag in film_rating]
            return rating[0].replace(u'\xa0', u' ')
        except IndexError:
            return 'not rated'

    def get_topcast(self):
        try:
            film_cast = self.soup.select('div.credit_summary_item a')
            cast = [tag.text for tag in film_cast]
            return f"{cast[0]}, {cast[1]}, {cast[2]}".replace(u', 1 more credit',u'')
        except IndexError:
            return '-'
            
    def get_details(self):
        film_details = self.soup.select('div#titleDetails div.txt-block')
        details = [tag.text for tag in film_details]
        #details[0].replace(u'\nSee more\xa0»\n', u'').replace(u'Show more on\n  IMDbPro\xa0»\n', u'').replace(u'See full technical specs\xa0»\n', u'').replace(u'\n\nEdit\n\n', u'').replace(u'Details',u'').replace('\n',' ')
        d = ''
        for i in details:
            d+= i.replace('\n','\xa0').replace('IMDbPro\xa0»','').replace(u'See more\xa0»', u'').replace(u'Show more on', u'').replace(u'See full technical specs\xa0»', u'').replace(u'Edit', u'').replace(u'Details',u'').replace('|',',')
        return d

    def write_doc(self):
        name = self.get_title()
        genres = self. get_genre()
        rating = self.get_rating()
        topcast = self.get_topcast()
        details = self.get_details()
        df = pd.DataFrame({'Title': [name],'genres': [genres], 'rating':[rating], 'topcast':[topcast], 'details':details})
        name_file = 'films.csv'
        df.to_csv(name_file, index=False, mode='a', header=False)
        logging.info('films writen on doc')
        return name_file


logging.basicConfig(level=logging.DEBUG, filename='imdb-app.log', format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
items = []
link_next = '/search/title/'
filters = {
    'genres' : ['documentary','biography'], #action adventure animation biography comedy crime documentary drama family fantasy film_noir game_show history horror music musical mystery news reality_tv romance sci_fi sport talk_show thriller war western
    'title_type' : 'tv_movie', #feature, tv_movie, tv_series, tv_episode, tv_special, tv_miniseries, tv_miniseries, documentary, video_game, short, video, tv_short
    'user_rating-min' : '', #from 1.0 to 10.0
    'countries' : '',
    'release_date-min' : '', #Format: YYYY-MM-DD, YYYY-MM, or YYYY
    'release_date-max' : '',
}    
print('Started..')         
while len(items)<1000:
    URL = 'https://www.imdb.com'+link_next
    result = requests.post(URL, params=filters)
    soup = BeautifulSoup(result.text, 'html.parser')
    temporary = soup.select('h3.lister-item-header a')
    for links in temporary:
            items += [links.get('href')]
    try:
        link_next = soup.select('a.next-page')[0].get('href')
    except IndexError:
        break          #out of pages
logger.info(f"found {len(items)} films") 
logger.info("parsing in progress...")
df = pd.DataFrame({'Title': [''],'genres': [''], 'rating':[''], 'topcast':[''], 'details':['']})
name_file = 'films.csv'
df.to_csv(name_file, index=False)
for item in items:
    try:
        films = PythonIMDB(item)
        print('Progress: ',items.index(item)+1,'/',len(items))
        films.write_doc()
    except TypeError:
        continue       #server error
logger.info("done")