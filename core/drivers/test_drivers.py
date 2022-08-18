# number of nodes and edges verify (json vs. database)
# Use donors object to count number of edges (json file vs. database cypher stuff)
# look for additional things to test
# count number of edges from Donors.json

import core.drivers.localDriver as ld
import core.drivers.config as c
from core.drivers.dbDriver import App
import os

def local_count(Donors, Interests):

    # Total number of edges
    edge_count = 0
    for donor_id in Donors:
        for category in Donors[donor_id]['clicks']:
            edge_count += len(Donors[donor_id]['clicks'][category])

    # Total number of donor nodes
    donor_node_count = len(Donors)

    # Total number of interest nodes
    interest_node_count = 0
    for category in Interests:
        interest_node_count += len(Interests[category])
    
    return [ donor_node_count, interest_node_count, edge_count ]


def database_count(Local=False):

    app = None

    if Local:
        app = App(c.uri, c.user, c.password) 
    else:
        app = App(os.environ["URI"].replace(' ', '+'), os.environ["USER"], os.environ["PASSWORD"])

    # Fetch number of nodes and edges from Neo4j
    donor_node_count = app.run("MATCH (a:Donor) RETURN COUNT(a)")[0]['COUNT(a)']
    interest_node_count = app.run("MATCH (c:Interest) RETURN COUNT(c)")[0]['COUNT(c)']
    edge_count = app.run("MATCH (:Donor)-[b:CLICKED]-(:Interest) RETURN COUNT(b)")[0]['COUNT(b)']
    app.close()
    
    return [ donor_node_count, interest_node_count, edge_count ]


def check_count(request, Local=False):

    result = None
    Donors = None
    Interests = None

    if Local:
        Donors = ld.load_Donors()
        Interests = ld.load_Interests()
    else:
        Donors = request.session['Donors']
        Interests = request.session['Interests']

    l_count = local_count(Donors, Interests)
    d_count = database_count(Local)

    if l_count == d_count:
        result = True
    else:
        result = False

    if Local:
        print(f'EQUAL : {result}')
        print('\t\tLocal\tDatabase')
        print(f'   Donors\t{l_count[0]}\t{d_count[0]}')
        print(f'Interests\t{l_count[1]}\t{d_count[1]}')
        print(f'    Edges\t{l_count[2]}\t{d_count[2]}')
    else:
        return result, l_count, d_count