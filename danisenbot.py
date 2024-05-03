import discord, os, configparser, setproctitle, logging
from discord.ext import commands

import nadanisen as dan
def privilege_check(ctx):
	#These are included as examples
	#Should be replaced immediately with the discordid of the bot runner
	#And the discord role for any danisen managers really
	#Taterade
	if ctx.author.id == 116390296819859463:
		return True
	#MixMasters TO
	elif ctx.author.get_role(111111111111111111111):
		return True
	if config.has_section(str(ctx.guild.id)):
		if config.has_option(str(ctx.guild.id), str(ctx.author.id)):
			return True
	return False
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
setproctitle.setproctitle("DanisenBot")
config = configparser.ConfigParser()
if not os.path.isfile('config.ini'):
	config['DEFAULT'] = {'key': 'value',
						'discordapikey': 'keygoeshere'}
	with open('config.ini', 'w') as configfile:
		config.write(configfile)
config.read('config.ini')
def initserver(ctx):
	if not config.has_section(str(ctx.guild.id)):
		config[str(ctx.guild.id)] = {
			'checkinslive': 'False',
			'protectedserver': 'False'
		}
		with open('config.ini', 'w') as configfile:
			config.write(configfile)
		return
	else:
		return

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

#TODO remove all prints to terminal and replace with info level logging outputs
@bot.command(name='addadmin')
async def addadmin(ctx, *args):
	if privilege_check(ctx):
		initserver(ctx)
		newadmin = args[0][2:-1]
		config[str(ctx.guild.id)][newadmin] = 'True'
		with open('config.ini', 'w') as configfile:
			config.write(configfile)

@bot.command(name='shutdown')
async def shutdown(ctx, *args):
	if privilege_check(ctx):
		with open('config.ini', 'w') as configfile:
			config.write(configfile)
		await ctx.send("Wrote config to file")
#####################DANISEN LEAGUE COMMANDS ###############################
@bot.command(name='register')
async def register(ctx, *args):
	for char in args:
		if not dan.validatecharacter(char):
			await ctx.send("""Invalid character sent
			$register <:BDAH:1075423369530441869> <:ELZA:1065450334102753290>""")
			return
	if len(args) == 0:
		await ctx.send("Don't forget to send your team")
	if len(args) == 1:
		point = args[0]
		mid = ""
		anchor = ""
	if len(args) == 2:
		point = args[0]
		mid = args[1]
		anchor = ""
	if len(args) == 3:
		point = args[0]
		mid = args[1]
		anchor = args[2]
	await ctx.send(dan.registerplayer(ctx.author.id, point, mid, anchor))
@bot.command(name='registerteam')
async def registerteam(ctx, *args):
	for char in args:
		if char == "1" or char == "2" or char == "3":
			teamnum = int(char)
			continue
		if not dan.validatecharacter(char):
			await ctx.send("""
			Invalid character sent
			$registerteam # <:BDAH:1075423369530441869> <:ELZA:1065450334102753290>""")
			return
	if len(args) == 2:
		point = args[1]
		mid = ""
		anchor = ""
	if len(args) == 3:
		point = args[1]
		mid = args[2]
		anchor = ""
	if len(args) == 4:
		point = args[1]
		mid = args[2]
		anchor = args[3]
	await ctx.send(dan.registerteam(ctx.author.id, teamnum, point, mid, anchor))
@bot.command(name='showprofile')
async def showprofile(ctx, *args):
	await ctx.send(dan.showprofile(ctx.author.id))
@bot.command(name='danisenreport')
async def danisenreport(ctx, *args):
	player1 = args[0][2:-1]
	player2 = args[2][2:-1]
	if int(player1) == ctx.author.id or int(player2) == ctx.author.id:
		valid_command = True
	else:
		valid_command = False
		await ctx.send("Can't report scores for sets you aren't part of")
		return
	await ctx.send(dan.danisenreportset(player1, player2))
@bot.command(name='setrank')
async def setrank(ctx, *args):
	if len(args) == 2:
		await ctx.send(dan.setrank(ctx.author.id, int(args[0]), int(args[1])))
@bot.command(name='removereports')
async def removereports(ctx, *args):
	if privilege_check(ctx):
		if dan.dailyReportClear():
			await ctx.send("Reports older than 24 hours from this message have been removed")
@bot.command(name='clearreports')
async def clearports(ctx, *args):
	if privilege_check(ctx):
		if dan.reportClear():
			await ctx.send("All ranked reports removed")
@bot.command(name='showranks')
async def showranks(ctx, *args):
	if privilege_check(ctx):
		ranks = dan.top50()
		count = 1
		output = "Top 50```\n"
		for player in ranks:
			user = await bot.fetch_user(player)
			output = output + ("%i) %s %s\n" % (count, user, ranks[player]))
			count += 1
		output = output +"```"
		await ctx.send(output)
@bot.command(name='removeuser')
async def removeuser(ctx, *args):
	if privilege_check(ctx):
		await ctx.send(dan.removePlayer(args[0]))
@bot.event
async def on_ready():
	logging.debug(f'We have logged in as {bot.user}')
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	await bot.process_commands(message)
bot.run(config['DEFAULT']['discordapikey'])