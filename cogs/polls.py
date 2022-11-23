
import interactions
from interactions.ext.enhanced import extension_component
import models.datastorage as datastorage

import config

from utils.logger import get_logger,log_file_name
logger = get_logger()
NEWLINE = '\n'

def setup(bot):
    Polls(bot)

class Polls(interactions.Extension):
    def __init__(self,bot:interactions.Client):
        self.bot=bot
        logger.debug('Cog initialized')

    def render_poll_overview(self,guild_id:int,creator_id:int,name:str)->list[interactions.Embed]:
        # Get Poll from DB
        poll = datastorage.Poll.get(guild_id,creator_id,name)
        # Get Question from DB
        questions = datastorage.PollQuestion.get_all_for_poll(guild_id,creator_id,name)
        # Get Participants from DB
        participants = datastorage.PollParticipant.get_all_for_poll(guild_id,creator_id,name)
        # Get Answers from DB
        answers = datastorage.PollAnswer.get_all_for_poll(guild_id,creator_id,name)
        # Render Poll
        result:list[interactions.Embed] = []
        embed = interactions.Embed(title=name,description=str(poll.description))
        statistics = f'''
        questions: {len(questions)}
        participants: {len(participants)}
        '''
        embed.add_field(name="Statistics",value=statistics,inline=False)
        for question in questions:
            options = question.options_dict
            question_answers = [answer for answer in answers if answer.question_nr == question.question_nr]
            question_stats = f'''
            options: {len(options)}
            answers: {len([question_answers])}
            '''
            if question_answers:
                answers_stats = '\n'.join(f'{option_text}: {len([answer for answer in question_answers if answer.answer == option_name])}' for option_name, option_text in options.items())
                question_stats += f'Current Answers:\n{answers_stats}'

            embed.add_field(name=f'{question.question_nr}: {question.question_text}',value=question_stats,inline=True)
            if len(embed.fields or []) > 9:
                result.append(embed)
                embed.set_footer(text=f'Page {len(result)}')
                embed = interactions.Embed(title=name)
        if embed.fields:
            result.append(embed)
            embed.set_footer(text=f'Page {len(result)}')
        return result

    def ascii_percentage_bar(self,percentage:float,width:int=20)->str:
        bar = '█' * int(percentage * width)
        bar += '░' * (width - len(bar))
        return bar

    def render_poll_interaction(self,guild_id:int,creator_id:int,name:str,question_nr:int) -> dict:
        if question_nr == -1:
            return {
                'content': 'Thank you for participating in this poll!',
                'embeds': None,
                'components': None
            }

        # Get all Question of the Poll from DB
        questions = datastorage.PollQuestion.get_all_for_poll(guild_id,creator_id,name)
        # Get Current Question from DB
        question = datastorage.PollQuestion.get(guild_id,creator_id,name,question_nr)
        if not question:
            question_nr = datastorage.PollQuestion.get_next_question_nr(guild_id,creator_id,name,question_nr)
            if question_nr == -1:
                return {
                    'content': 'Thank you for participating in this poll!',
                    'embeds': None,
                    'components': None
                }
            question = datastorage.PollQuestion.get(guild_id,creator_id,name,question_nr)

        old_questions = [q for q in questions if q.question_nr < question_nr]
        percentage_done = len(old_questions) / len(questions)
        embed = interactions.Embed(
            title=f'{name} - Question {question_nr}',
            description=str(question.question_text),
            footer=interactions.EmbedFooter(text=f'{self.ascii_percentage_bar(percentage_done)} {percentage_done:.0%} done'),
        )
        # Render Question
        options = question.options_dict
        buttons = [
            interactions.Button(
                label=option_text,
                style=interactions.ButtonStyle.PRIMARY,
                custom_id=f'poll_answer_{creator_id}_{name}_{question_nr}_{option_name}'
            )
            for option_name, option_text in options.items()]
        return {
            'embeds':embed,
            'components':interactions.spread_to_rows(*buttons)
        }

    @extension_component('poll_answer_',startswith=True)
    async def poll_answer(self,ctx:interactions.ComponentContext):
        creator_id,name,question_nr,option_name = str(ctx.custom_id).split('_')[2:]
        creator_id = int(creator_id)
        question_nr = int(question_nr)
        datastorage.PollAnswer.create(int(ctx.guild_id),creator_id,name,question_nr,int(ctx.author.id),option_name)
        next_question_nr = datastorage.PollQuestion.get_next_question_nr(int(ctx.guild_id),creator_id,name,question_nr)
        message_dict = self.render_poll_interaction(int(ctx.guild_id),creator_id,name,next_question_nr)
        if message_dict['components'] is None:
            datastorage.PollParticipant.create(int(ctx.guild_id),creator_id,name,int(ctx.author.id))
            logger.debug(f'Poll of {creator_id} with {name} completed by {ctx.author.id}')
        await ctx.edit(**message_dict)

    @interactions.extension_command(name="polls",description="Mangage User Polls",guild_ids=config.guild_ids)
    async def polls_base_command(self,ctx:interactions.CommandContext):
        pass

    @polls_base_command.subcommand(name="create",description="Create a new Poll",
        options=[
            interactions.Option(name="name",description="name of the poll",type=interactions.OptionType.STRING,required=True),
            interactions.Option(name="description",description="description of the poll",type=interactions.OptionType.STRING,required=True),
            interactions.Option(name="anonymous",description="is the poll anonymous",type=interactions.OptionType.BOOLEAN,required=True),
        ])
    async def polls_create_command(self,ctx:interactions.CommandContext,name:str,description:str,anonymous:bool):
        logger.debug('polls_create_command')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return
        datastorage.Poll.create(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name,description=description,anonymous=anonymous)
        rendered_polls = self.render_poll_overview(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        for embed in rendered_polls:
            await ctx.send(embed=embed,ephemeral=True)

    @polls_base_command.subcommand(name="list",description="Lists all Polls created by you")
    async def polls_list_command(self,ctx:interactions.CommandContext):
        logger.debug('polls_list_command')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return
        polls = datastorage.Poll.get_for_creator(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id))
        open_polls = [poll for poll in polls if not poll.closed]
        if not open_polls:
            await ctx.send("You have no open polls yet",ephemeral=True)
            return
        embed = interactions.Embed(title="Your open Polls")
        for poll in open_polls:
            embed.add_field(name=str(poll.name),value=str(poll.description),inline=False)
        await ctx.send(embed=embed,ephemeral=True)

    @polls_base_command.subcommand(name="close",description="Closes a Poll",
        options=[
            interactions.Option(name="name",description="name of the poll",type=interactions.OptionType.STRING,required=True),
        ])
    async def polls_close_command(self,ctx:interactions.CommandContext,name:str):
        logger.debug('polls_close_command')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return
        datastorage.Poll.update(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name,closed=True)
        await ctx.send(f"Poll {name} closed",ephemeral=True)

    @polls_base_command.subcommand(name="delete",description="Deletes a Poll",
        options=[
            interactions.Option(name="name",description="name of the poll",type=interactions.OptionType.STRING,required=True),
        ])
    async def polls_delete_command(self,ctx:interactions.CommandContext,name:str):
        logger.debug('polls_delete_command')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return
        datastorage.Poll.delete(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        await ctx.send(f"Poll {name} deleted",ephemeral=True)

    @polls_base_command.subcommand(name="show",description="Shows a Poll",
        options=[
            interactions.Option(name="name",description="name of the poll",type=interactions.OptionType.STRING,required=True),
        ])
    async def polls_show_command(self,ctx:interactions.CommandContext,name:str):
        logger.debug('polls_show_command')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return
        poll = datastorage.Poll.get(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        questions = datastorage.PollQuestion.get_all_for_poll(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        embed = interactions.Embed(
            title=f"Poll {name}",
            description=str(poll.description),
            fields=[
                interactions.EmbedField(name="Questions",value=f"There are {len(questions)} in the poll",inline=False)
                ],
            footer=interactions.EmbedFooter(text="Please click the start button to participate"))
        await ctx.send(embed=embed,components=[interactions.Button(label="Start",custom_id=f"poll_start_{ctx.author.id}_{name}",style=interactions.ButtonStyle.SUCCESS)])

    @extension_component('poll_start_',startswith=True)
    async def poll_start_component(self,ctx:interactions.ComponentContext):
        logger.debug('poll_start_component')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return

        creator_id,name = str(ctx.custom_id).split('_')[2:]
        poll = datastorage.Poll.get(guild_id=int(ctx.guild_id),creator_id=int(creator_id),name=name)
        if poll.closed:
            await ctx.send("This poll is closed",ephemeral=True)
            return
        existing_answers = datastorage.PollAnswer.get_all_for_poll(guild_id=int(ctx.guild_id),creator_id=int(creator_id),name=name)
        if existing_answers and any(answer.user_id == int(ctx.author.id) for answer in existing_answers):
            await ctx.send(
                "You already answered this poll",
                components=interactions.spread_to_rows(
                    interactions.Button(label='Restart',custom_id=f"poll_restart_{creator_id}_{name}",style=interactions.ButtonStyle.DANGER),
                ),
                ephemeral=True)
            return
        await ctx.send(**self.render_poll_interaction(int(ctx.guild_id),int(creator_id),name,0),ephemeral=True)

    @extension_component('poll_restart_',startswith=True)
    async def poll_restart_component(self,ctx:interactions.ComponentContext):
        logger.debug('poll_restart_component')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return
        creator_id,name = str(ctx.custom_id).split('_')[2:]
        datastorage.PollAnswer.delete_all_of_user_for_poll(guild_id=int(ctx.guild_id),creator_id=int(creator_id),name=name,user_id=int(ctx.author.id))
        await ctx.edit(**self.render_poll_interaction(int(ctx.guild_id),int(creator_id),name,0),ephemeral=True)

    def make_bar_plot(self,question:datastorage.PollQuestion, answers:list[datastorage.PollAnswer],width=20):
        relevant_answers = [answer for answer in answers if answer.question_nr == question.question_nr]
        grouped_answers = {
            option_text: len([answer for answer in relevant_answers if answer.answer == option_name])
            for option_name, option_text in question.options_dict.items()
        }
        max_value = max(grouped_answers.values())
        bars = [
            (f"{option_text} {round(value/max_value*width)*'█'} {value}",value)
            for option_text, value in grouped_answers.items()
        ]
        return [bar for bar,_ in sorted(bars,key=lambda x: x[1],reverse=True)]

    @polls_base_command.subcommand(name="results",description="Shows the results of a Poll",
        options=[
            interactions.Option(name="name",description="name of the poll",type=interactions.OptionType.STRING,required=True),
        ])
    async def polls_results_command(self,ctx:interactions.CommandContext,name:str):
        logger.debug('polls_results_command')
        if not ctx.guild:
            await ctx.send("This command is only available in a guild")
            return
        poll = datastorage.Poll.get(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        questions = datastorage.PollQuestion.get_all_for_poll(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        answers = datastorage.PollAnswer.get_all_for_poll(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        participants = datastorage.PollParticipant.get_all_for_poll(guild_id=int(ctx.guild_id),creator_id=int(ctx.author.id),name=name)
        # check if all questions have been answered
        participant_ids = {participant.user_id for participant in participants}
        all_answer_count = len(answers)
        answers = [answer for answer in answers if answer.user_id in participant_ids]
        if len(answers) != all_answer_count:
            logger.debug(f"Answers: {len(answers)} != {all_answer_count} some users did not answer all questions")
        embed = interactions.Embed(
            title=f"Resuls: {name}",
            description=f"Showing the results of the poll with {len(participants)} participants and {len(questions)} questions. {NEWLINE}*only showing answers of participants who completed the poll*",
        )
        page_count = 1
        detail_button = interactions.Button(label="Details",url='COMING SOON',disabled=True,style=interactions.ButtonStyle.LINK)
        for question in questions:
            question_detail = f'''**{question.question_text}**
            {NEWLINE.join(self.make_bar_plot(question,answers))}
            '''
            embed.add_field(name=f"Question {question.question_nr}",value=question_detail,inline=False)
            if len(embed.fields or []) >10:
                embed.set_footer(text=f'Page {page_count}')
                await ctx.send(
                    embeds=embed,
                    components=interactions.spread_to_rows(detail_button) if page_count == 1 else None,
                )
                page_count += 1
                embed = interactions.Embed(
            title=f"Resuls: {name}",
            description=f"Showing the results of the poll with {len(participants)} participants and {len(questions)} questions",
            )
        if embed.fields:
            embed.set_footer(text=f'Page {page_count}')
            await ctx.send(
                embeds=embed,
                components=interactions.spread_to_rows(detail_button) if page_count == 1 else None)