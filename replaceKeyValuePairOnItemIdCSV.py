import json
import requests
import secrets
import time
import csv
from datetime import datetime

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'
else:
    print 'Editing Stage'

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

requests.packages.urllib3.disable_warnings()

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}

filename = filePath+raw_input('Enter filename (including \'.csv\'): ')
replacedKey = raw_input('Enter key: ')
replacementKey = replacedKey
startTime = time.time()

f=csv.writer(open(filePath+'replacedKeyValuePair'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['replacedKey']+['replacedValue']+['replacementValue']+['delete']+['post'])

with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        itemMetadataProcessed = []
        itemID = row['itemID']
        replacedValue = row['replacedValue'].decode('utf-8')
        replacementValue = row['replacementValue'].decode('utf-8')
        itemMetadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
        for element in itemMetadata:
            languageValue = element['language']
            if element['key'] == replacedKey and element['value'] == replacedValue:
                updatedMetadataElement = {}
                updatedMetadataElement['key'] = replacementKey
                updatedMetadataElement['value'] = unicode(replacementValue)
                updatedMetadataElement['language'] = languageValue
                itemMetadataProcessed.append(updatedMetadataElement)

                provNote = '\''+replacedKey+': '+replacedValue+'\' was replaced by \''+replacementKey+': '+replacementValue+'\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
                provNoteElement = {}
                provNoteElement['key'] = 'dc.description.provenance'
                provNoteElement['value'] = unicode(provNote)
                provNoteElement['language'] = 'en_US'
                itemMetadataProcessed.append(provNoteElement)
            else:
                itemMetadataProcessed.append(element)
        print itemMetadata
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)

        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify, data=itemMetadataProcessed)
        print post
        f.writerow([itemID]+[replacedKey.encode('utf-8')]+[replacedValue.encode('utf-8')]+[replacementValue.encode('utf-8')]+[delete]+[post])
