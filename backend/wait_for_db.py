import socket
import time
import os
import sys

def is_port_open(host, port):
    """Check if a port is open on a host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False

def main():
    """Wait for database to become available"""
    # Get database host from environment variable or use default
    db_host = os.getenv('DB_HOST', 'db')
    db_port = int(os.getenv('DB_PORT', 5432))
    max_retries = 30
    retry_interval = 2
    
    print(f"Waiting for database at {db_host}:{db_port}...")
    
    for i in range(max_retries):
        if is_port_open(db_host, db_port):
            print("Database is ready!")
            return True
        else:
            print(f"Database not ready yet (attempt {i+1}/{max_retries}), retrying in {retry_interval}s...")
            time.sleep(retry_interval)
    
    print("Database was not ready in time. Exiting.")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
