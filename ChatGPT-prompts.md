# Create a simple web server that supports http 1.1, keeps the connection alive, and has support for pipelining.

Here’s a Python implementation of a simple HTTP 1.1 web server with persistent connections and support for request pipelining. This server will respond to GET requests and send basic text responses. We’ll use the `socket` library and implement the HTTP 1.1 protocol features.

### Features:
1. **HTTP/1.1 Support**  
2. **Keep-Alive Connections**  
3. **Pipelining** (processing multiple requests in one connection)

Here’s the code:

### Python Code for the Web Server
```python
import socket

HOST = '127.0.0.1'  # localhost
PORT = 8080         # Port to listen on
BUFFER_SIZE = 4096  # Size of each received chunk

def handle_request(request):
    """Parses the HTTP request and generates a response."""
    lines = request.split('\r\n')
    request_line = lines[0]
    method, path, _ = request_line.split()
    
    if method != 'GET':
        return generate_response(405, "Method Not Allowed")
    
    if path == '/':
        body = "Hello! This is a simple HTTP/1.1 server."
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
    """Runs the simple HTTP/1.1 server with keep-alive and pipelining support."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Serving HTTP on {HOST} port {PORT} (http://{HOST}:{PORT}/) ...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            with client_socket:
                client_socket.settimeout(5)
                data = b""
                
                try:
                    while True:
                        chunk = client_socket.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                        data += chunk
                        
                        # Handle multiple pipelined requests
                        requests = data.split(b"\r\n\r\n")
                        data = requests.pop()  # Keep the incomplete request for the next iteration
                        
                        for request in requests:
                            response = handle_request(request.decode('utf-8'))
                            client_socket.sendall(response.encode('utf-8'))
                
                except socket.timeout:
                    print(f"Connection to {client_address} timed out.")
                print(f"Closing connection to {client_address}")

if __name__ == "__main__":
    run_server()
```

---

### How it Works:
- **Server Basics**: Listens on `127.0.0.1:8080` and accepts incoming connections.
- **Request Handling**: Supports only the `GET` method for now.
- **Persistent Connections**: Uses the `Connection: keep-alive` header to keep the connection open.
- **Pipelining**: The server handles multiple requests in a single connection by parsing and responding to each request individually.

---

### How to Test:
1. **Run the server**:  
   Save the code in a file (e.g., `server.py`) and run it:
   ```bash
   python server.py
   ```
2. **Send HTTP requests**:  
   Use a tool like `curl` to test pipelining:
   ```bash
   curl -v --http1.1 --keepalive http://127.0.0.1:8080/
   ```
   Or you can send multiple requests in one connection:
   ```bash
   curl -v --http1.1 --keepalive --request GET http://127.0.0.1:8080/ --next --request GET http://127.0.0.1:8080/notfound
   ```

---

Want me to extend this with **file handling**, **multi-threading**, or **SSL support**? 😊
