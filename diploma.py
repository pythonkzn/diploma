import requests
import itertools
import json
import codecs

TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'

class User:
    def __init__(self, id):
        self.id = id

    def get_params(self):
        return {
            'user_id': self.id,
            'access_token': TOKEN,
            'v': 5.92
        }

    def get_subs_gid(self):
        params = self.get_params()
        response = requests.get(
            'https://api.vk.com/method/users.getSubscriptions',
            params
        )
        return response.json()['response']['groups']['items']

    def get_subs_gid_fr(self):
        friends_group_list = []
        params = self.get_params()
        response_get_friends = requests.get(
            'https://api.vk.com/method/friends.get',
            params
        )
        friends_list = response_get_friends.json()['response']['items'] #получение списка id друзей пользователя User
        for friend in friends_list:
            params = {
            'user_id': friend,
            'access_token': TOKEN,
            'v': 5.92
            }
            try: #обходим случаи по которым запрос не отвечает ожидаемым форматом
                response_get_groups = requests.get('https://api.vk.com/method/users.getSubscriptions', params)
                friends_group_list.append(response_get_groups.json()['response']['groups']['items']) #получаем список списков групп в которых состоят все друзья user
                print('-')
            except:
                pass
        output_list = list(itertools.chain.from_iterable(friends_group_list))
        return output_list

    def uncommomon_group_list(self):
        user_group_list = self.get_subs_gid()
        friends_group_list = self. get_subs_gid_fr()
        common_group = list(set(user_group_list) & set(friends_group_list)) #получаем список общих групп User и его друзей
        return common_group
        for group in user_group_list:
            for group_com in common_group:
                if group != group_com: #условие на нахождение групп в которых состоит User и не состоят другие пользователи
                    output_list.append(group)
                else:
                    pass
        return set(output_list)



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
        group_data_dict = {}
        output_dict = {}
        params = self.get_params()
        response_get_group = requests.get(
            'https://api.vk.com/method/groups.getById',
            params
        )
        group_data_dict = response_get_group.json()['response'][0]
        output_dict = {'name': group_data_dict['name'], 'gid': group_data_dict['id'], 'members_count': group_data_dict['members_count']}
        return output_dict


user = User(171691064)
uncommon_groups = user.uncommomon_group_list()
output_list = []
for group in uncommon_groups:
    try:
        group = Group(group)
        output_list.append(group.get_group_data())
    except:
        pass
print(output_list)
with codecs.open('groups.json', 'w', encoding='utf-8') as json_file:
    json.dump(output_list, json_file, ensure_ascii=False)

