#!/usr/bin/python3 

import socket
import os
import json
import requests
import base64
import re
import threading
import select
import logging  # Use logging module

# Configuration
SYSLOG_HOST = '0.0.0.0'
SYSLOG_UDP_PORT = 514
SYSLOG_TCP_PORT = 514
OPENOBSERVE_URL = os.getenv("OPENOBSERVE_URL", 'http://192.168.1.201:5080/api/default/gpon_logs/_json') # Provide default if not in .env
USERNAME = os.getenv("USERNAME", 'support@ksginfrasolutions.com') # Provide default if not in .env
PASSWORD = os.getenv("PASSWORD", 'randomPassword') # Provide default if not in .env
VERIFY_SSL = False

# Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s') #Added logging
logger = logging.getLogger(__name__)

# Function to Convert Severity to Text
def severity_to_text(severity):
    severity_levels = {
        0: 'emerg',
        1: 'alert',
        2: 'crit',
        3: 'err',
        4: 'warning',
        5: 'notice',
        6: 'info',
        7: 'debug'
    }
    return severity_levels.get(severity, 'unknown')

# Authentication Headers
auth_string = f'{USERNAME}:{PASSWORD}'
auth_bytes = auth_string.encode('utf-8')
auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {auth_base64}'
}

# Regular expression for parsing syslog messages
SYSLOG_REGEX_COMMON = re.compile(
    r'<\d+>(?P<timestamp>\w+ \d+ \d+:\d+:\d+) (?P<hostname>[^\s]+) (?P<program>[^:]+): (?P<message>.+)'
)

# Function to handle a single TCP connection
def handle_tcp_connection(conn, address):
    try:
        logger.info(f'New TCP connection from {address[0]}:{address[1]}') #Logging library

        while True:
            data = conn.recv(4096)
            if not data:
                break  # Connection closed

            message = data.decode('utf-8').strip()
            # Removed local debug logging
            try:
                match = SYSLOG_REGEX_COMMON.match(message)
                if match:
                    syslog_data = match.groupdict()
                    timestamp = syslog_data.get('timestamp', '')
                    hostname = syslog_data.get('hostname', '')
                    program = syslog_data.get('program', '')
                    log_message = syslog_data.get('message', '')

                    priority = int(message[1:].split('>', 1)[0])
                    facility = priority // 8
                    severity = priority % 8
                    payload = {
                        'level': severity_to_text(severity),
                        'job': program if program else hostname,
                        'message': log_message,
                        'hostname': hostname,
                        'facility': facility,
                        'device_type':'PON'
                    }

                    json_payload = json.dumps([payload])

                    try:
                        response = requests.post(OPENOBSERVE_URL, data=json_payload, headers=headers, verify=VERIFY_SSL)
                        response.raise_for_status()
                        logger.info(f'Forwarded TCP message from {address[0]}:{address[1]}') #Logging
                    except requests.exceptions.RequestException as e:
                        logger.error(f'Error sending TCP message to OpenObserve: {e}') # Logging
                else:
                   logger.warning(f'Could not parse TCP syslog message: {message}') #Logging

            except Exception as e:
                logger.error(f'Error processing TCP syslog message: {e}')  # Logging

    except Exception as e:
        logger.error(f'Error handling TCP connection: {e}') # Logging
    finally:
        conn.close()
        logger.info(f'TCP connection from {address[0]}:{address[1]} closed.') #Logging

# Create a UDP socket
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_address = (SYSLOG_HOST, SYSLOG_UDP_PORT)
udp_sock.bind(udp_server_address)
logger.info(f'Listening for syslog messages on UDP {SYSLOG_HOST}:{SYSLOG_UDP_PORT}') #Logging
# Create a TCP socket
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_address = (SYSLOG_HOST, SYSLOG_TCP_PORT)
tcp_sock.bind(tcp_server_address)
tcp_sock.listen(5)  # Listen for incoming connections (backlog of 5)
logger.info(f'Listening for syslog messages on TCP {SYSLOG_HOST}:{SYSLOG_TCP_PORT}') #Logging
#
try:
    while True:
        # Use select to listen on both UDP and TCP sockets
        rlist, _, _ = select.select([udp_sock, tcp_sock], [], []) # Use select module

        for ready_socket in rlist:
            if ready_socket is udp_sock: # If the socket is the UDP
                data, address = udp_sock.recvfrom(4096) # Standard UDP code from previous posts.
                message = data.decode('utf-8').strip()

                try:
                    match = SYSLOG_REGEX_COMMON.match(message)
                    if match:
                        syslog_data = match.groupdict()
                        timestamp = syslog_data.get('timestamp', '')
                        hostname = syslog_data.get('hostname', '')
                        program = syslog_data.get('program', '')
                        log_message = syslog_data.get('message', '')

                        priority = int(message[1:].split('>', 1)[0])
                        facility = priority // 8
                        severity = priority % 8

                        payload = {
                            'level': severity_to_text(severity),
                            'job': program if program else hostname,
                            'message': log_message,
                            'hostname': hostname,
                            'facility': facility,
                            'device_type':'PON'
                        }

                        json_payload = json.dumps([payload])

                        try:
                            response = requests.post(OPENOBSERVE_URL, data=json_payload, headers=headers, verify=VERIFY_SSL)
                            response.raise_for_status()
                            logger.info(f'Forwarded UDP message from {address[0]}:{address[1]}') #Logging
                        except requests.exceptions.RequestException as e:
                            logger.error(f'Error sending UDP message to OpenObserve: {e}') #Logging
                    else:
                        logger.warning(f'Could not parse UDP syslog message: {message}') #Logging

                except Exception as e:
                    logger.error(f'Error processing UDP syslog message: {e}')  # Logging

            elif ready_socket is tcp_sock: # If the socket is the TCP
                conn, address = tcp_sock.accept()
                thread = threading.Thread(target=handle_tcp_connection, args=(conn, address))
                thread.daemon = True # Make sure it doesn't block the program from exiting
                thread.start()


except KeyboardInterrupt:
    print('Exiting.')

finally:
    udp_sock.close()
    tcp_sock.close()



