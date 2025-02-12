import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = 4096

def handle_client(client_socket, client_address):
    """Handles a single client connection."""
    print(f"Handling connection from {client_address}")
    client_socket.settimeout(5)  # Set a timeout for client responses
    data = b""

    try:
        while True:
            chunk = client_socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            data += chunk
            print(data)
            time.sleep(7)

            # Split data by double CRLF to handle multiple requests (pipelining)
            requests = data.split(b"\r\n\r\n")
            data = requests.pop()  # Keep incomplete request for the next iteration

            for request in requests:
                response = handle_request(request.decode('utf-8'))
                client_socket.sendall(response.encode('utf-8'))

    except socket.timeout:
        print(f"Connection to {client_address} timed out.")
    finally:
        print(f"Closing connection to {client_address}")
        client_socket.close()

def handle_request(request):
    """Parses the HTTP request and generates a response."""
    lines = request.split('\r\n')
    request_line = lines[0]
    method, path, _ = request_line.split()

    if method != 'GET':
        return generate_response(405, "Method Not Allowed")

    if path == '/':
        body = "Hello! This is a simple multi-threaded HTTP/1.1 server."
        return generate_response(200, body)
    else:
        body = "404 Not Found: The requested resource does not exist."
        return generate_response(404, body)

def generate_response(status_code, body):
    """Generates a basic HTTP response with the given status code and body."""
    reason_phrases = {
        200: "OK",
        404: "Not Found",
        405: "Method Not Allowed"
    }
    reason = reason_phrases.get(status_code, "Unknown Status")

    response = (
        f"HTTP/1.1 {status_code} {reason}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: keep-alive\r\n"
        f"\r\n"
        f"{body}"
    )
    return response

def run_server():
    """Runs a multi-threaded HTTP/1.1 server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Serving HTTP on {HOST} port {PORT} (http://{HOST}:{PORT}/) ...")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

if __name__ == "__main__":
    run_server()

