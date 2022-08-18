import pandas as pd
import json
import os


### LOAD
def general_load(filePath):
    # File path has to point towards static
    cwd = os.getcwd()
    filePath = cwd + '/core/static/' + filePath
    with open(filePath) as json_file:
        if os.stat(filePath).st_size == 0:
            return {}
        else:
            return json.load(json_file)

def load_Donors():
    return general_load('master/Donors.json')

def load_Interests():
    return general_load('master/Interests.json')

def load_Links():
    return general_load('master/Links.json')


### WRITE
def general_write(filePath, object):
    # File path has to point towards static
    cwd = os.getcwd()
    filePath = cwd + '/core/static/' + filePath
    with open(filePath, 'w') as outFile:
        json.dump(object, outFile, indent=4)

def write_Donors(Donors):
    general_write('master/Donors.json', Donors)

def write_Interests(Interests):
    general_write('master/Interests.json', Interests)

def write_Links(Links):
    general_write('master/Links.json', Links)


### CREATE
def create_Donors(data):

    Donors = load_Donors()
    uniqueIDs = data.Lookup_ID.unique()

    for ID in uniqueIDs:
        ID = str(ID)
        if ID not in Donors:
            Donors[ID] = {}
            Donors[ID]['clicks'] = {}
            Donors[ID]['links'] = {}

    # Count interests for Donor per click
    for i in range(len(data.index)):

        thisDonorID = str(data.iloc[i].Lookup_ID)
        thisLink = data.iloc[i].link
        thisTimeStamp = data.iloc[i].timestamp
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

    write_Donors(Donors)


def create_Interests(data):

    Interests = load_Interests()

    for label in data.columns[4:]: # who knows if that 4 will always remain const

        parts = label.split(': ')
        category = parts[0]
        Interest = parts[1]

        if category not in Interests:
            Interests[category] = [Interest]
        elif Interest not in Interests[category]:
            Interests[category].append(Interest)

    write_Interests(Interests)


def create_Links(data):

    Links = load_Links()

    for i in range(len(data.index)):

        thisLink = data.iloc[i].link

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

    write_Links(Links)


### etc

def fresh_start():
    cwd = os.getcwd()
    directory = cwd + '\\data'
    for filename in os.listdir(directory):
        data = pd.read_csv('data/' + filename)
        create_Interests(data)
        create_Links(data)
        create_Donors(data)
