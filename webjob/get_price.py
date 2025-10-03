from web3 import Web3
import requests
import json


def get_bsc_token_price(token_address, bsc_rpc_url="https://bsc-dataseed.binance.org/"):
    """
    Retrieves the price of a given token on Binance Smart Chain in BUSD or WBNB with high precision.

    Args:
        token_address (str): The contract address of the token
        bsc_rpc_url (str): BSC RPC endpoint (default: Binance public node)

    Returns:
        tuple: (price, currency) where price is a float and currency is 'BUSD' or 'WBNB', or (None, None) if an error occurs
    """
    try:
        # Connect to BSC
        web3 = Web3(Web3.HTTPProvider(bsc_rpc_url))
        if not web3.is_connected():
            print("Failed to connect to BSC network")
            return None, None

        # PancakeSwap V2 Router contract address and ABI
        pancakeswap_router_address = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
        pancakeswap_router_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsOut",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

        # Standard ERC20 ABI to get decimals
        erc20_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

        # BUSD and WBNB contract addresses
        busd_address = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        wbnb_address = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

        # Get token decimals
        token_address = web3.to_checksum_address(token_address)
        token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)
        try:
            decimals = token_contract.functions.decimals().call()
        except:
            print("Failed to fetch token decimals, assuming 18")
            decimals = 18

        # Create PancakeSwap router contract instance
        router_contract = web3.eth.contract(
            address=web3.to_checksum_address(pancakeswap_router_address),
            abi=pancakeswap_router_abi
        )

        # Try BUSD pair first
        try:
            path = [token_address, busd_address]
            amount_in = 10 ** decimals  # 1 token, adjusted for decimals
            amounts = router_contract.functions.getAmountsOut(amount_in, path).call()
            price_in_busd = amounts[1] / 10 ** 18  # BUSD has 18 decimals
            return price_in_busd, "BUSD"
        except Exception as e:
            print(f"BUSD pair failed: {str(e)}")

        # Fallback to WBNB pair
        try:
            path = [token_address, wbnb_address]
            amount_in = 10 ** decimals
            amounts = router_contract.functions.getAmountsOut(amount_in, path).call()
            price_in_wbnb = amounts[1] / 10 ** 18  # WBNB has 18 decimals
            return price_in_wbnb, "WBNB"
        except Exception as e:
            print(f"WBNB pair failed: {str(e)}")

        # Fallback to PancakeSwap API
        try:
            api_url = f"https://api.pancakeswap.info/api/v2/tokens/{token_address}"
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = float(data['data']['price'])
                return price, "BUSD"
            else:
                print("PancakeSwap API request failed")
        except Exception as e:
            print(f"PancakeSwap API failed: {str(e)}")

        return None, None

    except Exception as e:
        print(f"Error fetching token price: {str(e)}")
        return None, None


# Example usage
if __name__ == "__main__":
    # Test with the provided token address
    token_address = "0xcb87860c26dad1fca0f938ccaa6406f3b5964444"
    price, currency = get_bsc_token_price(token_address)
    if price:
        print(f"Price of token: {price:.18f} {currency}")
    else:
        print("Failed to retrieve token price")