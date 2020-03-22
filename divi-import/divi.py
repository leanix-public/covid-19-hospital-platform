from bs4 import BeautifulSoup
import json

from random import seed
from random import randint

seed(1)

with open("index.html") as fp:
    soup = BeautifulSoup(fp)

dataList = soup.find("table", {"id": "dataList"}).tbody
content = []
counties = []
for tr in dataList.find_all('tr'):
    tds = tr.find_all('td')

    data = {}
    data['id'] = tds[0].text.strip().split('\n')[0].strip().replace(";", "")
    data['type'] = 'Hospital'
    data['data'] = {
        'location': ' '.join(tds[0].text.strip().split('\n')[2:]),
        'url': tds[1].find('a')['href'] if tds[1].find('a') else None,
        'county': tds[2].text.strip() if tds[2].text.strip() != "0" else None,
        'icuLowCare': tds[3].span.get('class')[0].replace("hr-icon-", ""),
        'icuLowCareId': "ICU Low Care" if tds[3].span.get('class')[0] != "hr-icon-unavailable" else None,
        'icuHighCare': tds[4].span.get('class')[0].replace("hr-icon-", ""),
        'icuHighCareId': "ICU High Care" if tds[4].span.get('class')[0] != "hr-icon-unavailable" else None,
        'ecmo': tds[5].span.get('class')[0].replace("hr-icon-", ""),
        'ecmoId': "ECMO" if tds[5].span.get('class')[0] != "hr-icon-unavailable" else None,
        'hospitalType': 'University' if 'Uni' in tds[0].text else 'Regular',
        'updatedAt': tds[6].text.strip().split('\n')[0].strip()
    }

    bedsICU = 0
    if data['data']['icuHighCareId']: bedsICU += 100
    if data['data']['icuLowCareId']: bedsICU += 200
    if data['data']['ecmoId']: bedsICU += 50
    
    bedsICUUsed = randint(50, 80) / 100 * bedsICU
    data['data']['bedsICU'] = bedsICU
    data['data']['bedsICUUsed'] = bedsICUUsed
    
    content.append(data)

    if (data['data']['county'] not in counties and data['data']['county']):
        counties.append(data['data']['county'])

for county in counties:
    data = {}
    data['id'] = county
    data['type'] = 'County'
    content.append(data)

content.append({"id": "ECMO", "type": "BC"})
content.append({"id": "ICU Low Care", "type": "BC"})
content.append({"id": "ICU High Care", "type": "BC"})


ldif = {
    "connectorId": "divi",
    "connectorType": "divi",
    "connectorVersion": "0.1",
    "lxVersion": "1.0.0",
    "lxWorkspace": "0c4b27c9-dd38-4d42-a7f4-d3a7b5ea0551",
    "description": "",
    "content": content
}

print (json.dumps(ldif, indent=2).replace('\\u00fc', 'ü').replace('\\u00df', 'ß').replace('\\u00f6', 'ö').replace('\\u00e4', 'ä'))
