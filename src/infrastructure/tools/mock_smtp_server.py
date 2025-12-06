import socket
import sys
import threading
import os
import time
from datetime import datetime

OUTPUT_DIR = "sent_emails"

def save_email(data):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"email_{timestamp}.eml"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(data)
        f.write(b"\r\n")
    
    print(f"\n[+] Email saved to: {filepath}")
    print(f"    You can open this file with your email client (Thunderbird, Outlook, Mail, etc.) to view it graphically.")

def handle_client(client_socket, addr):
    print(f"Connection from {addr}")
    try:
        client_socket.send(b"220 localhost Mock SMTP Server\r\n")
        
        buffer = b""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            
            buffer += data
            
            while b"\r\n" in buffer:
                if b"\r\n" in buffer:
                    line_end = buffer.find(b"\r\n")
                    line = buffer[:line_end]
                    
                    text = line.decode('utf-8', errors='ignore')
                    cmd = text.upper().split(' ')[0]
                    
                    if cmd == "DATA":
                        print(f"< {text}")
                        client_socket.send(b"354 Start mail input; end with <CRLF>.<CRLF>\r\n")
                        buffer = buffer[line_end+2:]
                        
                        while b"\r\n.\r\n" not in buffer:
                            more = client_socket.recv(4096)
                            if not more:
                                return 
                            buffer += more
                            
                            if len(buffer) > 10 * 1024 * 1024:
                                print("Error: Message too large for mock server")
                                return

                        end_marker = buffer.find(b"\r\n.\r\n")
                        data_content = buffer[:end_marker]
                        buffer = buffer[end_marker+5:] 
                        
                        print(f"(Received {len(data_content)} bytes of data)")
                        save_email(data_content)
                        client_socket.send(b"250 OK\r\n")
                        continue
                    
                    buffer = buffer[line_end+2:] 
                    
                    if cmd in ["EHLO", "HELO"]:
                        client_socket.send(b"250-localhost\r\n250 OK\r\n")
                    elif cmd == "MAIL":
                        client_socket.send(b"250 OK\r\n")
                    elif cmd == "RCPT":
                        client_socket.send(b"250 OK\r\n")
                    elif cmd == "QUIT":
                        client_socket.send(b"221 Bye\r\n")
                        return
                    elif cmd == "RSET":
                        client_socket.send(b"250 OK\r\n")
                    elif cmd == "NOOP":
                        client_socket.send(b"250 OK\r\n")
                    else:
                        client_socket.send(b"250 OK\r\n")

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()


def run_server(port=1025):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('localhost', port))
        server_socket.listen(5)
        print(f"Mock SMTP Server running on localhost:{port}")
        print(f"Emails will be saved to '{OUTPUT_DIR}' directory.")
        print("Press Ctrl+C to stop.")

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        try:
            server_socket.close()
        except:
            pass

if __name__ == "__main__":
    run_server()
