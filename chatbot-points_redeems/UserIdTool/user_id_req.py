import requests

USERNAME = 'enchom'

URL = 'https://api.twitch.tv/helix/users?login=' + USERNAME

h = {}
h['Client-ID'] = 'op2ffge97zlikpfm8ss3hzci6kxsip'

r = requests.get(url = URL, headers = h)

print(r.json()['data'][0]['id'])
