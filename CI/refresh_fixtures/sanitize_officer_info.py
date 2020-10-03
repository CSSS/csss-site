import json

with open('csss-site/src/about/fixtures/about.json') as f:
    about_data = json.load(f)

for officers in about_data:
    if officers['model'] == 'about.officer':
        officers['fields']['sfuid'] = 'sfuid'
        officers['fields']['sfu_email_alias'] = 'sfu_email_alias'
        officers['fields']['phone_number'] = 0
        officers['fields']['github_username'] = 'github_username'
        officers['fields']['gmail'] = 'gmail'

with open('csss-site/src/about/fixtures/about.json', 'w') as outfile:
    json.dump(about_data, outfile, indent=4)
