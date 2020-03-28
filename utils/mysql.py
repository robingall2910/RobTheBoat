import sqlite3

#change this if you're running it from somewhere else
conn = sqlite3.connect("RTB Blacklist.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def create_tables():
    cur.execute("""CREATE TABLE IF NOT EXISTS guilds(id TEXT, type TEXT, value TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS blacklist(id TEXT, name TEXT, discrim TEXT, reason TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS lockdown(id TEXT, servername TEXT, channame TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS markov(messages TEXT, serverid TEXT, userid TEXT)""")

def format_user(insertnerovar):
    return insertnerovar.name + "#" + insertnerovar.discriminator

def insert_data_entry(id, type, value):
    cur.execute("""INSERT INTO guilds(id, type, value) VALUES (?, ?, ?)""", (id, type, value))
    conn.commit()

def read_data_entry(id, type):
    cur.execute("""SELECT value FROM guilds WHERE id=(?) AND type=(?)""", (id, type))
    val = None
    try:
        val = cur.fetchone()[0]
    except:
        if type == "mod-role":
            insert_data_entry(id, type, "Dragon Commander")
            val = "Dragon Commander"
        elif type == "nsfw-channel":
            insert_data_entry(id, type, "nsfw")
            val = "nsfw"
        elif type == "mute-role":
            insert_data_entry(id, type, "Dragon Ignorance")
            val = "Dragon Ignorance"
        elif type == "join-message":
            insert_data_entry(id, type, None)
            val = None
        elif type == "leave-message":
            insert_data_entry(id, type, None)
            val = None
        elif type == "join-leave-channel":
            insert_data_entry(id, type, None)
            val = None
        elif type == "join-role":
            insert_data_entry(id, type, None)
            val = None
    return val

def update_data_entry(id, type, value):
    exists = read_data_entry(id, type)
    cur.execute("""UPDATE guilds SET value=(?) WHERE id=(?) AND type=(?)""", (value, id, type))
    conn.commit()

def delete_data_entry(id, type):
    cur.execute("""DELETE FROM guilds WHERE id=(?) AND type=(?)""", (id, type))
    conn.commit()

def blacklistuser(id, name, discrim, reason):
    cur.execute("""INSERT INTO blacklist(id, name, discrim, reason) VALUES (?, ?, ?, ?)""", (id, name, discrim, reason))
    conn.commit()

def unblacklistuser(id):
    cur.execute("""DELETE FROM blacklist WHERE id=""" + str(id))
    conn.commit()

def getblacklistentry(id):
    cur.execute("""SELECT id FROM blacklist WHERE id=""" + str(id))
    id = None
    name = None
    discrim = None
    reason = None
    try:
        id = cur.fetchone()[0]
    except:
        return None
    cur.execute("""SELECT name FROM blacklist WHERE id=""" + id)
    name = cur.fetchone()[0]
    cur.execute("""SELECT discrim FROM blacklist WHERE id=""" + id)
    discrim = cur.fetchone()[0]
    cur.execute("""SELECT reason FROM blacklist WHERE id=""" + id)
    reason = cur.fetchone()[0]
    blacklistentry = {"id":id, "name":name, "discrim":discrim, "reason":reason}
    return blacklistentry

def lockdownchannel(id, servername, channame):
    cur.execute('INSERT INTO lockdown(id, servername, channame) VALUES (?, ?, ?)', (id, servername, channame))
    conn.commit()

def removelockdownchannel(id):
    cur.execute("""DELETE FROM lockdown WHERE id=""" + str(id))

def getlockdowninfo():
    cur.execute('SELECT id, servername, channame FROM lockdown')
    entries = []
    rows = cur.fetchall()
    for row in rows:
        entry = "ID: \"" + row["id"] + "\" Server Name: \"" + row["servername"] + "\" Channel Name: \"" + row["channame"] + "\""
        entries.append(entry)
    return entries

def getquicklockdownstatus():
    cur.execute('SELECT id FROM lockdown')
    entries = []
    meme = cur.fetchall()
    for row in meme:
        entry = row['id']
        entries.append(entry)
    return entries

def getblacklist():
    cur.execute("""SELECT id, name, discrim, reason FROM blacklist""")
    entries = []
    rows = cur.fetchall()
    for row in rows:
        entry = "ID: \"" + row["id"] + "\" Name: \"" + row["name"]  + "\" Discrim: " + row["discrim"] + " Reason: \"" + row["reason"] + "\""
        entries.append(entry)
    return entries

def addword(item_text, serverid, userid):
    msg = 'INSERT INTO markov (messages, serverid, userid) VALUES (?, ?, ?)'
    args = (item_text, serverid, userid)
    cur.execute(msg, args)
    conn.commit()

def delword(item_text):
    msg = 'DELETE FROM markov WHERE messages = (?)'
    args = (item_text, )
    cur.execute(msg, args)
    conn.commit()

def getmsgs():
    msg = 'SELECT messages FROM markov'
    return [x[0] for x in cur.execute(msg)]

def getmsgsuser(userid):
    msg = 'SELECT userid FROM markov WHERE userid=' + userid
    return [x[0] for x in cur.execute(msg)]

create_tables()
