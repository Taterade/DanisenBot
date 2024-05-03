import sqlite3, time
con = sqlite3.connect("danisen.db")
cur = con.cursor()
def registercheck(discordid):
	res = con.execute("SELECT rowid FROM nasg WHERE discordid = ?", (discordid,))
	record = res.fetchall()
	if len(record) == 1:
		return True
	else:
		return False
def fancyrank(rank, diff):
	if diff < 0:
		return ("%i%i" % (rank, diff))
	else:
		return ("%i+%i" % (rank,diff))
def registerplayer(discordid, point, mid, anchor):
	#check if discord id is already registered
	#check if player is registered
	if not registercheck(discordid):
		params = (discordid, 1, 0, True, point, mid, anchor, False, ":fili:", ":fili:", ":fili", False, ":fili:", ":fili:", ":fili")
		con.execute("""
		INSERT INTO nasg VALUES 
		(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
		""", params)
		con.commit()
		return("Registered <@%s>"% discordid)
	else:
		return("You are already registered, follow instructions at https://discord.com/channels/878811708502736926/1061789808038510632/1209971602721079296")
	
def registerteam(discordid, teamnum, point, mid, anchor):
	#check if player is registered
	if not registercheck(discordid):
		return("You are not registered, follow instructions at https://discord.com/channels/878811708502736926/1061789808038510632/1209971602721079296")
	#check if this team is already registered
	#GOD THIS IS ANNOYING
	#check writing team 2 or 3
	#check if overwriting team 1 2 or 3
	#depending on team send update
	if teamnum == 1:
		cur.execute("""
		UPDATE nasg SET team1reg = ?, t1point = ?, t1mid = ?, t1anchor = ? WHERE discordid = ?"""
		, (1, point, mid, anchor, discordid))
	if teamnum == 2:
		cur.execute("""
		UPDATE nasg SET team2reg = ? , t2point = ? , t2mid = ? , t2anchor = ? WHERE discordid = ?"""
		, (1, point, mid, anchor, discordid))
		con.commit()
	if teamnum == 3:
		cur.execute("""
		UPDATE nasg SET team3reg = ?, t3point = ?, t3mid = ?, t3anchor = ? WHERE discordid = ?"""
		, (1, point, mid, anchor, discordid))
	con.commit()
	return("Registered team")
def adjustscore(discordid, up, down, gap):
	#check if player is registered
	if not registercheck(discordid):
		return("You are not registered, follow instructions at https://discord.com/channels/878811708502736926/1061789808038510632/1209971602721079296")
	#check if user is about to +/- 5 and change overall ranks
	res = cur.execute("SELECT * FROM nasg WHERE discordid = ?", (discordid,))
	record = res.fetchone()
	rank = int(record[1])
	differential = int(record[2])
	if up:
		if rank == 5:
			differential = differential + gap
		else:
			if (gap + differential) >= 5:
				rank += 1
				differential = 0
			else:
				differential = differential + gap
	if down:
		if rank == 1:
			if (differential - gap) <= 0:
				differential = 0
			else:
				differential - gap
		else:
			if (differential - gap) <= -5:
				differential = 0
				rank -= 1
			else:
				differential = differential - gap
	# if down and rank == 1:
	# 	if differential != 0:
	# 		differential -= 1
	params = (rank, differential, discordid)
	cur.execute("""
	UPDATE nasg SET rank = ?, differential = ? WHERE discordid = ?"""
	, (rank, differential, discordid))
	con.commit()
	return	
def danisenreportset(winner, loser):
	#check if player is registered
	if not registercheck(winner):
		return("Both players must be registered")
	#check if player is registered
	if not registercheck(loser):
		return("Both players must be registered")
	if checkReport(winner, loser):
		res = con.execute("SELECT * FROM nasg WHERE discordid = ?", (winner,))
		record = res.fetchone()
		winnerrank = int(record[1])
		res = con.execute("SELECT * FROM nasg WHERE discordid = ?", (loser,))
		record = res.fetchone()
		loserrank = int(record[1])
		rankdiff = winnerrank - loserrank
		if rankdiff >= 0:
			adjustscore(winner, True, False, 1)
			adjustscore(loser, False, True, 1)
		if rankdiff <= -1:
			rankdiff = rankdiff * -1
			adjustscore(winner, True, False, rankdiff)
			adjustscore(loser, False, True, rankdiff)
		return("Players updated")
	else:
		return("24 hours have not passed since last match between these players.")
	#possibly add check that these two players haven't played within 24 hours
	#db table to prevent record loss
	
