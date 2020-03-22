
# coding: utf-8




from requests import post
from json import dumps
from pandas.io.json import json_normalize

api_token = 'DN3Q4dh3a3X6KBf7QTv73QDnuDYymZyOqcUtt4Ch'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' # or something else if you have a dedicated MTM instance - you will know it if that is the case and if you don't just use this one.
request_url_pf = 'https://demo-eu.leanix.net/services/pathfinder/v1/graphql' # same thing as with the auth_url
request_url_metrics = 'https://demo-eu.leanix.net/services/metrics/v1/points'

response = post(auth_url,
                         auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() # this merely throws an error, if Webserver does not respond with a '200 OK'
access_token = response.json()['access_token']




gql_request_query = '''
query allFactSheetsQuery($filter: FilterInput!, $sortings: [Sorting]) {
  allFactSheets(first: 40, filter: $filter, sort: $sortings) {
    totalCount
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        ... on Hospital {
          id
          displayName
          bedsTotal
          bedsTotalUsed
          bedsICU
          bedsICUUsed
          relHospitalToPlace {
            edges{
              node{
                id
                factSheet {
                  id
                  name 
                }
              }
            }
          }
        }
      }
    }
  }
}
''' 
gql_request_variables = {"filter":{"facetFilters":[{"facetKey":"FactSheetTypes","operator":"OR","keys":["Hospital"]},{"facetKey":"relHospitalToPlace","operator":"NOR","keys":["__missing__"]}]},"sortings":[{"key":"displayName","order":"asc"}]}



data = {"query" : gql_request_query, "variables": gql_request_variables}
json_data = dumps(data)
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}
  
response = post(url=request_url_pf, headers=header, data=json_data)
response.raise_for_status()
## Next: take the output and form a meaningful python object:
hospital_data = json_normalize(response.json()['data']['allFactSheets']['edges'])



## extract plac_id
hospital_data['place_id'] = hospital_data.apply(lambda row: row['node.relHospitalToPlace.edges'][0]['node']['factSheet']['id'], axis=1)

##group by the places
places_sum_df = hospital_data.groupby(['place_id']).sum()


places_sum_df.columns = ['bedsTotal','bedsTotalUsed','bedsICU','bedsICUUsed']


for key, value in places_sum_df.iterrows():
    data = {
        'measurement': 'Availability of Beds',
        'workspaceId': '0c4b27c9-dd38-4d42-a7f4-d3a7b5ea0551',
        'tags': [
            {
                'k': 'factSheetId',
                'v': key
            }
        ],
        'fields':
        [
            {
                'k': 'bedsTotal',
                'v': value['bedsTotal']
            },
            {
                'k': 'bedsTotalUsed',
                'v': value['bedsTotalUsed']
            },
            {
                'k': 'bedsICU',
                'v': value['bedsICU']
            },
            {
                'k': 'bedsICUUsed',
                'v': value['bedsICUUsed']
            }
        ]
    }
    json_data = dumps(data)
    header_metrics = {'Authorization': auth_header, 'Content-Type': 'application/json'}
    response = post(url=request_url_metrics, headers=header_metrics, data = json_data)
    response.raise_for_status()
    print(response.json())


# In[38]:


## Generate dummy legacy data:
## comment in the two last lines to generate the dummy data again.
from datetime import timedelta, date
from math import floor
for key, value in places_sum_df.iterrows():
    for single_date in (date.today() - timedelta(n) for n in range(7)):
        
        data = {
            'measurement': 'Availability of Beds',
            'workspaceId': '0c4b27c9-dd38-4d42-a7f4-d3a7b5ea0551',
            'tags': [
                {
                    'k': 'factSheetId',
                    'v': key
                }
            ],
            'time': single_date.isoformat() + 'T08:00:00.000Z',
            'fields':
            [
                {
                    'k': 'bedsTotal',
                    'v': value['bedsTotal']
                },
                {
                    'k': 'bedsTotalUsed',
                    'v': floor(value['bedsTotalUsed'] * 0.95**((date.today()-single_date).days))
                },
                {
                    'k': 'bedsICU',
                    'v': value['bedsICU']
                },
                {
                    'k': 'bedsICUUsed',
                    'v': floor(value['bedsICUUsed'] * 0.95**((date.today()-single_date).days))
                }
            ]
        }
        json_data = dumps(data)
        header_metrics = {'Authorization': auth_header, 'Content-Type': 'application/json'}
#        response = post(url=request_url_metrics, headers=header_metrics, data = json_data)
#        response.raise_for_status()

