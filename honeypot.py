import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading

LOGGING_FORMAT = logging.Formatter('%(message)s')
SSH_BANNER = "SSH-2.0-OpenSSH_1.0"
HOST_KEY = paramiko.RSAKey(filename="Server.key")

funnel_logger = logging.getLogger("funnellogger")
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler("audits.log", maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(LOGGING_FORMAT)
funnel_logger.addHandler(funnel_handler)

creds_logger = logging.getLogger("credslogger")
creds_logger.setLevel(logging.INFO)
ch = RotatingFileHandler("cmd_audits.log", maxBytes=2000, backupCount=5)
ch.setFormatter(LOGGING_FORMAT)
creds_logger.addHandler(ch)


class HoneypotServer(paramiko.ServerInterface):
    def __init__(self, client_ip, username, password):
        self.client_ip = client_ip
        self.username = username
        self.password = password
        self.pty_event = threading.Event()
        self.shell_event = threading.Event()

    
    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client IP: {self.client_ip} - Attempted login with Username: "{username}" and Password: "{password}"')
        creds_logger.info(f'Client IP: {self.client_ip} - Attempted login with Username: "{username}" and Password: "{password}"')
        funnel_logger.info(f"Login attempt {username}:{password} from {self.client_ip}")
        if username == self.username and password == self.password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    

    
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        self.pty_event.set()
        return True

    def check_channel_shell_request(self, channel):
        self.shell_event.set()
        return True


def emulated_shell(channel, client_ip):
    channel.send(b"corporate-jumpbox2$ ")
    command = b""

    while True:
        char = channel.recv(1)
        if not char:
            break

        channel.send(char)
        command += char

        if char == b"\r":
            cmd = command.strip().lower()

            if cmd == b"exit":
                channel.send(b"logout\r\n")
                break
            elif cmd == b"pwd":
                response = b"/usr/local\r\n"
                creds_logger.info(f'Command {cmd}' + 'executed by' + f'{client_ip}')
            elif cmd == b"whoami":
                response = b"corpuser1\r\n"
                creds_logger.info(f'Command {cmd}' + 'executed by' + f'{client_ip}')
            elif cmd == b"ls":
                response = b"jumpbox.conf\r\n"
                creds_logger.info(f'Command {cmd}' + 'executed by' + f'{client_ip}')
            elif cmd == b"cat jumpbox.conf":
                response = b"Go to Google.com\r\n"
                creds_logger.info(f'Command {cmd}' + 'executed by' + f'{client_ip}')    
            else:
                response = cmd + b"\r\n"

            creds_logger.info(f"Command {cmd.decode(errors='ignore')} {client_ip}")
            channel.send(b"\n" + response)
            channel.send(b"corporate-jumpbox2$ ")
            command = b""


def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"[+] Connection from {client_ip}")

    transport = paramiko.Transport(client)
    transport.local_version = SSH_BANNER
    transport.add_server_key(HOST_KEY)

    server = HoneypotServer(client_ip, username, password)
    transport.start_server(server=server)

    channel = transport.accept(20)
    if channel is None:
        transport.close()
        return

    if not server.pty_event.wait(10):
        channel.close()
        transport.close()
        return

    if not server.shell_event.wait(10):
        channel.close()
        transport.close()
        return

    channel.send(b"Welcome to Corporate Jumpbox 2.0\r\n")
    emulated_shell(channel, client_ip)

    channel.close()
    transport.close()


def honeypot(host, port, username, password):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)

    print(f"[+] Honeypot listening on {host}:{port}")

    while True:
        client, addr = sock.accept()
        threading.Thread(
            target=client_handle,
            args=(client, addr, username, password),
            daemon=True,
        ).start()


honeypot("0.0.0.0", 5501, "username", "password")