import re
import requests
import discord

_USER_ID_MATCH = re.compile(r"<@(\d+)>")

_EMOTE_ID_MATCH = re.compile(r"<:(.+?):(\d+)>")

py = "```py\n{}```"

xl = "```xl\n{}```"

diff = "```diff\n{}```"

def write_file(filename, contents):
    with open(filename, "w", encoding="utf8") as file:
        for item in contents:
            file.write(str(item))
            file.write("\n")

def download_file(url, destination):
    req = requests.get(url)
    file = open(destination, "wb")
    for chunk in req.iter_content(100000):
        file.write(chunk)
    file.close()

def extract_emote_id(arg):
    match = _EMOTE_ID_MATCH.match(arg)
    if match:
        return str(match.group(2))

def make_message_embed(author, color, message, *, formatUser=False, useNick=False):
    if formatUser:
        name = str(author)
    else:
        if useNick and author.nick:
            name = author.nick
        else:
            name = author.name
    if author.avatar_url:
        avatar = author.avatar_url
    else:
        avatar = author.default_avatar_url
    embed = discord.Embed(color=color, description=message)
    embed.set_author(name=name, icon_url=avatar)
    return embed

def remove_html(arg):
    arg = arg.replace("&quot;", "\"").replace("<br />", "").replace("[i]", "*").replace("[/i]", "*")
    arg = arg.replace("&ldquo;", "\"").replace("&rdquo;", "\"").replace("&#039;", "'")
    return arg
