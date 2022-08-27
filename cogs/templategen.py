"""Imports"""
import discord
from discord.ext import commands
import cogs._secrets as secret
from cogs._anime_util import AnimeMd
import aiohttp
import urllib.parse
from cogs._name_parser import get_title_from_name,get_year_from_name
import requests
from cogs._movie_tv_util import ImdbObject
from cogs._sizecheck import service,GoogleDriveSizeCalculate
import os

import base64
import asyncio

def b64e(s):
    return base64.urlsafe_b64encode(s.encode()).decode()


# def b64d(s):
#     return base64.b64decode(s).decode()

def gen_template(genre:list,name,size,link,external_link=None):
    msg = ""
    if not len(genre) == 0:
        msg+=f"`{' | '.join(genre)}`\n"
    msg+=f":drive: **{name}**\n\n"
    msg+=f"> Download Link: <{link}>\n"
    msg+=f"> Size: **{size}**\n\n"
    if external_link:
        msg+=external_link
    if secret.custom_message:
        msg+=f"\n\n{secret.custom_message}"

    return msg


def encode_link(link,author):
    # https://links.gamesdrive.net/#/link/{base64}.{uploaderB64}
    e_link = b64e(link)
    e_author = b64e(author)
    return f"https://links.gamesdrive.net/#/link/{e_link}.{e_author}"
    

