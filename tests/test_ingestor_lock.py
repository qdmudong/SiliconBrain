import unittest
import subprocess
import sys
import os
import tempfile
from layers.ingestor_lock import acquire_ingestor_lock, release_ingestor_lock

class TestIngestorLock(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and path for the lock file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.lock_path = os.path.join(self.temp_dir.name, "test_ingest.lock")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_exclusivity(self):
        # 1. Acquire lock in current process
        lock1 = acquire_ingestor_lock(self.lock_path)
        self.assertIsNotNone(lock1)
        
        # 2. Try to acquire lock in a separate subprocess.
        # It should fail because the parent process holds the lock.
        code_fail = f"""
import sys
import os
# Make sure the project root is in the path
sys.path.insert(0, {repr(os.getcwd())})
from layers.ingestor_lock import acquire_ingestor_lock
lock = acquire_ingestor_lock({repr(self.lock_path)})
if lock is None:
    sys.exit(0)  # lock failed as expected
else:
    sys.exit(1)  # lock succeeded unexpectedly
"""
        res = subprocess.run([sys.executable, "-c", code_fail], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Subprocess should fail to acquire lock while held by parent. Stderr: {res.stderr}")

        # 3. Release lock in parent
        release_ingestor_lock(lock1)

        # 4. Now the subprocess should succeed in acquiring it
        code_succeed = f"""
import sys
import os
sys.path.insert(0, {repr(os.getcwd())})
from layers.ingestor_lock import acquire_ingestor_lock
lock = acquire_ingestor_lock({repr(self.lock_path)})
if lock is not None:
    sys.exit(0)  # lock succeeded as expected
else:
    sys.exit(1)  # lock failed unexpectedly
"""
        res2 = subprocess.run([sys.executable, "-c", code_succeed], capture_output=True, text=True)
        self.assertEqual(res2.returncode, 0, f"Subprocess should succeed in acquiring lock after parent release. Stderr: {res2.stderr}")

    def test_no_directory_component(self):
        # Verify that lock acquisition succeeds even with lock files having no directory prefix (relative to cwd)
        lock_name = "test_ingest_no_dir.lock"
        try:
            lock = acquire_ingestor_lock(lock_name)
            self.assertIsNotNone(lock)
            release_ingestor_lock(lock)
        finally:
            if os.path.exists(lock_name):
                os.remove(lock_name)
