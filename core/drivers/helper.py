from io import StringIO
import core.drivers.config as c
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import os

def get_click_data(allResult): # For exporting Cypher results

    if not allResult:
        print('There is no result corresponding to this search')
        return None
    
    # Check the category, a, b or c
    category = set(allResult[0].keys())

    if category == {'a'}:
        result = pd.DataFrame([ r['a'] for r in allResult])
        result['Labels'] = [ r['a'].labels for r in allResult]
    
    elif category == {'b'}:
        result = pd.DataFrame([ r['b'] for r in allResult])
        result['Labels'] = [ r['b'].labels for r in allResult]
    
    elif category == {'c'}:
        result = pd.DataFrame([ r['c'] for r in allResult])
        result['start_node_id'] = [r['c'].nodes[0].id for r in allResult]
        result['end_node_id'] = [r['c'].nodes[1].id for r in allResult]
        result['Relationship_id'] = [r['c'].id for r in allResult]
    
    elif category == {'a','b','c'}:

        # We frist convert all the data from the Neo4j query to pandas dataframe first
        part1 = pd.DataFrame([d['c'].nodes[0] for d in allResult])
        part1['donor_labels'] = [next(iter((d['c'].nodes[0].labels))) for d in allResult]
        part2 = pd.DataFrame([d['c'].nodes[1] for d in allResult])
        part2['interests_label'] = [next(iter((d['c'].nodes[1].labels))) for d in allResult]
        part3 = pd.DataFrame([d['c'] for d in allResult])
        show = pd.concat([part1,part2,part3], axis = 1)

        # Convert the dataframe to data with click information with
        df = pd.get_dummies(show.iloc[:,[0,4]])
        df = pd.concat([df['ID'], df.iloc[:,1:].mul(show['count'], axis = 0)], axis = 1).groupby(['ID']).sum()
        df.reset_index(inplace=True)
        df.columns = df.columns.str.replace('Name_', '')

        if len(df.index) > 1:
            totalRow = {}
            for col in df:
                if col == 'ID':
                    totalRow[col] = ['Total']
                elif col == 'Version':
                    totalRow[col] = ['N/A']
                else:
                    totalRow[col] = [df[col].sum()]
            df2 = pd.DataFrame(totalRow)
            df = pd.concat([df, df2], ignore_index = True)
        
        result = df
        
    return result


def get_Interest_Count(Donors, Interests, Links):

    InterestCount = {}

    # Initialize 
    for category in Interests:
        for Interest in Interests[category]:
            InterestCount[Interest] = {'actual' : 0, 'possible' : 0}

    # count actual All Clicks
    for donor_id in Donors:
        for category in Donors[donor_id]['clicks']:
            for Interest in Donors[donor_id]['clicks'][category]:
                InterestCount[Interest]['actual'] += Donors[donor_id]['clicks'][category][Interest]

    # count possible
    list_file_url = f"https://www.googleapis.com/drive/v3/files?q=%27{c.folder_id}%27+in+parents&key={c.API_key}"
    file_list = requests.get(list_file_url).json()
    for file in file_list['files']:
        file_id = file['id']
        download_file_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        file_text = requests.get(download_file_url).text
        csv_raw = StringIO(file_text)
        data = pd.read_csv(csv_raw)
        uniqueIDs = data['Lookup ID'].unique()
        uniqueLinks = data[' link'].unique()

        for link in uniqueLinks:
            if link in Links:
                for category in Links[link]:
                    for Interest in Links[link][category]:
                        InterestCount[Interest]['possible'] += len(uniqueIDs)

    # set apRatio
    for category in InterestCount:
        for Interest in InterestCount: 

            apRatio = InterestCount[Interest]['actual'] / InterestCount[Interest]['possible']
            InterestCount[Interest]['apRatio'] = apRatio

    return InterestCount

def sort_interests_by(type, InterestCount):

    acceptedTypes = ['actual', 'possible', 'apRatio']

    if type in acceptedTypes:
        InterestCount = dict(sorted(InterestCount.items(), key=lambda item: item[1][type]))
    
    else:
        print(f'Type : {type} not recognized')
        return
    
    return InterestCount

def show_apRatio_graph(InterestCount):

    InterestCount = sort_interests_by('apRatio', InterestCount)
    labels = list(InterestCount.keys())
    apRatios = [x['apRatio']*100 for x in InterestCount.values()]

    plt.figure(figsize=(30, 20))
    plt.barh(labels, apRatios, color='#00274C')
    plt.ylabel('Interest Labels', fontweight='bold')
    plt.xlabel('Effectiveness %', fontweight='bold')
    plt.title('Interest Labels actual over possible ratios', fontweight='bold')
    
    # plt.savefig('actualOverPossible.jpg')
    plt.show()

def show_AVP_graph(InterestCount):
    
    InterestCount = sort_interests_by('possible', InterestCount)
    InterestCount = sort_interests_by('actual', InterestCount)

    plt.figure(facecolor='#FFCB05', figsize=(2000, 30))

    labels = list(InterestCount.keys())
    actual = [x['actual'] for x in InterestCount.values()]
    possible = [x['possible'] for x in InterestCount.values()]

    factor = 30
    x = np.arange(0, factor*len(labels), factor)  # the label locations

    fig, ax = plt.subplots()
    fig.set_size_inches(30, 36, forward=True)

    width = 12  # the width of the bars
    rects1 = ax.barh(x - width/2, actual, width, label='actual', align='center', color='#00274C')
    rects2 = ax.barh(x + width/2, possible, width, label='possible', align='center', color='#FFCB05')

    ax.set_xlabel('Total Clicks', fontweight='bold')
    ax.set_title('Actual vs Possible Number of Clicks', fontweight='bold')
    ax.set_yticks(x, labels, fontweight='bold')

    ax.bar_label(rects1)
    ax.bar_label(rects2)

    # plt.savefig('actualVSpossible.jpg')
    plt.show()