def setrank(discordid, rank, differential):
	#check if player is registered
	if not registercheck(discordid):
		return("You are not registered, follow instructions at https://discord.com/channels/878811708502736926/1061789808038510632/1209971602721079296")
	if rank > 5 or rank < 1:
		return("You are not the god of SG please set a valid rank (1-5)")
	if differential < -4 or differential > 4:
		return("Differentials can only be set from -4 to 4")
	res = con.execute("SELECT * FROM nasg WHERE discordid = ?", (discordid,))
	record = res.fetchone()
	oldrank = int(record[1])
	olddiff = int(record[2])
	#straight forward just let people set their rank, abuses will be taken out back and
	params = (rank, differential, discordid)
	cur.execute("""
	UPDATE nasg SET rank = ? , differential = ? WHERE discordid = ?"""
	, (rank, differential, discordid))
	con.commit()
	return ("Rank was changed from %s to %s" % (fancyrank(oldrank, olddiff), fancyrank(rank, differential)))
def showprofile(discordid):
	#check if player is registered
	if not registercheck(discordid):
		return("You are not registered, follow instructions at https://discord.com/channels/878811708502736926/1061789808038510632/1209971602721079296")
	#retrieve all teams, report to player
	#probably just use a boolean for knowing if a 2nd and 3rd team are registerec
	#output = record[1] + " " + record[2] "-" + record[3]
	res = con.execute("SELECT * FROM nasg WHERE discordid = ?", (discordid,))
	record = res.fetchone()
	output = ("Rank %s\n" % (fancyrank(record[1], record[2])))
	output =  output + ("Teams:\n%s %s %s\n" % (record[4], record[5], record[6]))
	if (record[7]):
		output = output + ("%s %s %s\n" % (record[8], record[9], record[10]))
	if (record[11]):
		output = output + ("%s %s %s\n" % (record[12], record[13], record[14]))
	return output
def validatecharacter(character):
	actors = ["<:ANIE:1065449280107724860>", "<:BAND:1065450184923955240>", 
	"<:BDAH:1075423369530441869>", "<:CERE:1065449471657377902>", 
	"<:DBBL:1065450062542544947>", "<:ELZA:1065450334102753290>", 
	"<:FILI:1065449406968635464>", "<:FORT:1065449918665326703>", 
	"<:FUKU:1065450260463366265>", "<:PAIN:1065449797361868860>", 
	"<:PARA:1065449651030982809>", "<:PEAK:1065449861903822938>", 
	"<:ROBO:1065450384233074728>", "<:SQIG:1065450118301634702>", 
	"<:UMBR:1065450443146268753>", "<:VALN:1065449986025865228>", 
	"<:WULF:1065449525013135430>", "<:MARI:1222241904687845499>"]
	return (character in actors)
def addReport(player1, player2):
	currentdatetime = int(time.time())
	cur.execute("""INSERT INTO nasg_reports VALUES (?,?,?)""", (player1, player2, currentdatetime))
	con.commit()
	return True
def checkReport(player1, player2):
	res = cur.execute("SELECT * FROM nasg_reports WHERE player1 = ? AND player2 = ?", (player1,player2))
	result = res.fetchone()
	currentdatetime = int(time.time())
	twentyfourhoursinseconds = 86400
	if not result is None:
		if (currentdatetime - int(result[2])) >= twentyfourhoursinseconds:
			res = cur.execute("DELETE FROM nasg_reports WHERE player1 = ? AND player2 = ?", (player1,player2))
			addReport(player1, player2, currentdatetime)
			return True
		else:
			return False
	res = cur.execute("SELECT * FROM nasg_reports WHERE player1 = ? AND player2 = ?", (player2,player1))
	result = res.fetchone()
	if not result is None:
		if (currentdatetime - int(result[2])) >= twentyfourhoursinseconds:
			res = cur.execute("DELETE FROM nasg_reports WHERE player1 = ? AND player2 = ?", (player2,player1))
			addReport(player1, player2)
			return True
		else: 
			return False
	return addReport(player1, player2)
def dailyReportClear():
	currentdatetime = int(time.time())
	onedayago = currentdatetime - 86400
	res = cur.execute("DELETE FROM nasg_reports WHERE time < ?", (onedayago,))
	con.commit()
	return True
def reportClear():
	onedayago = 1
	res = cur.execute("DELETE FROM nasg_reports WHERE time > ?", (onedayago,))
	con.commit()
	return True
def top50():
	res = cur.execute("SELECT * FROM nasg ORDER BY rank DESC, differential DESC")
	record = res.fetchall()
	count = 1
	dict50 = {}
	for ranking in record:
		dict50[int(ranking[0])] = "%s" % fancyrank(ranking[1], ranking[2])
		count += 1
		if count >50:
			break
	return dict50
def removePlayer(player):
	if not registercheck(player):
		return "That player doesn't exist"
	else:
		res = cur.execute("DELETE FROM nasg WHERE discordid = ?", (player,))
		con.commit()
		return "Removed %s"
