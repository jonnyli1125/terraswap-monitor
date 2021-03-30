#!/usr/bin/env python3
import json
from bot import TerraswapMonitorBot


if __name__ == '__main__':
    config = {}
    with open('config.json', 'r') as fp:
        config = json.load(fp)
    bot = TerraswapMonitorBot(config)
    try:
        bot.run()
    except KeyboardInterrupt:
        print('Exiting...')
