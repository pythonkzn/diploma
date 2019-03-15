import requests
import itertools
import json
import codecs
import time


class User:
    def __init__(self, id):
        self.id = id

    def get_params(self):
        return dict(user_id=self.id, access_token=TOKEN, v=5.92)

    def get_subs_gid(self):
        params = self.get_params()
        response = requests.get(
            'https://api.vk.com/method/groups.get',
            params
        )
        return response.json()['response']['items']

    def get_subs_gid_fr(self):
        friends_group_list = []
        params = self.get_params()
        response_get_friends = requests.get(
            'https://api.vk.com/method/friends.get',
            params
        )
        friends_list = response_get_friends.json()['response']['items']   # получение списка id друзей пользователя User
        for friend in friends_list:
            params = dict(user_id=friend, access_token=TOKEN, v=5.92)
            try:  # обходим случаи по которым запрос не отвечает ожидаемым форматом
                response_get_groups = requests.get('https://api.vk.com/method/groups.get', params)
                friends_group_list.append(response_get_groups.json()['response']['items'])
                # получаем список списков групп в которых состоят все друзья user
                print('-')
                time.sleep(1)
            except Exception as e:
                print(response_get_groups.json())  # выводим полученные ошибки от API VK
        output_list = list(itertools.chain.from_iterable(friends_group_list))  # делаем список групп из списка списков
        return output_list

    def uncommon_group_list(self):
        user_group_set = set(self.get_subs_gid())
        friends_group_set = set(self.get_subs_gid_fr())
        return set(user_group_set.difference(friends_group_set))


class Group:
    def __init__(self, id):
        self.id = id

    def get_params(self):
        return {
            'group_id': self.id,
            'fields': 'members_count',
            'access_token': TOKEN,
            'v': 5.92
        }

    def get_group_data(self):
        params = self.get_params()
        response_get_group = requests.get(
            'https://api.vk.com/method/groups.getById',
            params
        )
        group_data_dict = response_get_group.json()['response'][0]
        output_dict = {'name': group_data_dict['name'],
                       'gid': group_data_dict['id'],
                       'members_count': group_data_dict['members_count']}
        return output_dict


if __name__ == "__main__":
    with open('token.json', 'r') as file:
        data = json.load(file)
        TOKEN = data[0]['token']

    user_input = input('Введите id или имя пользователя: ')

    try:
        int(user_input)
        user = User(user_input)
    except ValueError:
        params = {
            'user_ids': user_input,
            'access_token': TOKEN,
            'v': 5.92
        }
        response_get_id = requests.get(
            'https://api.vk.com/method/users.get',
            params
        )
        user = User(int(response_get_id.json()['response'][0]['id']))  # получили по имени пользователя его id

    output_list = []
    uncommon_groups = user.uncommon_group_list()

    for group in uncommon_groups:
        try:
            group = Group(group)
            output_list.append(group.get_group_data())
        except Exception as e:
            pass

    with codecs.open('groups.json', 'w', encoding='utf-8') as json_file:
        json.dump(output_list, json_file, ensure_ascii=False)
    print(uncommon_groups)
