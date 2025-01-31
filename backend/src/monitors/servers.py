"""
Created On: January 2025
Created By: Sourav Saha
"""
import socket

def check_status(host: str, port: int, timeout=2) -> tuple[bool, int]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))

    except Exception as e:
        print(f"An error occurred: {e}")
        return False, -1

    else:
        sock.close()
        return True, 0
