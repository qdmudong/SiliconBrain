from layers.graph_connector import MemgraphConnector
import os

def export_brain(output_path="data/trained_brain.cypher", name_prefix=None):
    print(f"--- Exporting SiliconBrain Memory to {output_path} ---")
    connector = MemgraphConnector()
    
    with connector.driver.session() as session:
        if name_prefix:
            # Fetch nodes starting with prefix
            nodes_result = session.run("MATCH (n) WHERE n.name STARTS WITH $prefix RETURN n, labels(n) as labels", prefix=name_prefix)
            # Fetch relationships between nodes both starting with prefix
            rels_result = session.run(
                "MATCH (s)-[r]->(o) WHERE s.name STARTS WITH $prefix AND o.name STARTS WITH $prefix "
                "RETURN s.name as s_name, type(r) as r_type, r, o.name as o_name",
                prefix=name_prefix
            )
        else:
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
                rel = record["r"]
                
                # Extract and format relationship properties
                props_list = [f"{k}: {json_repr(v)}" for k, v in rel.items()]
                props_str = f" {{{', '.join(props_list)}}}" if props_list else ""
                
                # Use JSON representation for names to handle nested single/double quotes safely in Cypher
                s_name_esc = json_repr(s_name)
                o_name_esc = json_repr(o_name)
                
                # We assume nodes are identified by name for simplicity in MERGE
                query = f"MATCH (s {{name: {s_name_esc}}}), (o {{name: {o_name_esc}}}) MERGE (s)-[:{r_type}{props_str}]->(o);\n"
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
