from bs4 import BeautifulSoup
import json

with open("index.html") as fp:
    soup = BeautifulSoup(fp)

dataList = soup.find("table", {"id": "dataList"}).tbody
content = []
counties = []
for tr in dataList.find_all('tr'):
    tds = tr.find_all('td')

    data = {}
    data['id'] = tds[0].text.strip().split('\n')[0].strip()
    data['type'] = 'Hospital'
    data['data'] = {
        'location': ' '.join(tds[0].text.strip().split('\n')[2:]),
        'url': tds[1].find('a')['href'] if tds[1].find('a') else None,
        'county': tds[2].text.strip() if tds[2].text.strip() != "0" else None,
        'icuLowCare': tds[3].span.get('class')[0],
        'icuHighCare': tds[4].span.get('class')[0],
        'ecmo': tds[5].span.get('class')[0],
        'university': 'Uni' in tds[0].text,
        'updatedAt': tds[6].text.strip().split('\n')[0].strip()
    }
    content.append(data)

    if (data['data']['county'] not in counties and data['data']['county']):
        counties.append(data['data']['county'])

for county in counties:
    data = {}
    data['id'] = county
    data['type'] = 'County'
    content.append(data)

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
