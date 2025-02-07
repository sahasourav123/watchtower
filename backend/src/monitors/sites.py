"""
Created On: January 2025
Created By: Sourav Saha
"""
import ssl
import socket
from datetime import datetime
import whois
import certifi
import requests
import dns.resolver
import dns.exception

from utils.commons import logger


def check_website(domain_name: str) -> tuple[bool, int]:
    try:
        res = requests.get(
            domain_name,
            verify=False,
            timeout=10
        )
        return True, res.status_code

    # handle name resolution error
    except requests.exceptions.ConnectionError as e:
        # logger.error(f"Connection Error: {e}")
        return False, -1

    # handle timeout error
    except requests.exceptions.Timeout as e:
        # logger.error(f"Timeout Error: {e}")
        return False, -2

    # handle other exceptions
    except Exception as e:
        # logger.error(f"Error: {e}")
        return False, -10

def check_domain_expiry(domain_name: str) -> tuple[bool, int]:
    try:
        domain_info = whois.whois(domain_name)
        expiry_date = domain_info.expiration_date

        # Handle the possibility of multiple expiration dates
        if isinstance(expiry_date, list):
            expiry_date = expiry_date[0]

        if expiry_date is None:
            # logger.error(f"Could not retrieve expiration date for {domain_name}.")
            return False, -10

        else:
            remaining_days = (expiry_date - datetime.utcnow()).days
            # logger.info(f"Domain {domain_name} expires after {remaining_days} days on {expiry_date}.")
            return True, remaining_days

    except Exception as e:
        # logger.error(f"An error occurred: {e}")
        return False, -10


def check_certificate_expiry(hostname: str, port=443) -> tuple[bool, int]:
    context = ssl.create_default_context(cafile=certifi.where())

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()

    if not cert:
        # logger.error(f"Could not retrieve certificate for {hostname}")
        return False, -10

    # Get the certificate's expiration date
    exp_date_str = cert['notAfter']
    exp_date = datetime.strptime(exp_date_str, '%b %d %H:%M:%S %Y %Z')

    # Get the current date
    remaining_days = (exp_date - datetime.utcnow()).days

    # logger.info(f"Certificate for {hostname} is valid until {exp_date}, with {remaining_days} days remaining.")
    return True, remaining_days

def check_dns(hostname: str, record_type: str = 'A', dns_server: list = None) -> tuple[bool, int]:
    resolver = dns.resolver.Resolver()
    resolver.nameservers = dns_server or ['8.8.8.8', '1.1.1.1']
    try:
        answer = resolver.resolve(hostname, record_type)
        return True, len(answer.rrset.items)

    except dns.resolver.NXDOMAIN:
        # logger.error(f"The domain {hostname} does not exist.")
        return False, -1

    except dns.resolver.Timeout:
        # logger.error(f"Query timed out when resolving {hostname} with DNS server {resolver.nameservers}.")
        return False, -2

    except dns.resolver.NoNameservers:
        # logger.error(f"No nameservers are available to resolve {hostname} with DNS server {resolver.nameservers}.")
        return False, -3

    except dns.exception.DNSException as e:
        # logger.error(f"An error occurred: {e}")
        return False, -10
