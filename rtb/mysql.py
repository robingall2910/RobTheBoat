import sqlite3

conn = sqlite3.connect("data/Some Dragon.db")
cur = conn.cursor()

def create_table():
    cur.execute("CREATE TABLE IF NOT EXISTS servers(id TEXT, type TEXT, value TEXT)")

def insert_data_entry(id, type, value):
    cur.execute("""INSERT INTO servers(id, type, value) VALUES (?, ?, ?)""", (id, type, value))
    conn.commit()

def read_data_entry(id, type):
    cur.execute("""SELECT value FROM servers WHERE id=""" + id + """ AND type='""" + type + """'""")
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
        elif type == "ignore-role":
            insert_data_entry(id, type, "Dragon Ignorance")
            val = "Dragon Ignorance"
        elif type == "system-on":
            insert_data_entry(id, type, "yes")
            val = "yes"
    return val

def update_data_entry(id, type, value):
    cur.execute("""UPDATE servers SET value='""" + value + """' WHERE id=""" + id + """ AND type='""" + type + """'""")
    conn.commit()

def delete_data_entry(id, type):
    cur.execute("""DELETE FROM servers WHERE id=""" + id + """ AND type='""" + type + """'""")
    conn.commit()

#insert_data_entry("209784725559181312", "mod-role", "Fucking admin")
#read_data_entry("209784725559181312", "mod-role")
#update_data_entry("209784725559181312", "mod-role", "Fucking mod")
#delete_data_entry("209784725559181312", "mod-role")