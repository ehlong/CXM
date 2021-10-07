import yaml
import json
from twython import Twython

with open('../config/key.yaml') as file:
    api_key = yaml.safe_load(file)

twitter = Twython(api_key['key'], api_key['secret'], oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

twitter = Twython(api_key['key'], access_token=ACCESS_TOKEN)

with open('results.json', 'w') as out:
    json.dump(twitter.search(q='to:EpicGames'), out, indent=2)
