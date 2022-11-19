import utils.logger as custom_logging
import logging
custom_logging.init_logger(logger = 'DiscordBot', log_file = 'DiscordBot.log', log_level=logging.DEBUG)
logger = logging.getLogger('DiscordBot')

from datetime import datetime, timezone
from fastapi import Request
import os


import secret
import interactions
from interactions.ext.fastapi import setup
import models.datastorage
import config
from fastapi.responses import HTMLResponse,RedirectResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import webserver.util as webserver_util
import webserver.example as webserver_example



intents = interactions.Intents.GUILD_MEMBERS | interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT

client = interactions.Client(
    token=secret.token,
    intents=intents,
    presence=interactions.ClientPresence(
        status=interactions.StatusType.ONLINE,
        activities=[
            interactions.PresenceActivity(name="Lester Discord Bot", type=interactions.PresenceActivityType.GAME)
        ]
    )
)

api = setup(client,host='0.0.0.0')

client.load("interactions.ext.enhanced")
client.load('interactions.ext.files')
for extension in os.listdir('cogs'):
    if extension.endswith('.py'):
        client.load(f'cogs.{extension[:-3]}')

webserver_util.client = client
webserver_example.client = client
logger.info('cogs loaded')

@client.event
async def on_ready():
    logger.debug('ready')




api._api.app.mount("/static", StaticFiles(directory="static"), name="static")
api._api.app.include_router(webserver_util.router)
api._api.app.include_router(webserver_example.router)


client.start()
