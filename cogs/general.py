"""Imports"""
import discord
from discord.ext import commands

class General(commands.Cog):
    """General commands"""

    def __init__(self, bot):
        self.bot:commands.Bot = bot

    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """
        await ctx.trigger_typing()    
        return

    @commands.command()
    async def ping(self,ctx):
        """Used to check if bot is alive"""
        await ctx.send(f'🏓 Pong! Latency: {round(self.bot.latency*1000)}ms')
    
    @commands.slash_command(name='ping',description='Used to check if bot is alive')
    async def slash_ping(self,ctx):
        """Used to check if bot is alive"""
        await ctx.send(f'🏓 Pong! Latency: {round(self.bot.latency*1000)}ms')


def setup(bot):
    bot.add_cog(General(bot))
    print("General cog is loaded")