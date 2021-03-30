import asyncio
import discord
from terraswap import TerraswapMonitor


class TerraswapMonitorBot(discord.Client):
    def __init__(self, config):
        self.config = config['discord']
        self.ts = TerraswapMonitor(config['terraswap'])
        self.rates = {}
        for pair in self.config['pairs']:
            self.rates[pair] = [float('inf'), float('inf')]
        self.thresholds = self.config['thresholds']
        self.interval = self.config['interval']
        self.log_channel = None
        self.ping_list = self.config['ping_list']
        super().__init__()

    def run(self):
        super().run(self.config['login_token'])

    async def on_ready(self):
        print('Logged on as', self.user)
        self.log_channel = self.get_channel(int(self.config['log_channel']))
        print('Starting monitor loop...')
        await self.monitor()

    async def monitor(self):
        while True:
            luna_to_bluna = await self.ts.get_luna_to_bluna_rate()
            bluna_to_luna = await self.ts.get_bluna_to_luna_rate()
            rates = self.rates['bluna_luna']
            threshold = self.thresholds['bluna_luna']
            msg = (
				"```" +
				"Luna to bLUNA - {} bLUNA per Luna\n" +
				"bLUNA to Luna - {} bLUNA per Luna" +
				"```").format(luna_to_bluna, bluna_to_luna)
            if (luna_to_bluna > threshold[0] and rates[0] < threshold[0]) or (bluna_to_luna > threshold[1] and rates[1] < threshold[1]):
                for uid in self.ping_list:
                    msg += "<@{}> ".format(uid)
            self.rates['bluna_luna'] = [luna_to_bluna, bluna_to_luna]
            await self.log_channel.send(msg)
            await asyncio.sleep(self.interval)
