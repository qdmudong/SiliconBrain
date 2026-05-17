from pyvis.network import Network
from layers.graph_connector import MemgraphConnector
import os

class BrainVisualizer:
    def __init__(self):
        self.connector = MemgraphConnector()
        self.net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False, directed=True)
        # Add physics for better layout
        self.net.force_atlas_2based()

    def generate_map(self, output_path="brain_map.html"):
        print(f"[VISUALIZER] Fetching graph data from Memgraph...")
        
        with self.connector.driver.session() as session:
            # 1. Fetch Entities and their Relations
            entity_query = "MATCH (s:Entity)-[r:RELATION]->(o:Entity) RETURN s.name as s, r.type as rel, o.name as o"
            entities = session.run(entity_query)
            
            # 2. Fetch States and their Transitions
            state_query = "MATCH (cs:State)-[t:TRANSITION]->(ns:State) RETURN cs.name as s, t.action as action, ns.name as o"
            states = session.run(state_query)

            # Process Entities (Blue nodes)
            for record in entities:
                self.net.add_node(record["s"], label=record["s"], color="#3498db", title="Entity")
                self.net.add_node(record["o"], label=record["o"], color="#3498db", title="Entity")
                self.net.add_edge(record["s"], record["o"], title=record["rel"], label=record["rel"], color="#5dade2")

            # Process States (Green nodes)
            for record in states:
                self.net.add_node(record["s"], label=record["s"], color="#2ecc71", shape="diamond", title="Workflow State")
                self.net.add_node(record["o"], label=record["o"], color="#2ecc71", shape="diamond", title="Workflow State")
                self.net.add_edge(record["s"], record["o"], title=record["action"], label="ACTION", color="#58d68d")

        self.net.save_graph(output_path)
        print(f"[VISUALIZER] Brain Map generated successfully: {os.path.abspath(output_path)}")
        self.connector.close()

if __name__ == "__main__":
    viz = BrainVisualizer()
    viz.generate_map()
