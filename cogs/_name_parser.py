# https://github.com/platelminto/parse-torrent-title
import PTN

def get_title_from_name(name):
    return PTN.parse(name).get('title')

def get_year_from_name(name):
    return PTN.parse(name).get('year')