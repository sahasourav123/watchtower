"""
Created On: January 2025
Created By: Sourav Saha
"""
import ssl
import socket
from datetime import datetime
import whois
import certifi

from monitors import servers

def check_status(domain_name: str) -> tuple[bool, int]:
    return servers.check_status('localhost', 80)

def check_domain_expiry(domain_name: str) -> tuple[bool, int]:
    try:
        domain_info = whois.whois(domain_name)
        expiry_date = domain_info.expiration_date

        # Handle the possibility of multiple expiration dates
        if isinstance(expiry_date, list):
            expiry_date = expiry_date[0]

        if expiry_date is None:
            print(f"Could not retrieve expiration date for {domain_name}.")
            return False, -10

        else:
            remaining_days = (expiry_date - datetime.utcnow()).days
            print(f"Domain {domain_name} expires on {expiry_date}.")
            print(f"Days until expiry: {remaining_days}")
            return True, remaining_days

    except Exception as e:
        print(f"An error occurred: {e}")
        return False, -10


def check_certificate_expiry(hostname: str, port=443) -> tuple[bool, int]:
    context = ssl.create_default_context(cafile=certifi.where())

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()

    if not cert:
        print(f"Could not retrieve certificate for {hostname}")
        return False, -10

    # Get the certificate's expiration date
    exp_date_str = cert['notAfter']
    exp_date = datetime.strptime(exp_date_str, '%b %d %H:%M:%S %Y %Z')

    # Get the current date
    remaining_days = (exp_date - datetime.utcnow()).days

    print(f"Certificate for {hostname} is valid until {exp_date}, with {remaining_days} days remaining.")
    return True, remaining_days
