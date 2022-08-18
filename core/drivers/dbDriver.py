from neo4j import GraphDatabase

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))


    def run(self, command):
        with self.driver.session(database = 'neo4j') as session:
            try:
                result = session.run(command)
            except:
                print('neo4j recieved a bad command :', command)
                return ''
            return [dict(i) for i in result]

    
    def fresh_start(self, Donors, Interests):
        self.reset()
        self.create_donor_nodes(Donors)
        self.create_interest_nodes(Interests)
        self.create_click_edges(Donors)


    def reset(self):
        with self.driver.session() as session:
            session.run("MATCH (a) -[r] -> () DELETE a, r ")    # clear edges
            session.run("MATCH (a) DELETE a ")                  # clear nodes

    def fix_donors(self, Donors):
        with self.driver.session() as session:
            for donor_id in Donors:
                checker = f'MATCH (a:Donor {{ID: {donor_id}}}) RETURN a'
                checkResult = self.run(checker)
                if len(checkResult) == 1:
                    query = (
                        f'MATCH (a:Donor {{ID: {donor_id}}})'
                        f" SET a.abr = '{Donors[donor_id]['version'][0]}' "
                    )
                    session.run(query)
                else:
                    print(f'Donor {donor_id} not found')


    def create_donor_nodes(self, Donors):
        with self.driver.session() as session:
            for donor_id in Donors:
                session.run(f"CREATE (:Donor {{ID: {int(donor_id)}, Version: '{Donors[donor_id]['version']}', abr: '{Donors[donor_id]['version'][0]}'}})")


    def create_interest_nodes(self, Interests):
        with self.driver.session() as session:
            for category in Interests:
                for Interest in Interests[category]:
                    session.run(f"CREATE (:Interest {{Name: '{Interest}', Type:'{category}'}})")


    def create_click_edges(self, Donors):
        with self.driver.session() as session:
            for donor_id in Donors:
                for category in Donors[donor_id]['clicks']:
                    for Interest in Donors[donor_id]['clicks'][category]:

                        checker = f'MATCH (a:Donor {{ID: {donor_id}}})-[b:CLICKED]-(c:Interest {{name: "{Interest}"}}) RETURN a, b, c' 
                        checkResult = self.run(checker)

                        if len(checkResult) == 0:
                            query = (
                                "MATCH (a:Donor), (b:Interest) "
                                f"WHERE a.ID = {int(donor_id)} AND b.Name = '{Interest}'"
                                f"CREATE (a)-[r:CLICKED {{count: {Donors[donor_id]['clicks'][category][Interest]}}}]->(b) "
                            )
                            session.run(query)

                        elif len(checkResult) == 1:
                            if checkResult[0]['b']['count'] != Donors[donor_id]['clicks'][category][Interest]:
                                # if not equal, fix
                                print(f'TEMP : EDGE UPDATED BETWEEN {donor_id} and {Interest}')
                                
                                query = (
                                    f'MATCH (:Donor {{ID: {donor_id}}})-[b:CLICKED]-(:Interest {{name: "{Interest}"}}) '
                                    f"SET b.count = {Donors[donor_id]['clicks'][category][Interest]} "
                                )
                                session.run(query)

                        else:
                            print(f'ERROR : MORE THAN 1 EDGE BETWEEN {donor_id} and {Interest}')


    def close(self):
        self.driver.close()
