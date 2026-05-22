import unittest
import os
from layers.graph_connector import MemgraphConnector
from layers.exporter import export_brain

class TestExporterRoundTrip(unittest.TestCase):
    def setUp(self):
        # 1. Connect to Memgraph
        try:
            self.connector = MemgraphConnector()
            # Run a dummy query to check if database is online
            with self.connector.driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            self.skipTest(f"Memgraph is offline: {e}")
            
        # 2. Setup paths
        self.test_export_path = "data/test_brain_export.cypher"
        
        # 3. Clear any existing test nodes
        self.clear_test_data()

    def tearDown(self):
        if hasattr(self, "connector"):
            self.clear_test_data()
            self.connector.close()
        if os.path.exists(self.test_export_path):
            try:
                os.remove(self.test_export_path)
            except:
                pass

    def clear_test_data(self):
        with self.connector.driver.session() as session:
            # Delete any test nodes (Entity or State) starting with __TEST__ and their relationships
            session.run("MATCH (e:Entity) WHERE e.name STARTS WITH '__TEST__' DETACH DELETE e")
            session.run("MATCH (s:State) WHERE s.name STARTS WITH '__TEST__' DETACH DELETE s")
            session.run("MATCH (n) WHERE n.name STARTS WITH '__TEST__' DETACH DELETE n")

    def test_round_trip(self):
        # 1. Add test nodes with special characters/quotes
        subject_name = "__TEST__ Python's GIL"
        object_name = "__TEST__ CPU \"Bottleneck\""
        
        # Add triple (will create RELATION type relationship)
        self.connector.add_triple(subject_name, "causes", object_name)
        
        # Add procedure (will create TRANSITION type relationship)
        state_a = "__TEST__ Idle State"
        state_b = "__TEST__ Working State"
        action = "Start processing Python's code"
        knowledge = ["__TEST__ GIL lock", "__TEST__ thread synchronization"]
        self.connector.add_procedure(state_a, action, state_b, knowledge)

        # 2. Export brain
        os.makedirs(os.path.dirname(self.test_export_path), exist_ok=True)
        export_brain(self.test_export_path, name_prefix="__TEST__")
        self.assertTrue(os.path.exists(self.test_export_path))

        # 3. Read the cypher export file to ensure names are double-quoted properly
        with open(self.test_export_path, "r") as f:
            cypher_content = f.read()
            
        self.assertIn('name: "__TEST__ Python\'s GIL"', cypher_content)
        self.assertIn('name: "__TEST__ CPU \\"Bottleneck\\""', cypher_content)
        self.assertIn('name: "__TEST__ Idle State"', cypher_content)
        self.assertIn('action: "Start processing Python\'s code"', cypher_content)

        # 4. Clear the test data
        self.clear_test_data()

        # Verify it's cleared
        with self.connector.driver.session() as session:
            res = session.run("MATCH (n) WHERE n.name STARTS WITH '__TEST__' RETURN count(n) as count").single()
            self.assertEqual(res["count"], 0)

        # 5. Run the exported cypher queries to re-import
        with self.connector.driver.session() as session:
            for line in cypher_content.splitlines():
                line = line.strip()
                if line and not line.startswith("//"):
                    session.run(line)

        # 6. Verify re-imported data correctness
        # Verify RELATION
        relations = self.connector.query_kg(subject_name)
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0]["predicate"], "causes")
        self.assertEqual(relations[0]["object"], object_name)

        # Verify TRANSITION
        with self.connector.driver.session() as session:
            res = session.run(
                "MATCH (cs:State {name: $cs})-[t:TRANSITION]->(ns:State) "
                "RETURN t.action as action, t.knowledge as knowledge, ns.name as ns_name",
                cs=state_a
            ).single()
            
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], action)
        self.assertEqual(res["knowledge"], knowledge)
        self.assertEqual(res["ns_name"], state_b)
