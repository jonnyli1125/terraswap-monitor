from terra_sdk.client.lcd import AsyncLCDClient


class TerraswapMonitor:
    def __init__(self, config):
        self.terra = AsyncLCDClient(url=config["mainnet_url"])
        self.pair_addresses = config["pairs"]
        self._simulation_input_amt = 1000000

    async def get_luna_to_bluna_rate(self):
        '''Return swap rate of Luna to bLUNA transaction in units of bLUNA per Luna.'''
        data = {
            "simulation": {
                "offer_asset": {
                    "info": {"native_token": {"denom": "uluna"}},
                    "amount": str(self._simulation_input_amt)
                }
            }
        }
        res = await self.terra.wasm.contract_query(self.pair_addresses["bluna_luna"], data)
        bluna_amt = res['return_amount']
        return int(bluna_amt) / self._simulation_input_amt

    async def get_bluna_to_luna_rate(self):
        '''Return swap rate of bLUNA to Luna transaction in units of bLUNA per Luna.'''
        data = {
            "reverse_simulation": {
                "ask_asset": {
                    "info": {"native_token": {"denom": "uluna"}},
                    "amount": str(self._simulation_input_amt)
                }
            }
        }
        res = await self.terra.wasm.contract_query(self.pair_addresses["bluna_luna"], data)
        bluna_amt = res['offer_amount']
        return int(bluna_amt) / self._simulation_input_amt