class TemplateGenerator(commands.Cog):
    """TemplateGenerator commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """ 
        await ctx.trigger_typing()    
        return

    @commands.command()
    async def template(self,ctx:commands.Context,*,link=None):
        """This is used to generate template by providing a google drive link."""
        if not link: return await ctx.send(f"Please provide the link. `{secret.prefix}template https://drive.google.com/whatever`")

        category_message = """Choose a category and send the corrosponding number:
        1.  `🎎 Anime`
        2. `📽️ Movie / 📺 TV show`
        3. `🐉 Miscellaneous`
        """
        await ctx.send(category_message)
        def check(m):
            return m.author == ctx.author
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send('You did not tell me the category, so I\'m exiting the command. Kindly re-run the command. AND DO MENTION THE CAREGORY this time :)')

        try:
            category = ['anime','movie/tv','misc'][int(msg.content)-1]
        except (ValueError,IndexError):
            return await ctx.send('Error, the chosen number is not valid / or you had sent some text instead of number.')

        async with ctx.typing():
            if os.getenv('private_key') and os.getenv('sa_email'):
                calculator = GoogleDriveSizeCalculate(service)
                file_details = calculator.gdrive_checker(link)
            else:
                resp = requests.post('http://gdrivesize.jsmsj.repl.co/checksize',json={"link":link})
                print(resp.status_code)
                file_details = resp.json()



        name = get_title_from_name(file_details['name'])
        if name in ['',None,False] : name = file_details['name']
        
        ask_if_name_correct = await ctx.send(f'Is this the TITLE of the anime/movie/tv-show ?\n`{name}`\n\nIf yes then **reply `yes`**, else reply with the correct title.')
        try:
            confirmation_msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send('AH i Timed out. You should responded under 60 seconds the next time you run the command!')
        if confirmation_msg.content.lower() != 'yes':
            name = confirmation_msg.content
        
        async with ctx.typing():
            if category == 'anime':
                anime = AnimeMd()
                which_anime_msg_content = ""
                anime_list = anime.search_anime_by_name_get_ids(name)
                if not len(anime_list) == 0:
                    if len(anime_list) != 1:
                        for idx,val in enumerate(anime_list):
                            which_anime_msg_content+= f"{idx+1}. {val[2]} | {val[1]}\n"
                        temp = 'Choose the index number besides the name of the anime\nEg: reply 2 for the second value\nIf your anime is not in the list, then it is not listed on Anilist.\nKindly generate the template yourself\n'
                        temp+=f'```\n{which_anime_msg_content[:1750:]}\n```'
                        choose_anime_msg = await ctx.send(temp)
                        try:
                            chosen_anime_msg = await self.bot.wait_for('message', check=check,timeout=60)
                        except asyncio.TimeoutError:
                            return await ctx.send('I timed out! please respond under 60 seconds the next time you run this command!')
                        try:
                            chosen_anime = anime_list[int(chosen_anime_msg.content)-1]
                        except (ValueError,IndexError):
                            return await ctx.send('You didnt choose a number/or the number chosen is not valid')
                    else:
                        chosen_anime = anime_list[0]
                    anime_id = chosen_anime[0]
                    anime_details = anime.get_anime_details(anime_id)
                    genres_list = anime_details[0]
                    romaji_title = anime_details[1]
                    external_link = f"https://anilist.co/anime/{anime_id}/{urllib.parse.quote(romaji_title)}/"

                    ultimate = gen_template(genres_list,file_details['name'].replace('.', ' '),file_details['size'],encode_link(link,ctx.author.name),external_link)

                    await ctx.send(ultimate)
                    await ctx.send(f'```\n{ultimate}\n```')
                else:
                    return await ctx.send('No anime found. Kindly generate the template yourself.')

            elif category =='movie/tv':
                imdb_obj = ImdbObject()
                year = get_year_from_name(file_details['name'])
                try:
                    year = int(year)
                except:
                    year = None
                final_name = name +" " + str(year) if year else name 
                list_of_movies = imdb_obj.imdb_movie_list(final_name)
                if len(list_of_movies) == 0:
                    imdb_lnk = imdb_obj.brute_imdb_link(final_name)
                    if imdb_lnk:
                        mov_id = imdb_obj.id_from_imdblink(imdb_obj.brute_imdb_link(final_name)).replace(" ","")
                        if mov_id == "":return await ctx.send('No movie/tv found. Kindly generate the template yourself.')
                        imdb_id = mov_id
                    else:
                        return await ctx.send('No movie/tv found. Kindly generate the template yourself.')
                elif len(list_of_movies) == 1:
                    imdb_id = imdb_obj.movie_id(list_of_movies[0])
                else:
                    movie_ls = []
                    for i,movie in enumerate(list_of_movies):
                        movie_ls.append(f'{i+1}. {imdb_obj.movie_title_with_year(movie)}')
                    temp = 'Choose the index number besides the name of the movie/tv-show\nEg: reply 2 for the second value\nIf your movie/tv-show is not in the list, then it is not listed on IMDB, or the bot cannot get it.\nKindly generate the template yourself\n'
                    temp+='```\n'
                    temp+='\n'.join(movie_ls)[:1750:]
                    temp+='\n```'
                    movie_list_msg = await ctx.send(temp)
                    try:
                        chosen_movie_msg = await self.bot.wait_for('message', check=check, timeout=60)
                    except asyncio.TimeoutError:
                        return await ctx.send('I timed out! please respond under 60 seconds the next time you run this command!')
                    try:
                        chosen_movie = list_of_movies[int(chosen_movie_msg.content)-1]
                    except (ValueError,IndexError):
                        return await ctx.send('You didnt choose a number/or the number chosen is not valid')
                    imdb_id = imdb_obj.movie_id(chosen_movie)

                list_of_genres = imdb_obj.get_genre_list(imdb_obj.movie_obj(imdb_id))
                external_link = f"https://www.imdb.com/title/tt{imdb_id}"

                ultimate = gen_template(list_of_genres,file_details['name'].replace('.', ' '),file_details['size'],encode_link(link,ctx.author.name),external_link)

                await ctx.send(ultimate)
                await ctx.send(f'```\n{ultimate}\n```')

            elif category == 'misc':
                ultimate = gen_template([],file_details['name'].replace('.', ' '),file_details['size'],encode_link(link,ctx.author.name))
                await ctx.send(ultimate)
                await ctx.send(f'```\n{ultimate}\n```')
        

        

        


def setup(bot):
    bot.add_cog(TemplateGenerator(bot))
    print("TemplateGenerator cog is loaded")