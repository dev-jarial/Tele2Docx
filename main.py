import telebot
from google.auth import exceptions
from google.oauth2 import service_account
from googleapiclient.discovery import build


# Set up Telegram bot
bot_token = '6273935761:AAFU7eODH20Bji_DL0MNwHnlwo47t_0Pxyk'
bot = telebot.TeleBot(bot_token)

# Set up Google Docs
credentials_file = 'credentials.json'
credentials = service_account.Credentials.from_service_account_file(
    credentials_file, scopes=['https://www.googleapis.com/auth/documents']
)
service = build('docs', 'v1', credentials=credentials)

# Define the Google Docs document ID
document_id = '1f2vVKmunMORGjqyGV_QsIBlh7G2oipMOwRa5Gy7_kVU'

# Define a list of available commands
available_commands = [
    '/deposit - Capture user data and save it to Google Docs',
    '/list - Show the list of available commands',
]

# Handle /deposit command
@bot.message_handler(commands=['deposit'])
def deposit_command(message):
    # Prompt the user for their full name
    bot.reply_to(message, 'Please enter your full name:')

    # Store the user ID to match the response later
    user_id = message.from_user.id

    # Set a flag to indicate that we are waiting for the full name
    bot.register_next_step_handler(message, process_full_name, user_id)

# Process full name received after /deposit command
def process_full_name(message, user_id):
    # Retrieve the full name from the user's response
    full_name = message.text

    # Prompt the user for their message
    bot.reply_to(message, 'Please enter your message:')

    # Store the full name and user ID to match the response later
    user_data = {'full_name': full_name, 'user_id': user_id}

    # Set a flag to indicate that we are waiting for the message
    bot.register_next_step_handler(message, process_message, user_data)

# Process message received after full name
def process_message(message, user_data):
    # Retrieve the message from the user's response
    message_text = message.text

    # Get user information
    username = message.from_user.username

    # Retrieve stored data
    full_name = user_data['full_name']
    user_id = user_data['user_id']

    # Create the document content
    content = [
        {'insertText': {'text': f'User ID: {user_id}\n', 'location': {'index': 1}}},
        {'insertText': {'text': f'Username: {username}\n', 'location': {'index': 2}}},
        {'insertText': {'text': f'Full Name: {full_name}\n', 'location': {'index': 3}}},
        {'insertText': {'text': f'Message: {message_text}\n', 'location': {'index': 4}}},
        {'insertText': {'text': f'-------------------------------------------------------------------------------------------------------------------------------\n', 'location': {'index': 4}}}
    ]

    # Append the content to the document
    try:
        service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': [{'insertText': {'text': '\n', 'location': {'index': 1}}}]},
        ).execute()
        service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': [{'insertText': {'text': '\n'.join([item['insertText']['text'] for item in content]), 'location': {'index': 1}}}]},
        ).execute()
        bot.reply_to(message, 'Your Message sent successfully!')
    except exceptions.GoogleAuthError:
        bot.reply_to(message, 'Authentication error. Please check the credentials.')

# Handle /list command
@bot.message_handler(commands=['list'])
def list_commands(message):
    command_list = "\n".join(available_commands)
    bot.reply_to(message, f"Available commands:\n{command_list}")

# Start the bot
bot.polling()
