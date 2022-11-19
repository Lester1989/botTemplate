# First Steps
+ optional, make a virtualenv and activate it

+ install the requirements with `pip install -r requirements.txt`

+ get your token from [Discord Developer Portal](https://discord.com/developers/applications/)
+ create secret.py file with the following content:
`
token = 'your_token_bot_token_here'
`

+ start the bot with:
`
python main.py
`

+ open the browser and go to [localhost at port 32512](http://localhost:32512)

You are **ready** to go!

# Existing Files

## main.py

This is the main file, it starts the bot and the webserver.

New Cogs and new Webroutes **need to be registered** here.

## config.py

This file contains the configuration for the bot which is not to be stored in the database. 

## cogs

This folder contains all the cogs for the bot.

## cogs/help.py

This cog contains the help command.

## cogs/example.py

This cog contains an examples for the different interactions.

*This cog is for development only and should not be loaded in the finished Bot*

## models

This folder contains all the models for the database.

## models/datastorage.py

this file imports all the models and creates the database.

## models/base.py

This file contains the base class for all models and the database connection.

## models/example.py

This model contains an example for the database.

*This model is for development only and should not be imported in the finished Bot*

## utils

This folder contains files that are used by multiple cogs and/or routes.

## utils/commands.py

This file provides a function to gather all commands from all cogs loaded in the bot.
it also contains the class for convienient command display.

## utils/logger.py

This file contains the logger class.

## webserver

This folder contains all the files for the webserver.

## webserver/util.py

this file contains the routes for the logs page and the commands page.

## webserver/example.py

This file contains an example for a webroute.

## templates

This folder contains all the templates for the webserver.

The templates are rendered with [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/).

## templates/index.html

This is the template for the index page. other routes can be linked here for convenience.

## templates/logs.html

This is the template for the logs page.

## templates/commands.html

This is the template for the commands page.

## templates/example.html

This is the template for the example page.

# New Cog

## New Command

## New Eventlistener

## Buttons

## Modals (aka. Popups with Textinput-fields)

# New Webpage

## Link it in the index page

# Store Data

## Get Data

## Set Data

## Delete Data

## Update Data