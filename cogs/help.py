import interactions
import config
from utils.commands import gather_all_commands
from utils.logger import get_logger,log_file_name
logger = get_logger()

NEWLINE = '\n'
def setup(bot):
    HelpCog(bot)

class HelpCog(interactions.Extension):
    def __init__(self,bot:interactions.Client):
        self.bot=bot
        logger.debug('Cog initialized')

    @interactions.extension_command(name="help",description="Lists all Commands of the bot",guild_ids=config.guild_ids)
    async def help(self,ctx:interactions.CommandContext):
        commands = gather_all_commands(self.bot)
        embeds = []
        for extension, commands in commands.items():
            embed = interactions.Embed(title=f"Commands for {extension}")
            for command in commands:
                if command.options:
                    options_text = NEWLINE+NEWLINE.join(f'**{option_name}** *({descr_type[1]})*: {descr_type[0]}' for option_name,descr_type in command.options.items())
                else:
                    options_text = ''
                embed.add_field(name=command.name, value=f"{command.description}{options_text}", inline=False)
            embeds.append(embed)
            if len(embeds) == 5:
                await ctx.send(embeds=embeds)
                embeds = []
        if embeds:
            await ctx.send(embeds=embeds)

    @interactions.extension_command(name="logs",description="Shows the Logs of the current day",guild_ids=config.guild_ids,options=[
        interactions.Option(name="level",description="Sets LogLevel for Output (default: DEBUG)",type=interactions.OptionType.STRING,required=False,
            choices=[
                interactions.Choice(name="DEBUG",value="debug"),
                interactions.Choice(name="INFO",value="info"),
                interactions.Choice(name="WARNING",value="warning"),
                interactions.Choice(name="ERROR",value="error"),
                interactions.Choice(name="CRITICAL",value="critical")
    ])
    ])
    async def logs(self,ctx:interactions.CommandContext,level:str="debug"):
        if level.lower() not in ["debug","info","warning","error","critical"]:
            await ctx.send("Invalid LogLevel")
            return
        logger.handlers[0].flush()
        with open(log_file_name, 'r') as f:
            logs = f.readlines()
        showing_level = ["debug","info","warning","error","critical"]
        showing_level = showing_level[showing_level.index(level.lower()):]
        filtered_logs = [line for line in logs if line.split('-')[3].strip().lower() in showing_level]
        result = ""
        for line in filtered_logs:
            result += line+"\n"
            if len(result) > 4000:
                await ctx.send(result)
                result = ""
        if result:
            await ctx.send(result)
