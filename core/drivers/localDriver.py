from io import StringIO
import core.drivers.config as c
import pandas as pd
import requests
import json
import os

""" The Load and Write sections are just for the json files in the master folder """

### LOAD
def general_load(filePath):
    with open(filePath) as json_file:
        if os.stat(filePath).st_size == 0:
            return {}
        else:
            return json.load(json_file)

def load_Donors():
    return general_load('core/drivers/master/Donors.json')

def load_Interests():
    return general_load('core/drivers/master/Interests.json')

def load_Links():
    return general_load('core/drivers/master/Links.json')
### LOAD


### WRITE
def general_write(filePath, object):
    with open(filePath, 'w') as outFile:
        json.dump(object, outFile, indent=4)

def write_Donors(Donors):
    general_write('core/drivers/master/Donors.json', Donors)

def write_Interests(Interests):
    general_write('core/drivers/master/Interests.json', Interests)

def write_Links(Links):
    general_write('core/drivers/master/Links.json', Links)
### WRITE


def create_Donors(data, Donors):

    uniqueIDs = data['Lookup ID'].unique()

    for ID in uniqueIDs:
        ID = str(ID).split('.')[0]
        if ID.isnumeric() and ID not in Donors:
            Donors[ID] = {}
            Donors[ID]['clicks'] = {}
            Donors[ID]['links'] = {}

    # Count interests for Donor per click
    for i in range(len(data.index)):

        thisDonorID = str(data.at[i, 'Lookup ID']).split('.')[0]
        if not thisDonorID.isnumeric(): # incase there are test IDS such as nan
            continue

        thisLink = data.at[i, ' link']
        thisTimeStamp = data.at[i, ' timestamp']
        newRow = False

        if thisLink not in Donors[thisDonorID]['links']:
            newRow = True        
            Donors[thisDonorID]['links'][thisLink] = [thisTimeStamp]
        elif thisTimeStamp not in Donors[thisDonorID]['links'][thisLink]:
            newRow = True
            Donors[thisDonorID]['links'][thisLink].append(thisTimeStamp)
        
        if newRow:
            for i, enry in enumerate(data.iloc[i][4:]):
                if pd.notna(enry):

                    category = data.columns[i+4].split(': ')[0]
                    Interest = data.columns[i+4].split(': ')[-1]
                    
                    if category not in Donors[thisDonorID]['clicks']:
                        Donors[thisDonorID]['clicks'][category] = {}

                    if Interest not in Donors[thisDonorID]['clicks'][category]:
                        Donors[thisDonorID]['clicks'][category][Interest] = 1
                    else:
                        Donors[thisDonorID]['clicks'][category][Interest] += 1

        if 'version' not in Donors[thisDonorID]: # wonder if there's a way to not check this so often
            Donors[thisDonorID]['version'] = data.iloc[i].Version

    return Donors


def create_Interests(data, Interests):

    for label in data.columns[4:]: # who knows if that 4 will always remain const

        parts = label.split(': ')
        category = parts[0]
        Interest = parts[1]

        if category not in Interests:
            Interests[category] = [Interest]
        elif Interest not in Interests[category]:
            Interests[category].append(Interest)

    return Interests


def create_Links(data, Links):

    for i in range(len(data.index)):

        thisLink = data.at[i, ' link']

        if thisLink not in Links:

            Links[thisLink] = {}

            for i, entry in enumerate(data.iloc[i][4:]):
                if pd.notna(entry):

                    category = data.columns[i+4].split(': ')[0]
                    Interest = data.columns[i+4].split(': ')[-1]

                    if category not in Links[thisLink]:
                        Links[thisLink][category] = [Interest]
                    else:
                        Links[thisLink][category].append(Interest)

    return Links


def compile_data(allData):

    Interests = {}
    Donors = {}
    Links = {}

    for data in allData:
        
        Interests = create_Interests(data, Interests)
        Donors = create_Donors(data, Donors)
        Links = create_Links(data, Links)

    return Donors, Interests,  Links


def fetch_data():

    list_file_url = f"https://www.googleapis.com/drive/v3/files?q=%27{c.folder_id}%27+in+parents&key={c.API_key}"
    file_list = requests.get(list_file_url).json()

    allData = []

    for file in file_list['files']:
        file_id = file['id']
        download_file_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        file_text = requests.get(download_file_url).text
        csv_raw = StringIO(file_text)
        data = pd.read_csv(csv_raw)
        allData.append(data)

    return allData


def fetch_donors_and_interests_from_drive():

    allData = fetch_data()
    Donors, Interests, Links = compile_data(allData)
    return Donors, Interests, Links


def update_master():

    Donors, Interests, Links = fetch_donors_and_interests_from_drive()

    write_Donors(Donors)
    write_Interests(Interests)
    write_Links(Links)