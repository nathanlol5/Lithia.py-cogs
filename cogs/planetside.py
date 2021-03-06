import random
from discord.ext import commands
import discord
import json
import aiohttp
import urllib.request
import datetime
import asyncio
import time
import auraxium
from auraxium import ps2

class Planetside(commands.Cog):
    def __init__(self, client):
        self.client = client

        #Default Variables, Probably better way to do this?
        self.EasterEggs = ["https://media.discordapp.net/attachments/723022911589580832/801699761933123634/Chimken_Sandwhich.gif", "https://media.discordapp.net/attachments/296056831514509312/791652552826814464/image0-448.gif", "https://media.discordapp.net/attachments/193278651020738561/779947007670222848/which.gif"]
        self.PS2Images = ["https://cdn.discordapp.com/app-assets/309600524125339659/517514078227398677.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514073433309194.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514062985428993.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514065401217036.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514084455809034.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514083352969216.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514082136358916.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514072778866688.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514073055821825.png","https://cdn.discordapp.com/app-assets/309600524125339659/517514077812293643.png"]
        self.servernum = {'briggs':25, "jaeger":19, 'connery':1,'miller':10,'emerald':17,'cobalt':13,'soltech':40}
        self.servers = ['briggs', "jaeger", 'connery','miller','emerald','cobalt','soltech']
        self.ps2icon = "https://pbs.twimg.com/profile_images/883060220779532288/zViSqVuM_400x400.jpg"
        self.icons = {'nc':'<:NC:528718336180092938>','vs':'<:VS:528718387627687936>','tr':'<:TR:528718372192649237>','NS':'<:NS:740268320988725381>'}
        self.colors = {'nc':0x0080ff,'vs':0x740084,'tr':0xa40000}
        self.NewCheckTime = 300

        #Default loading Embed, Probably a better to put this inside the actual command?
        self.PS2_Loading_Embed=discord.Embed(color=0xc0c0c0)
        self.PS2_Loading_Embed.set_thumbnail(url=f"https://cdn.discordapp.com/attachments/802538687698567178/805190014588682270/planetside.webp")
        self.PS2_Loading_Embed.add_field(name=f'Population', value=f'``🔵`` ``...``\n``🟣`` ``...``\n``🔴`` ``...``', inline=True)
        self.PS2_Loading_Embed.add_field(name='Statistics', value=f'``Loading...``\n``POP :`` ``...``\n``OP  :`` ``...``', inline=True)
        self.PS2_Loading_Embed.set_footer(text=f"| PS2.FISU.PW RT-API | {datetime.datetime.utcnow()} |")

        #Default EasterEgg Embed for old Briggs server, Probably better to embed this into the actual command?
        self.BRIGGS_Embed=discord.Embed(color=0xc0c0c0)
        self.BRIGGS_Embed.set_thumbnail(url=f"{random.choice(self.PS2Images)}")
        self.BRIGGS_Embed.add_field(name=f'Briggs', value=f'``🔵`` ``0 : 0%``\n``🟣`` ``1 : 100%``\n``🔴`` ``0 : 0%``', inline=True)
        self.BRIGGS_Embed.add_field(name='Statistics', value=f'``POP :`` Thanks\n``OP  :`` Diamond\n``WIN :`` Wing', inline=True)
        self.BRIGGS_Embed.set_footer(text=f"| PS2.FISU.PW RT-API | {datetime.datetime.utcnow()} |")

        #Query cache variables, Not utilizing these right now.
        self.briggsTime   = None
        self.jaegerTime   = None
        self.conneryTime  = None
        self.millerTime   = None
        self.emeraldTime  = None
        self.colbaltTime  = None
        self.soltechTime  = None

        self.briggsData     = None
        self.jaegerData     = None
        self.conneryData    = None
        self.millerData     = None
        self.emeraldData    = None
        self.colbaltData    = None
        self.soltechData    = None


    def JsonGrab(self, URL, seconds = 15):
        try:
            data = json.loads(urllib.request.urlopen(URL, timeout=seconds).read().decode("utf8"))
        except urllib.error.URLError:
            return 'URLERROR'
        else:
            return data

    def PS2WorldGrab(self, WorldID):
        return self.JsonGrab(f"http://ps2.fisu.pw/api/population/?world={WorldID}")

    def PS2EmbedGen(self, JData, ServerName = "Server_Name"):
        """Generates Embeds from supplied data"""
        #Extracting data from JSON.
        NC = JData['result'][0]['nc']
        VS = JData['result'][0]['vs']
        TR = JData['result'][0]['tr']

        #Calculating population percentages.
        total = NC+VS+TR
        if NC is not 0: NCPERC = round(NC/total*100)
        else: NCPERC = NC
        if VS is not 0: VSPERC = round(VS/total*100)
        else: VSPERC = VS
        if TR is not 0: TRPERC = round(TR/total*100)
        else: TRPERC = TR

        #Calculating Overpopuled Faction. (probably a better way to do this?)
        if max(TR, NC, VS) == 0:
            embedcolor = 0xc0c0c0
            OverPOP = "NS"
        elif TR == max(TR, NC, VS):
            embedcolor = 0xa40000
            OverPOP = "TR"
        elif NC == max(TR, NC, VS):
            embedcolor = 0x0080ff
            OverPOP = "NC"
        elif VS == max(TR, NC, VS):
            embedcolor = 0x740084
            OverPOP = "VS"

        #Easter Egg?
        if random.randint(0,100) < 10: EmbedImage = random.choice(self.EasterEggs)
        else: EmbedImage = random.choice(self.PS2Images)

        #Generating the Embed.
        ps2embed=discord.Embed(color=embedcolor)
        ps2embed.set_thumbnail(url=f"{EmbedImage}")
        ps2embed.add_field(name=f'Population', value=f'``🔵`` ``{NC} : {NCPERC}%``\n``🟣`` ``{VS} : {VSPERC}%``\n``🔴`` ``{TR} : {TRPERC}%``', inline=True)
        ps2embed.add_field(name='Statistics', value=f'``{ServerName.upper()} [{self.servernum[ServerName]}]``\n``POP :`` ``{total}``\n``OP  :`` ``{OverPOP}``', inline=True)
        ps2embed.set_footer(text=f"| PS2.FISU.PW RT-API | {datetime.datetime.utcnow()} |")

        #Return a generated embed.
        return ps2embed


    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(pass_context=True, aliases=['jaeger', 'Jaeger', 'connery', 'Connery', 'miller', 'Miller', 'emerald', 'Emerald', 'cobalt', 'Cobalt', 'soltech', 'Soltech'])
    async def Planetside(self, ctx):
        """
        Checks the status of a Planetside2 Server.
        Usage: {ServerName}
        """
        server = ctx.message.content.split()[0][1:].lower()
        if server in self.servers:
            try:
                MSG = await ctx.reply('<https://github.com/NathanLithia/>', embed=self.PS2_Loading_Embed)
                #start_time = time.time()
                setattr(self, f"{server}Data", self.PS2EmbedGen(self.PS2WorldGrab(self.servernum[server]), server))
                await MSG.edit(content=f'<https://github.com/NathanLithia/>',embed=getattr(self, f"{server}Data"))
                #else:
                #    MSG = await ctx.send(f"{ctx.message.author.mention} ``CACHED``", embed=getattr(self, f"{server}Data"))
            except Exception as e: await ctx.send(f'{e}')


    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.command(pass_context=True, aliases=['briggs'])
    async def Briggs(self, ctx):
        await ctx.send(f'{ctx.message.author.mention}', embed=self.BRIGGS_Embed)


    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.command(pass_context=True, aliases=['ceres', 'Ceres', 'genudine', 'Genudine'])
    async def PS2Unsupported(self, ctx):
        await ctx.reply(f'Playstation® PlanetSide 2 servers are not planned to be supported.')


    #Experimental command.
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.command(pass_context=True)
    async def Online(self, ctx, character):
        """
        Checks Status of a Planetside2 Character.
        Usage: Online {Character}
        """
        if character == None: return
        else:
            async with auraxium.Client() as cli:
                char = await cli.get_by_name(ps2.Character, f'{character}')

                status = await char.is_online()
                if status == True: status = "Online"
                else: status = "Offline"

                faction = await char.faction()
                outfit = await char.outfit()
                world = await char.world()
                stat = await char.stat()
            await ctx.send(f'``[{outfit}] {char.name()}``\nFaction = {faction}\nStatus = {status}\nWorld = {world}\n')
            await ctx.send(f'stat {stat}')
            asyncio.get_event_loop().run_until_complete(main())


    #Experimental command.
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.command(pass_context=True)
    async def KD(self, ctx, character):
        if character == None: return
        else:
            async with auraxium.Client() as cli:
                char = await cli.get_by_name(ps2.leaderboard, f'{character}')

                status = await char.is_online()
                if status == True: status = "Online"
                else: status = "Offline"

                faction = await char.faction()
                outfit = await char.outfit()
                world = await char.world()
                stat = await char.stat()
            await ctx.send(f'``[{outfit}] {char.name()}``\nFaction = {faction}\nStatus = {status}\nWorld = {world}\n')
            await ctx.send(f'stat {stat}')
            asyncio.get_event_loop().run_until_complete(main())


def setup(client):
    client.add_cog(Planetside(client))