from discord.ext import commands
import cogs._secrets as secret
import discord
import os


intents = discord.Intents.all()

bot = commands.Bot(command_prefix=secret.prefix, intents=intents, case_insensitive=True) # help_command=None,

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(platform='YouTube',name='Templates',game='Megadrive',url='https://www.youtube.com/watch?v=_pQ9XOPYvIk'))
    print("Bot is ready!")

@bot.event
async def on_command_error(ctx,error):
    if hasattr(ctx.command, 'on_error'):
        return
    



if __name__ == '__main__':
    # When running this file, if it is the 'main' file
    # i.e. its not being imported from another python file run this
    for file in os.listdir("cogs/"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(token=secret.bot_token)
