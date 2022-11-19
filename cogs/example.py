import interactions
import config
from interactions.ext.enhanced import extension_component
import models.datastorage as datastorage

def setup(bot):
    ExampleCog(bot)

class ExampleCog(interactions.Extension):
    def __init__(self,bot:interactions.Client):
        self.bot=bot

    @interactions.extension_command(name="example",description="Example command",guild_ids=config.guild_ids)
    async def example(self,ctx:interactions.CommandContext):
        await ctx.send("Example")

    @interactions.extension_command(name="ex",guild_ids=config.guild_ids)
    async def base_command(self,ctx:interactions.CommandContext):
        pass
  
    @base_command.subcommand(name="sub1",description="Example sub command",options=[
        interactions.Option(name="option",description="Example option",type=interactions.OptionType.STRING,required=True)
    ])
    async def sub1_command(self,ctx:interactions.CommandContext,option:str):
        await ctx.send(f"Subcommand 1 got {option}")

    @base_command.subcommand(name="sub2",description="Example sub command",options=[
        interactions.Option(name="option",description="Example option",type=interactions.OptionType.STRING,required=False)
    ])
    async def sub2_command(self,ctx:interactions.CommandContext,option:str="default"):
        await ctx.send(f"Subcommand 2 got {option}")

    @interactions.extension_command(name="cool",guild_ids=config.guild_ids)
    async def cool_base_command(self,ctx:interactions.CommandContext):
        pass

    @cool_base_command.subcommand(name="embed",description="Example sub command")
    async def cool_sub1_command(self,ctx:interactions.CommandContext):
        await ctx.send(
            embeds=interactions.Embed(
                title="Example Embed",
                description="This is an example embed",
                color=0x00ff00,
                fields=[
                    interactions.EmbedField(name="Field 1",value="This is a field",inline=False),
                    interactions.EmbedField(name="Field 2",value="This is another field",inline=False)
                ],
                footer=interactions.EmbedFooter(text="This is a footer",icon_url="https://cdn.discordapp.com/embed/avatars/0.png"),
                image=interactions.EmbedImageStruct(url="https://cdn.discordapp.com/embed/avatars/1.png"),
                author=interactions.EmbedAuthor(name='Bot',url="https://cdn.discordapp.com/embed/avatars/2.png"),
        ))

    @cool_base_command.subcommand(name="buttons",description="Example sub command")
    async def cool_sub2_command(self,ctx:interactions.CommandContext):
        await ctx.send(
            content="Example buttons",
            components=[
                interactions.ActionRow(components=[
                    interactions.Button(label="Button 1",custom_id='id_button_1',style=interactions.ButtonStyle.PRIMARY),
                    interactions.Button(label="Button 2",custom_id='id_button_2',style=interactions.ButtonStyle.SECONDARY),
                    interactions.Button(label="Button 3",custom_id='id_button_3',style=interactions.ButtonStyle.SUCCESS),
                    interactions.Button(label="Button 4",custom_id='other',style=interactions.ButtonStyle.DANGER),
                    interactions.Button(label="Button 5",style=interactions.ButtonStyle.LINK,url="https://www.google.com")
                    ]) # type: ignore
            ]
        )

    @extension_component("id_button_",startswith=True)
    async def button_handler(self,ctx:interactions.ComponentContext):
        number = str(ctx.custom_id).split("_")[-1]
        await ctx.send(f"Button {number} was pressed")

    @extension_component("other")
    async def other_button_handler(self,ctx:interactions.ComponentContext):
        await ctx.send("Dangerous button was pressed")

    @cool_base_command.subcommand(name="select",description="Example select")
    async def select_command(self,ctx:interactions.CommandContext):
        await ctx.send(
            content="Example select",
            components=[
                interactions.ActionRow(components=[
                    interactions.SelectMenu(
                        custom_id="select_example",
                        min_values=1,
                        max_values=3,
                        options=[
                            interactions.SelectOption(label="Option 1",value="1"),
                            interactions.SelectOption(label="Option 2",value="2"),
                            interactions.SelectOption(label="Option 3",value="3")
                        ]
                    )  # type: ignore
                ])
            ]
        )    

    @extension_component("select_example")
    async def select_handler(self,ctx:interactions.ComponentContext,data:list[str]):
        await ctx.send(f"Selected {data}")
        
    @cool_base_command.subcommand(name="select_channel",description="Example select")
    async def select_channel_command(self,ctx:interactions.CommandContext):
        await ctx.send(
            content="Example select",
            components=[
                interactions.ActionRow(components=[
                    interactions.Component(
                        type=interactions.ComponentType.CHANNEL_SELECT,
                        custom_id="select_channel_example",
                        min_values=1,
                        max_values=25,# 25 is max
                    )  # type: ignore
                ])
            ]
        )

    @extension_component("select_channel_example")
    async def select_channel_handler(self,ctx:interactions.ComponentContext,data:list[interactions.Channel]):
        await ctx.send(f"Selected {data}")

    @cool_base_command.subcommand(name='modal',description="Example modal")
    async def modal_command(self,ctx:interactions.CommandContext):
        await ctx.popup(
            interactions.Modal(
                title="Example Modal",
                custom_id="modal_example",
                components=[
                    interactions.TextInput(
                        custom_id="text_input_1",
                        style=interactions.TextStyleType.SHORT,
                        placeholder="no value",
                        min_length=1,
                        max_length=100,
                        label="Example text input",
                        value="default value",
                        required=True
                    )  # type: ignore
                ]
            )
        )

    @interactions.extension_modal("modal_example")
    async def modal_handler(self,ctx:interactions.ComponentContext,text_input_1:str):
        await ctx.send(f"Text input value: {text_input_1}")

    @interactions.extension_command(name='database',guild_ids=config.guild_ids)
    async def database_command(self,ctx:interactions.CommandContext):
        pass

    @database_command.subcommand(name='add',description="Add a value to the database",options=[
        interactions.Option(name="key",description="Key to add",type=interactions.OptionType.STRING,required=True),
        interactions.Option(name="value",description="Value to add",type=interactions.OptionType.INTEGER,required=True)
    ])
    async def database_add_command(self,ctx:interactions.CommandContext,key:str,value:int):
        if not ctx.guild:
            await ctx.send("This command can only be used in a guild")
            return

        datastorage.ExampleData.create(int(ctx.guild.id),key,value)
        await ctx.send(f"Added {key}{value} to the database")

    @database_command.subcommand(name='liste',description="Gets all entries from the database")
    async def database_list_command(self,ctx:interactions.CommandContext):
        if not ctx.guild:
            await ctx.send("This command can only be used in a guild")
            return

        data = datastorage.ExampleData.get_all(int(ctx.guild.id))
        NEWLINE = "\n"
        await ctx.send(f"Database entries: {NEWLINE.join([f'{entry}' for entry in data])}")
    
    