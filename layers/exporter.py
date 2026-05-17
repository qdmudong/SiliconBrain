from layers.graph_connector import MemgraphConnector
import os

def export_brain(output_path="data/trained_brain.cypher"):
    print(f"--- Exporting SiliconBrain Memory to {output_path} ---")
    connector = MemgraphConnector()
    
    with connector.driver.session() as session:
        # Fetch all nodes and their properties
        nodes_result = session.run("MATCH (n) RETURN n, labels(n) as labels")
        
        # Fetch all relationships
        rels_result = session.run("MATCH (s)-[r]->(o) RETURN s.name as s_name, type(r) as r_type, r, o.name as o_name")
        
        with open(output_path, "w") as f:
            f.write("// SiliconBrain Pre-Trained Memory Snapshot\n")
            f.write("// Total Nodes and Relationships exported from local Memgraph instance.\n\n")
            
            # Export Nodes
            node_count = 0
            for record in nodes_result:
                node = record["n"]
                labels = ":".join(record["labels"])
                props = ", ".join([f"{k}: {json_repr(v)}" for k, v in node.items()])
                f.write(f"MERGE (n:{labels} {{{props}}});\n")
                node_count += 1
            
            f.write(f"\n// Exported {node_count} nodes.\n\n")
            
            # Export Relationships
            rel_count = 0
            for record in rels_result:
                s_name = record["s_name"]
                o_name = record["o_name"]
                r_type = record["r_type"]
                # We assume nodes are identified by name for simplicity in MERGE
                query = f"MATCH (s {{name: '{s_name}'}}), (o {{name: '{o_name}'}}) MERGE (s)-[:{r_type}]->(o);\n"
                f.write(query)
                rel_count += 1
                
            f.write(f"\n// Exported {rel_count} relationships.\n")

    connector.close()
    print(f"✅ Successfully exported {node_count} nodes and {rel_count} relationships.")

def json_repr(val):
    import json
    return json.dumps(val)

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    export_brain()
