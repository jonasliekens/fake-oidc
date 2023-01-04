import json
import os

users_dir = 'resources/users'


def find_all_user_tokens_and_details():
    users = {}

    for file in os.listdir(users_dir):
        if file.endswith('.json'):
            with open(os.path.join(users_dir, file), 'r') as user_file:
                users[os.path.basename(user_file.name).replace('.json', '')] = json.loads(user_file.read())

    return users


def find_user_by_token(token):
    user_file_path = os.path.join(users_dir, '{}.json'.format(token))

    if os.path.exists(user_file_path):
        with open(user_file_path) as user_file:
            return json.loads(user_file.read())
    else:
        return None

