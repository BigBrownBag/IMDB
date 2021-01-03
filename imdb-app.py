import requests
from bs4 import BeautifulSoup
import logging

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
        film_genre = self.soup.select('div.subtext a')
        genre = [tag.text for tag in film_genre]
        return genre

    def get_rating(self):
        film_rating = self.soup.select('div.ratingValue strong span')
        rating = [tag.text for tag in film_rating]
        return rating[0].replace(u'\xa0', u' ')

    def get_topcast(self):
        film_cast = self.soup.select('div.credit_summary_item a')
        cast = [tag.text for tag in film_cast]
        return f"{cast[0]}, {cast[1]}, {cast[2]}"

    def get_details(self):
        film_details = self.soup.select('div#titleDetails')
        details = [tag.text for tag in film_details]
        return details[0].replace(u'\nSee more\xa0»\n', u'').replace(u'Show more on\n  IMDbPro\xa0»\n', u'').replace(u'See full technical specs\xa0»\n', u'').replace(u'\n\nEdit\n\n', u'')

logging.basicConfig(level=logging.DEBUG, filename='imdb-app.log', format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
items = []
link_next = '/search/title/'
filters = {
    'genres' : [], #action adventure animation biography comedy crime documentary drama family fantasy film_noir game_show history horror music musical mystery news reality_tv romance sci_fi sport talk_show thriller war western
    'title_type' : 'tv_movie', #feature, tv_movie, tv_series, tv_episode, tv_special, tv_miniseries, tv_miniseries, documentary, video_game, short, video, tv_short
    'user_rating-min' : '', #from 1.0 to 10.0
    'countries:' : '',
    'release_date-min:' : '', #Format: YYYY-MM-DD, YYYY-MM, or YYYY
    'release_date-max:' : '',
}             
try:
    while len(items)<1000:
        URL = 'https://www.imdb.com'+link_next
        result = requests.post(URL, params=filters)
        soup = BeautifulSoup(result.text, 'html.parser')
        temporary = soup.select('h3.lister-item-header a')
        link_next = soup.select('a.next-page')[0].get('href')
        for links in temporary:
            items += [links.get('href')]
        logger.info(f"found {len(items)} films") 
except IndexError:
    for links in temporary:
            items += [links.get('href')]
    logger.info(f"found {len(items)} films") 
logger.info("parsing in progress...")
f = open('films.txt', 'w', encoding='utf-8')
try:
    for item in items:
        films = PythonIMDB(item)
        f.write(films.get_title() + '\n')
        for i in range(1,len(films.get_genre())-1):
            f.write(films.get_genre()[i]+' ')
        f.write('\n')
        f.write(films.get_rating() + '\n')
        f.write(films.get_topcast() + '\n')
        f.write(films.get_details() + '\n')
        f.write('----------------' + '\n')
except IndexError:
    f.write(films.get_topcast() + '\n')
    f.write(films.get_details() + '\n')
    f.write('----------------' + '\n')
f.close()
logger.info("done")