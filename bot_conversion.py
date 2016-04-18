import discord
import asyncio
import aiohttp

OWNER_EMAIL = 'robinson.leal7@gmail.com'
OWNER_PASSWORD = 'robingl24!!'

BOT_EMAIL = 'robinson.gl@hotmail.com'
BOT_PASSWORD = 'robingl24!'

APPLICATIONS = 'https://discordapp.com/api/oauth2/applications'

class AutoCloseClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0.user}'.format(self))
        await self.logout()

owner = discord.Client()
bot = AutoCloseClient()

async def create_application():
    global owner

    headers = {
        'authorization': owner.token,
        'content-type': 'application/json'
    }

    payload = {
        'name': bot.user.name
    }

    print('Creating application')
    async with aiohttp.post(APPLICATIONS, headers=headers, data=discord.utils.to_json(payload)) as resp:
        data = await resp.json()
        owner.client_id = data['id']
        print('Successfully created an application! ')
        print('Client ID: {0[id]}\nSecret: {0[secret]}'.format(data))

async def do_conversion():
    global owner
    global bot
    url = '{0}/{1.client_id}/bot'.format(APPLICATIONS, owner)
    headers = {
        'authorization': owner.token,
        'content-type': 'application/json'
    }

    payload = {
        'token': bot.token
    }

    print('Converting account into a bot account.')
    async with aiohttp.post(url, headers=headers, data=discord.utils.to_json(payload)) as resp:
        data = await resp.json()
        print('Bot conversion complete.')
        print(data)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(owner.login(OWNER_EMAIL, OWNER_PASSWORD))
    loop.run_until_complete(owner.session.close())
    loop.run_until_complete(bot.start(BOT_EMAIL, BOT_PASSWORD))
except Exception as e:
    print('oops, something happened: ' + str(e))
else:
    loop.run_until_complete(create_application())
    loop.run_until_complete(do_conversion())
finally:
    loop.close()
