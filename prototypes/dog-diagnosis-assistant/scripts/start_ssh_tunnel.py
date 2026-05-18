import os
import time
import socket
import select
import threading
import paramiko


def forward_tunnel(local_port, remote_host, remote_port, transport):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", int(local_port)))
        sock.listen(5)
        while True:
            client_socket, addr = sock.accept()
            threading.Thread(
                target=handle_forward,
                args=(client_socket, remote_host, int(remote_port), transport),
                daemon=True,
            ).start()


def handle_forward(client_socket, remote_host, remote_port, transport):
    try:
        chan = transport.open_channel(
            "direct-tcpip",
            (remote_host, remote_port),
            client_socket.getpeername(),
        )
        while True:
            r, _, _ = select.select([client_socket, chan], [], [])
            if client_socket in r:
                data = client_socket.recv(1024)
                if not data:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if not data:
                    break
                client_socket.send(data)
    finally:
        client_socket.close()
        try:
            chan.close()
        except Exception:
            pass


def start_tunnel():
    required = [
        "SSH_HOST", "SSH_PORT", "SSH_USERNAME", "SSH_PASSWORD",
        "LOCAL_PORT", "REMOTE_HOST", "REMOTE_PORT"
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        os.getenv("SSH_HOST"),
        port=int(os.getenv("SSH_PORT")),
        username=os.getenv("SSH_USERNAME"),
        password=os.getenv("SSH_PASSWORD"),
    )
    transport = client.get_transport()
    print("SSH tunnel started.")
    forward_tunnel(
        int(os.getenv("LOCAL_PORT")),
        os.getenv("REMOTE_HOST"),
        int(os.getenv("REMOTE_PORT")),
        transport,
    )


if __name__ == "__main__":
    try:
        start_tunnel()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("SSH tunnel closed.")
