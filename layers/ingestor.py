import os
import time
import json
from layers.extractor import extract_intelligence
from layers.graph_connector import MemgraphConnector

class HungryBrain:
    def __init__(self, watch_dir="data/ingest"):
        self.watch_dir = watch_dir
        self.connector = MemgraphConnector()
        self.processed_files_log = "data/processed_files.json"
        self.processed_files = self._load_processed_log()

    def _load_processed_log(self):
        if os.path.exists(self.processed_files_log):
            with open(self.processed_files_log, "r") as f:
                return set(json.load(f))
        return set()

    def _save_processed_log(self):
        with open(self.processed_files_log, "w") as f:
            json.dump(list(self.processed_files), f)

    def ingest_file(self, file_path):
        print(f"\n[HUNGRY BRAIN] Consuming new file: {file_path}")
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # 1. Extract Intelligence using the Phase 0 Librarian
            intelligence = extract_intelligence(content)
            
            # 2. Ingest into Memgraph using the Phase 1 Connector
            kg_count = len(intelligence.get("knowledge_graph", []))
            pm_count = len(intelligence.get("procedural_map", []))
            
            print(f"[HUNGRY BRAIN] Extracted {kg_count} facts and {pm_count} steps.")
            
            for triple in intelligence.get("knowledge_graph", []):
                self.connector.add_triple(triple["subject"], triple["predicate"], triple["object"])
                
            for step in intelligence.get("procedural_map", []):
                self.connector.add_procedure(step["current_state"], step["action"], 
                                        step["next_state"], step["required_knowledge"])
            
            print(f"[HUNGRY BRAIN] Successfully integrated {os.path.basename(file_path)} into memory.")
            return True
        except Exception as e:
            print(f"[HUNGRY BRAIN] Error consuming {file_path}: {e}")
            return False

    def watch(self, once=False):
        print(f"--- SiliconBrain Ingestion Service Started (Watching {self.watch_dir}) ---")
        while True:
            files = [f for f in os.listdir(self.watch_dir) if f.endswith(('.md', '.txt'))]
            new_files = [f for f in files if f not in self.processed_files]
            
            if not new_files and once:
                break
                
            for file_name in new_files:
                full_path = os.path.join(self.watch_dir, file_name)
                if self.ingest_file(full_path):
                    self.processed_files.add(file_name)
                    self._save_processed_log()
            
            if once:
                break
            time.sleep(10) # Poll every 10 seconds

if __name__ == "__main__":
    # Ensure the directory exists
    if not os.path.exists("data/ingest"):
        os.makedirs("data/ingest")
        
    hb = HungryBrain()
    hb.watch()
