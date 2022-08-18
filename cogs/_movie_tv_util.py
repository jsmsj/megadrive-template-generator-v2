import re
from imdb import Cinemagoer
from googlesearch import search

import re


class ImdbObject:
    def __init__(self) -> None:
        self.ia = Cinemagoer()

    def id_from_imdblink(self,url):
        pattern = re.compile(r"https?://(www\.)?imdb\.com/title/tt(\d+)/?")
        matches = pattern.finditer(url)
        for match in matches:
            return str(match.group(2))

    def brute_imdb_link(self,name):
        query = name+ " site:imdb.com"
        pool = search(query, tld="com",num=1,stop=1,pause=2)
        for i in pool:
            return i
    
    def imdb_movie_list(self,name):
        return self.ia.search_movie(name)

    def movie_title_with_year(self,movie):
        try:
            name =  movie['title'] + " " + str(movie['year'])
        except:
            name = movie['title']
        return name

    def movie_id(self,movie):
        return movie.movieID

    def movie_obj(self,movie_id):
        return self.ia.get_movie(str(movie_id))

    def get_genre_list(self,imdb_movie_object):
        return imdb_movie_object.get('genres')

