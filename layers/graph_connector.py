from neo4j import GraphDatabase
import json

class MemgraphConnector:
    def __init__(self, uri="bolt://localhost:7687", user="", password=""):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def add_triple(self, subject, predicate, object_val):
        with self.driver.session() as session:
            # Ensure everything is a string to avoid type errors in Cypher
            query = (
                "MERGE (s:Entity {name: toString($subject)}) "
                "MERGE (o:Entity {name: toString($object)}) "
                "MERGE (s)-[r:RELATION {type: toString($predicate)}]->(o)"
            )
            session.run(query, subject=subject, predicate=predicate, object=object_val)

    def add_procedure(self, current_state, action, next_state, required_knowledge):
        with self.driver.session() as session:
            # Ensure everything is a string
            query = (
                "MERGE (cs:State {name: toString($current_state)}) "
                "MERGE (ns:State {name: toString($next_state)}) "
                "MERGE (cs)-[a:TRANSITION {action: toString($action), knowledge: $knowledge}]->(ns)"
            )
            session.run(query, current_state=current_state, next_state=next_state, 
                        action=action, knowledge=required_knowledge)

    def query_kg(self, subject):
        with self.driver.session() as session:
            # Case-insensitive match, ensuring we only compare strings and handle types safely
            query = """
            MATCH (s:Entity)
            WHERE (valueType(s.name) = 'STRING') AND (toLower(s.name) = toLower(toString($subject)))
            MATCH (s)-[r]->(o)
            RETURN r.type as rel, o.name as obj
            """
            result = session.run(query, subject=subject)
            return [{"predicate": record["rel"], "object": record["obj"]} for record in result]

def ingest_data(file_path):
    connector = MemgraphConnector()
    connector.clear()
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    print(f"Ingesting {len(data['knowledge_graph'])} triples...")
    for triple in data["knowledge_graph"]:
        connector.add_triple(triple["subject"], triple["predicate"], triple["object"])
        
    print(f"Ingesting {len(data['procedural_map'])} state transitions...")
    for step in data["procedural_map"]:
        connector.add_procedure(step["current_state"], step["action"], 
                                step["next_state"], step["required_knowledge"])
    
    connector.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data("data/manifesto_extracted.json")
