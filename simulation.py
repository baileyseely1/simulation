from telethon import TelegramClient, events
import re
import json
from datetime import datetime

def run_scraping():
    api_id = '29750573'
    api_hash = 'd3db64927f4e22b040565eea461e775e'
    client = TelegramClient('Simulation', api_id, api_hash)
    client.start()

    # File to store the data
    filename = "channel_data.json"

    # Updated Regular Expressions
    contract_regex = re.compile(r"🏠 Address:\s+(\S+)")  # Extracts the address
    supply_regex = re.compile(r"├─ 💰 Total Supply:\s+([\d,]+)")  # Extracts the total supply
    token_name_regex = re.compile(r"├─ 🏷 Name: (.+)")
    token_symbol_regex = re.compile(r"├─ 💲 Symbol: (.+)")
    transactions_regex = re.compile(r"├─ 🖨 Transactions: (\d+)")  # Extracts the number of transactions
    balance_sol_regex = re.compile(r"├─ 💵 Balance SOL: ([\d.]+)")  # Extracts the balance in SOL
    owner_regex = re.compile(r"🔑 Owner:\s+([A-Za-z0-9]+)")  # Extracts the owner address

    def extract_urls_from_entities(message):
        # Segment the message to exclude undesired sections
        segmented_text = message.text.split("Open in Sniper Bots:")[0].split("📢 Ads:")[0]

        # Initialize default values as "Unknown"
        telegram = twitter = website = "Unknown"

        # Extract URLs from the segmented text
        urls = re.findall(r'https?://\S+', segmented_text)
        
        # Filter out undesired bot URLs
        bot_blacklist = ["BananaGunSniper_bot", "MaestroSniperBot", "MaestroProBot", "unibotsniper_bot", "OttoMethodIDs", 'https://t.me/solanascanner']
        urls = [url for url in urls if not any(bot in url for bot in bot_blacklist)]
        
        # Clean any URL that ends with a parenthesis
        urls = [url.rstrip(')') for url in urls]
        
        # Check for Telegram URL or handle partial URL
        telegram_match = re.search(r"Telegram:\s*(https?://t\.me/\S+|t\.me/\S+)", segmented_text)
        if telegram_match:
            telegram_url = telegram_match.group(1)
            # Add 'https://' if not present
            telegram_urls = [f"https://{telegram_url}" if not telegram_url.startswith('http') else telegram_url]
            if telegram in bot_blacklist:
                telegram = "Unknown"
        else:
            # Look in the extracted URLs for a Telegram link
            telegram_urls = [url for url in urls if "t.me" in url]

        # Initialize twitter and website URLs as "Unknown"
        twitter_urls = [url for url in urls if "twitter.com" in url]
        website_urls = [url for url in urls if url not in telegram_urls and url not in twitter_urls and not url.startswith("https://etherscan.io/token/") and "OttoMethodIDs" not in url]

        # Return the first URL of each type or "Unknown" if not available
        telegram = telegram_urls[0] if telegram_urls else "Unknown"
        twitter = twitter_urls[0] if twitter_urls else "Unknown"
        website = website_urls[0] if website_urls else "Unknown"
        
        return telegram, twitter, website   



    def get_or_unknown(regex, text, group=1):
        match = regex.search(text)
        return match.group(group) if match else "Unknown"

    @client.on(events.NewMessage(chats="SolanaScanner"))
    async def main(event):
        message_text = event.message.message

        # Extracting details using the regular expressions
        contract_address = get_or_unknown(contract_regex, message_text)
        total_supply = get_or_unknown(supply_regex, message_text)
        token_name = get_or_unknown(token_name_regex, message_text)
        token_symbol = get_or_unknown(token_symbol_regex, message_text)
        transactions = get_or_unknown(transactions_regex, message_text)
        balance_sol = get_or_unknown(balance_sol_regex, message_text)
        owner_address = get_or_unknown(owner_regex, message_text)  # Extract owner address
        telegram, twitter, website = extract_urls_from_entities(event.message)

        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Structuring the data
        data = {
            'timestamp': current_timestamp,
            'contract_address': contract_address,
            'total_supply': total_supply,
            'token_name': token_name,
            'token_symbol': token_symbol,
            'transactions': transactions,
            'balance_sol': balance_sol,
            'owner_address': owner_address,
            'socials': {
                'telegram': telegram,
                'twitter': twitter,
                'website': website
            }
        }

        # Print and save the extracted data
        print(json.dumps(data, indent=4))

        try:
            with open(filename, 'r') as file:
                data_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data_list = []

        data_list.append(data)

        with open(filename, 'w') as file:
            json.dump(data_list, file, indent=4)

    with client:
        client.run_until_disconnected()

run_scraping()