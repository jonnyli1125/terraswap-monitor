from terra_sdk.client.lcd import AsyncLCDClient


class TerraswapMonitor:
    def __init__(self, config):
        self.terra = AsyncLCDClient(url=config["mainnet_url"])
        self.pair_addresses = config["pairs"]
        self._simulation_input_amt = 1000000

    async def get_swap_rate(self, pair, reverse=False, input_denom="uluna"):
        '''Return swap rate of input_denom to other token in pair, in units of other token per input_denom.'''
        data = {
            ("reverse_simulation" if reverse else "simulation"): {
                ("ask_asset" if reverse else "offer_asset"): {
                    "info": {"native_token": {"denom": input_denom}},
                    "amount": str(self._simulation_input_amt)
                }
            }
        }
        pair_addr = self.pair_addresses[pair]
        res = await self.terra.wasm.contract_query(pair_addr, data)
        other_amt = res['offer_amount' if reverse else 'return_amount']
        return int(other_amt) / self._simulation_input_amt

    async def get_luna_to_bluna_rate(self):
        '''Return swap rate of Luna to bLUNA transaction in units of bLUNA per Luna.'''
        return await self.get_swap_rate("bluna_luna")

    async def get_bluna_to_luna_rate(self):
        '''Return swap rate of bLUNA to Luna transaction in units of bLUNA per Luna.'''
        return await self.get_swap_rate("bluna_luna", reverse=True)

    async def get_luna_to_ust_rate(self):
        '''Return swap rate of Luna to UST transaction in units of UST per Luna'''
        return await self.get_swap_rate("ust_luna")
