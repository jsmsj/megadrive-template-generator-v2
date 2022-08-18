from AnilistPython import Anilist
from pprint import pprint

class AnimeMd:
    def __init__(self) -> None:
        self.anilist = Anilist()
    
    def search_anime_by_name_get_ids(self,name):
        """Give a search term and get (id,romaji_title,english_title)"""
        anime_list = []
        data = self.anilist.anime.extractID.anime(name)
        for i in range(len(data['data']['Page']['media'])):
            curr_anime = (data['data']['Page']['media'][i]['id'],data['data']['Page']['media'][i]['title']['romaji'],data['data']['Page']['media'][i]['title']['english'])
            anime_list.append(curr_anime)
        return anime_list
    
    def get_anime_details(self,anime_id):
        """Give anime id and get (genres,romaji_title,english_title)"""
        data = self.anilist.anime.extractInfo.anime(anime_id)
        return (data['data']['Media']['genres'],data['data']['Media']['title']['romaji'],data['data']['Media']['title']['english'])
    
        


# anilist = Anilist()

# anime_list = []
# data = anilist.anime.extractID.anime('Seraph of the End')
# pprint(data)
# for i in range(len(data['data']['Page']['media'])):
#     curr_anime = data['data']['Page']['media'][i]['title']['romaji']
#     anime_list.append(curr_anime)

# anime_ID = data['data']['Page']['media'][0]['id']

# info = anilist.anime.extractInfo.anime(anime_id=1735)

# pprint(info)

# pprint(anime_list)

# a = AnimeMd()
# print(a.search_anime_by_name_get_ids('Dan Doh!!'))