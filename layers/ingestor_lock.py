import os
import fcntl

def acquire_ingestor_lock(lock_path="data/ingestor.lock"):
    """
    Acquire an OS-level exclusive flock (POSIX only).
    Returns the lock handle (file object) if successful, None otherwise.
    Note: flock is process-scoped, meaning it manages lock exclusivity across different OS processes.
    """
    try:
        dir_name = os.path.dirname(lock_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        # Open in write-intent mode
        lock_file = open(lock_path, "a+")
        
        # Try to acquire exclusive lock without blocking
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Write PID for observability
        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(f"{os.getpid()}\n")
        lock_file.flush()
        
        return lock_file
    except (IOError, OSError):
        try:
            lock_file.close()
        except:
            pass
        return None

def release_ingestor_lock(lock_file):
    """
    Release the OS-level lock by unlocking and closing the file handle.
    """
    if lock_file is not None:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
        except:
            pass
