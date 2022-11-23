
A Basic Cog could start with the following. Just replace the XXXXXX and start creating commands or listeners

```python

import interactions
from interactions.ext.enhanced import extension_component

import models.datastorage as datastorage
import config

from utils.logger import get_logger,log_file_name
logger = get_logger()

def setup(bot):
    XXXXXX(bot)

class XXXXXX(interactions.Extension):
    def __init__(self,bot:interactions.Client):
        self.bot=bot
        logger.debug('Cog initialized')

    @interactions.extension_command(name="dummy",description="Explain it",guild_ids=config.guild_ids)
    async def dummy_command(self,ctx:interactions.CommandContext):
        await ctx.send('Hello World')
```