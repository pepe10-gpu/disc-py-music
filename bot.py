import asyncio

import discord

import random

import youtube_dl

yag = ["made by yoink!", "google dont sue us-", "Celeste", "no premium feature", "Long live rythym!", "with cats!", "Long live groovy!", "yeah", "fnf fanworks", "Garry's Mod", "VR", "not monetized!"]
from discord.ext import commands

convar_token = "insert token"

# made by yoinked
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        """plays a yt song"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Playing: {player.title}')
    #self.assert_(boolean expression, 'message')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if volume > 0 and volume < 250:

            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f"Changed volume to {volume}%")
        else:

            ctx.voice_client.source.volume = 100
            await ctx.send("no.")


    @commands.command()
    async def rng(self, ctx, dice: int):
        """Ask RNGesus a thing"""

        if dice > 1:
            await ctx.send("You rolled a " + str(random.randint(1,dice)) + "." )
        else:
            await ctx.send("no.")
    #aa
    @commands.command()
    async def cool(self, ctx):
        """Check if youre cool B)"""
        if random.randint(1,2) == 2:
            await ctx.send("You are cool!" )
        else:
            await ctx.send("lame!.")
    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"),
                   description='rhythm clone')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=yag[random.randint(0,(len(yag) - 1))]))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('--------------------------------------------')

bot.add_cog(Music(bot))
bot.run(convar_token)
