import unittest
from unittest.mock import MagicMock, patch
from layers.graph_connector import MemgraphConnector
from layers.orchestration_v2 import SiliconBrainPhase3

class TestOrchestratorCycleSafety(unittest.TestCase):
    def setUp(self):
        # 1. Connect to Memgraph
        try:
            self.connector = MemgraphConnector()
            with self.connector.driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            self.skipTest(f"Memgraph is offline: {e}")
            
        # 2. Setup testing state loop in DB
        self.clear_test_data()
        
        # Inject cycle: StateA -> StateB -> StateA
        self.state_a = "__TEST__ StateA"
        self.state_b = "__TEST__ StateB"
        self.connector.add_procedure(self.state_a, "Go to StateB", self.state_b, [])
        self.connector.add_procedure(self.state_b, "Go to StateA", self.state_a, [])

    def tearDown(self):
        if hasattr(self, "connector"):
            self.clear_test_data()
            self.connector.close()

    def clear_test_data(self):
        with self.connector.driver.session() as session:
            session.run("MATCH (e:Entity) WHERE e.name STARTS WITH '__TEST__' DETACH DELETE e")
            session.run("MATCH (s:State) WHERE s.name STARTS WITH '__TEST__' DETACH DELETE s")
            session.run("MATCH (n) WHERE n.name STARTS WITH '__TEST__' DETACH DELETE n")

    @patch("layers.orchestration_v2.ChatOpenAI")
    def test_cycle_termination(self, mock_chat_openai):
        # Setup mock instance and its invoke method
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        def mock_invoke(messages):
            prompt_content = messages[0].content
            mock_res = MagicMock()
            if "Your goal is to map this input" in prompt_content:
                mock_res.content = self.state_a
            elif "Identify the primary subjects" in prompt_content:
                mock_res.content = "__TEST__ entity"
            elif "Action to perform" in prompt_content:
                mock_res.content = "Mocked execution output."
            elif "Provide a concise, final report" in prompt_content:
                mock_res.content = "Mocked final answer."
            else:
                mock_res.content = "Default mock response."
            return mock_res
            
        mock_instance.invoke.side_effect = mock_invoke
        
        # Initialize orchestrator
        orchestrator = SiliconBrainPhase3()
        
        # Run graph
        inputs = {
            "user_input": "Test query forcing StateA loop",
            "chat_history": [],
            "history": [],
            "thought_process": [],
            "graph_results": []
        }
        
        result = orchestrator.build_graph().invoke(inputs)
        
        # Assertions to verify correct cycle protection contract
        self.assertEqual(result["current_state"], "END_OF_WORKFLOW")
        # Ensure it visited A and B
        self.assertIn(self.state_a, result["visited"])
        self.assertIn(self.state_b, result["visited"])
        
        # Steps count should be small, showing it exited early instead of looping 15 times
        # Let's count visits:
        # Step 0: StateA (from interpreter)
        # Step 1: StateB (Transition 1)
        # Step 2: StateA (Transition 2 - count is 2)
        # Step 3: StateB (Transition 3 - count is 2)
        # Step 4: StateA (Transition 4 - count is 3 -> triggers guard)
        self.assertTrue(result["steps"] <= 5)
        self.assertEqual(result["visited"].count(self.state_a), 3)
        self.assertTrue(result.get("cycle_detected", False))
