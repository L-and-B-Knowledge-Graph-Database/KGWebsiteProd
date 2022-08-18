from neo4j import GraphDatabase

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear(self):
        with self.driver.session() as session:
            session.run("MATCH (a) -[r] -> () DELETE a, r ")    # clear edges
            session.run("MATCH (a) DELETE a ")                  # clear nodes
    
    def update_neo4j(self, Donors, Interests):
        self.create_donor_nodes(Donors)
        self.create_interest_nodes(Interests)
        self.create_click_edges(Donors)

    def fresh_start(self, Donors, Interests):
        self.clear()
        self.update_neo4j(Donors, Interests)

    def run(self, command):
        with self.driver.session(database = 'neo4j') as session:

            try:
                result = session.run(command)
            except:
                print('neo4j recieved a bad command')
                return []

            return [dict(i) for i in result]


    def create_donor_nodes(self, Donors):
        with self.driver.session() as session:

            result = self.run('MATCH (a:Donor) RETURN a')
            resultDonors = []
            badDonors = []

            for node in result:
                if str(node['a']['ID']) not in Donors:
                    if node['a'].id not in badDonors:
                        badDonors.append(node['a'].id)
                elif node['a']['ID'] not in resultDonors:
                    resultDonors.append(node['a']['ID'])
                elif node['a'].id not in badDonors:
                    badDonors.append(node['a'].id)

            if badDonors:
                self.run(f"MATCH (a) WHERE ID(a) IN {badDonors} DETACH DELETE a")

            for donor_id in Donors:
                if int(donor_id) not in resultDonors:
                    session.run(f"CREATE (:Donor {{ID: {int(donor_id)}, Version: '{Donors[donor_id]['version']}', abr: '{Donors[donor_id]['version'][0]}'}})")


    def create_interest_nodes(self, Interests):
        with self.driver.session() as session: # For Future - What if local has more or less nodes than database. Should handle both cases automatically.

            justInterests = []
            for category in Interests:
                for Interest in Interests[category]:
                    justInterests.append(Interest)

            result = self.run('MATCH (b:Interest) RETURN b')
            resultInterests = []
            badInterests = []

            for node in result:
                if node['b']['Name'] not in justInterests:
                    if node['b'].id not in badInterests:
                        badInterests.append(node['b'].id)
                elif node['b']['Name'] not in resultInterests:
                    resultInterests.append(node['b']['Name'])
                elif node['b'].id not in badInterests:
                    badInterests.append(node['b'].id)

            if badInterests:
                self.run(f"MATCH (b) WHERE ID(b) IN {badInterests} DETACH DELETE b")

            for category in Interests:
                for Interest in justInterests:
                    if Interest not in resultInterests:
                        session.run(f"CREATE (:Interest {{Name: '{Interest}', Type:'{category}'}})")


    def create_click_edges(self, Donors):
        with self.driver.session() as session:

            justClicks = {}
            for donor_id in Donors:
                justClicks[donor_id] = {}
                for category in Donors[donor_id]['clicks']:
                    for Interest in Donors[donor_id]['clicks'][category]:
                        justClicks[donor_id][Interest] = Donors[donor_id]['clicks'][category][Interest]

            result = self.run('MATCH (a:Donor)-[c:CLICKED]->(b:Interest) RETURN a, b, c')
            resultEdges = {}
            badEdges = []

            for edge in result:

                if str(edge['a']['ID']) not in justClicks or edge['b']['Name'] not in justClicks[str(edge['a']['ID'])]:
                    if edge['c'].id not in badEdges:
                        badEdges.append(edge['c'].id)
                else:
                    if str(edge['a']['ID']) not in resultEdges:
                        resultEdges[str(edge['a']['ID'])] = {}
                    if edge['b']['Name'] not in resultEdges[str(edge['a']['ID'])]:
                        resultEdges[str(edge['a']['ID'])][edge['b']['Name']] = edge['c']['count']
                    elif edge['c'].id not in badEdges:
                        badEdges.append(edge['c'].id)

            if badEdges:
                print(badEdges)
                self.run(f"MATCH (:Donor)-[c:CLICKED]->(:Interest) WHERE ID(c) IN {badEdges} DELETE c")
            
            for donor_id in justClicks:
                for Interest in justClicks[donor_id]:

                    if donor_id not in resultEdges or Interest not in resultEdges[donor_id]:
                        # Create new edge
                        print('create', donor_id, Interest, justClicks[donor_id][Interest])
                        command = (
                            "MATCH (a:Donor), (b:Interest) "
                            f"WHERE a.ID = {int(donor_id)} AND b.Name = '{Interest}'"
                            f"CREATE (a)-[r:CLICKED {{count: {justClicks[donor_id][Interest]}}}]->(b) "
                        )
                        session.run(command)

                    elif justClicks[donor_id][Interest] != resultEdges[donor_id][Interest]:
                        print('set', donor_id, Interest, justClicks[donor_id][Interest])
                        command = (
                                f"MATCH (:Donor {{ID: {donor_id}}})-[b:CLICKED]-(:Interest {{Name: '{Interest}'}}) "
                                f"SET b.count = {justClicks[donor_id][Interest]} "
                            )
                        session.run(command)
