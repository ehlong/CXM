import yaml

with open('config/key.yaml') as file:
    api_key = yaml.safe_load(file)

print(api_key)



