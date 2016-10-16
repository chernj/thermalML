__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

from time import sleep
import os
import json
import telegram

def send_message(access_token, user_id, msg_text):

# construct client and key word arguments
    message_kwargs = {
        'chat_id': user_id,
        'text': msg_text
    }
    client = telegram.Bot(token=access_token)

# send welcome message
    response = client.sendMessage(**message_kwargs)

    return response.to_dict()

def get_updates(access_token, last_update_path=''):

# construct client and key words
    update_kwargs = {}
    if last_update_path:
        file_details = json.loads(open(last_update_path).read())
        if 'last_update' in file_details.keys():
            update_kwargs['offset'] = file_details['last_update'] + 1
    client = telegram.Bot(token=access_token)

# send request
    response = client.getUpdates(**update_kwargs)

# construct update list
    update_list = []
    if response:
        for i in range(len(response)):
            update_list.append(response[i].to_dict())

    return update_list

def log_updates(last_update_path, updates_folder_path, update_list):

# iterate over update list
    if update_list:
        for i in range(len(update_list)):
            update_details = update_list[i]

# parse user id and time id from update details
            if 'message' in update_details.keys():
                user_id = ''
                time_id = ''
                msg_details = update_details['message']
                if 'from' in msg_details.keys():
                    if 'id' in msg_details['from'].keys():
                        user_id = str(msg_details['from']['id'])
                if 'date' in msg_details.keys():
                    time_id = str(msg_details['date'])

# create file path
                if user_id and time_id:
                    folder_path = os.path.abspath(updates_folder_path)
                    subfolder_path = os.path.join(folder_path, user_id)
                    if not os.path.exists(subfolder_path):
                        os.makedirs(subfolder_path)
                    file_path = os.path.join(subfolder_path, '%s.json' % time_id)

# save update data to local file
                    update_data = json.dumps(update_details).encode('utf-8')
                    with open(file_path, 'wb') as f:
                        f.write(update_data)
                        f.close()

# update last update id
            if i + 1 == len(update_list):
                update_dict = { 'last_update': update_details['update_id'] }
                update_data =  json.dumps(update_dict).encode('utf-8')
                with open(last_update_path, 'wb') as f:
                    f.write(update_data)
                    f.close()

    return True

def log_message(message_folder_path, message_details):

# parse user id and time id from message details
    user_id = ''
    time_id = ''
    if 'chat' in message_details.keys():
        if 'id' in message_details['chat'].keys():
            user_id = str(message_details['chat']['id'])
    if 'date' in message_details.keys():
        time_id = str(message_details['date'])

# create file path
    if user_id and time_id:
        folder_path = os.path.abspath(message_folder_path)
        subfolder_path = os.path.join(folder_path, user_id)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
        file_path = os.path.join(subfolder_path, '%s.json' % time_id)

# save update data to local file
        message_data = json.dumps(message_details).encode('utf-8')
        with open(file_path, 'wb') as f:
            f.write(message_data)
            f.close()

    return True

def create_user(table_path, user_details):

# open user table and append new users
    user_table = json.loads(open(table_path).read())
    for user in user_table:
        if user['telegram']['id'] == user_details['telegram']['id']:
            return False
    user_table.append(user_details)

# save table data to local file
    table_data = json.dumps(user_table).encode('utf-8')
    with open(table_path, 'wb') as f:
        f.write(table_data)
        f.close()
    sleep(0.005)

    return True

def read_user(table_path, user_id):

# open user table
    user_table = json.loads(open(table_path).read())
    for user in user_table:
        if user['telegram']['id'] == user_id:
            return user

    return False

def update_user(table_path, user_details):

# open user table and find user
    user_table = json.loads(open(table_path).read())
    for user in user_table:
        if user['telegram_info']['id'] == user_details['telegram']['id']:
            user = user_details

# save table data to local file
            table_data = json.dumps(user_table).encode('utf-8')
            with open(table_path, 'wb') as f:
                f.write(table_data)
                f.close()
            sleep(0.005)
            return True

    return False

def parse_text(input_string, text_commands, update_details, user_id):

    command_name = '/catchall'
    command_parameters = {}
    input_tokens = input_string.split()
    if input_tokens[0] in text_commands.keys():
        command_name = input_tokens[0]
        command_parameters = text_commands[input_tokens[0]]

    return command_name, command_parameters

def analyze_updates(access_token, text_commands, user_table_path, message_folder_path, update_list):

# iterate over update list
    if update_list:
        for i in range(len(update_list)):
            update_details = update_list[i]
            if 'message' in update_details.keys():
                msg_details = update_details['message']
                user_details = msg_details.get('from')
                command_name = ''
                command_details = {}
                command_parameters = {}
                if 'text' in msg_details.keys():
                    parse_kwargs = {
                        'input_string': msg_details['text'],
                        'text_commands': text_commands,
                        'update_details': update_details,
                        'user_id': ''
                    }
                    if isinstance(user_details, dict):
                        parse_kwargs['user_id'] = user_details.get('id')
                    command_name, command_parameters = parse_text(**parse_kwargs)
                if command_name:
                    command_details = text_commands[command_name]
                if command_details and user_details:
                    if command_details['command'] == 'start':
                        record_details = { 'telegram': user_details }
                        if create_user(user_table_path, record_details):
                            message_kwargs = {
                                'access_token': access_token,
                                'user_id': user_details['id'],
                                'msg_text': command_details['msg_text']
                            }
                            message_details = send_message(**message_kwargs)
                            log_message(message_folder_path, message_details)
                    if command_details['message_type'] == 'simple_message':
                        message_kwargs = {
                            'access_token': access_token,
                            'user_id': user_details['id'],
                            'msg_text': command_details['msg_text']
                        }
                        if command_parameters:
                            if command_parameters.get('msg_clarify'):
                                message_kwargs['msg_text'] = command_details['msg_clarify']
                        message_details = send_message(**message_kwargs)
                        log_message(message_folder_path, message_details)

    return True

if __name__ == '__main__':
    from credentials.credTelegram import telegram_credentials
    user_table = json.loads(open('data/user_table.json').read())
    text_commands = json.loads(open('data/text_commands.json').read())
    access_token = telegram_credentials['access_token']
    # cmd_name, cmd_params = parse_text('/help me', text_commands, {}, '')
    while True:
        update_list = get_updates(access_token, 'data/last_update.json')
        analyze_updates(access_token, text_commands, 'data/user_table.json', 'data/outgoing', update_list)
        log_updates('data/last_update.json', 'data/incoming/', update_list)
        sleep(1)
