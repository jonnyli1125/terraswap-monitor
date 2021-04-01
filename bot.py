#!/usr/bin/env python3
import asyncio
import json
import discord.ext.commands
from terraswap import TerraswapMonitor

class TerraswapMonitorBot(discord.ext.commands.Bot):
    def __init__(self, config):
        self.config = config['discord']
        self.ts = TerraswapMonitor(config['terraswap'])
        self.rates = {}
        self.thresholds = self.config['thresholds']
        for pair in self.thresholds:
            self.rates[pair] = [(0, float('inf'))]
        self.interval = self.config['interval']
        self.log_channel = None
        self.ping_list = self.config['ping_list']
        super().__init__(command_prefix=self.config['command_prefix'])

    def run(self):
        super().run(self.config['login_token'])

    async def on_ready(self):
        print('Logged on as', self.user)
        self.log_channel = self.get_channel(int(self.config['log_channel']))
        print('Starting monitor loop...')
        await self.monitor()

    async def monitor(self):
        # TODO: use discord.ext.tasks eventually
        while True:
            luna_to_bluna = await self.ts.get_luna_to_bluna_rate()
            bluna_to_luna = await self.ts.get_bluna_to_luna_rate()
            luna_to_ust = await self.ts.get_luna_to_ust_rate()
            rates = self.rates['bluna_luna']
            threshold = self.thresholds['bluna_luna']
            msg = (
				"```" +
				"Luna to bLUNA - {} bLUNA per Luna\n" +
				"bLUNA to Luna - {} bLUNA per Luna\n" +
                "Luna to UST   - {} UST per Luna" +
				"```").format(luna_to_bluna, bluna_to_luna, luna_to_ust)
            # TODO: generalize this logic eventually
            if (luna_to_bluna >= threshold[0] and rates[0] < threshold[0]) or (bluna_to_luna <= threshold[1] and rates[1] > threshold[1]):
                for uid in self.ping_list:
                    msg += "<@{}> ".format(uid)
            self.rates['bluna_luna'] = [luna_to_bluna, bluna_to_luna]
            await self.log_channel.send(msg)
            await asyncio.sleep(self.interval)


config = {}
with open('config.json', 'r') as fp:
    config = json.load(fp)
bot = TerraswapMonitorBot(config)

@bot.command()
async def interval(ctx, val:int=None):
    if not val:
        await ctx.send("Current interval: {} seconds".format(bot.interval))
        return
    bot.interval = val
    await ctx.send("Updated interval to {} seconds.".format(val))

@bot.command()
async def threshold(ctx, forward_val:float=None, backward_val:float=None):
    pair = "bluna_luna" # temp
    if not forward_val or not backward_val:
        msg = "Current thresholds: {}\nUse `{}threshold <forward_val> <backward_val>` to set values.".format(bot.thresholds[pair], bot.command_prefix)
        await ctx.send(msg)
        return
    bot.thresholds[pair] = [forward_val, backward_val]
    bot.rates[pair] = [0, float('inf')]
    await ctx.send("Updated thresholds to {}.".format(bot.thresholds[pair]))

if __name__ == '__main__':
    try:
        bot.run()
    except KeyboardInterrupt:
        print('Exiting...')
