import requests, os

# def get_all_user_id():
#     headers = {"Content-Type": "application/json"}
#     auth = {'access_token': config.access_token}
#     all_users = []
    
#     for group_id in config.group_ids:
#         FB_URL = config.graph_api + '/' + str(group_id) + config.workplace_user_data_fetch
#         response = requests.request("GET", FB_URL, headers=headers, params=auth) 
#         all_users.extend(response.json()['data'])

#         while 'next' in response.json().get('paging',{}):
#             result = requests.get(response.json()['paging']['next'])
#             response = result
#             all_users.extend(result.json()['data'])
#     return all_users

# all_users = get_all_user_id()
headers = {
  'Accept': 'application/json',
  'Workvivo-Id': os.getenv("WORKVIVO_ID"),
  'Authorization': "Bearer " + os.getenv("WORKVIVO_TOKEN")
}

def get_user_data(id_):
    url = os.getenv("WORKVIVO_API_URL").split('chat/bots/message')[0] + f"users/{str(id_)}"
    payload={}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response['data']

# print(">>>>", get_user_data('3003104378'))
