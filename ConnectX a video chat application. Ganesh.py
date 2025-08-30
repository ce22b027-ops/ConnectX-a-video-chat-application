import socket
import cv2
import pickle
import struct

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = socket.gethostbyname(socket.gethostname())
port = 12345
socket_address = (host_ip, port)

print(f"[ConnectX Host] Starting server at {host_ip}:{port}")
server_socket.bind(socket_address)
server_socket.listen(1)

print("[ConnectX Host] Waiting for a connection...")
conn, addr = server_socket.accept()
print(f"[ConnectX Host] Connected to {addr}")

# Start webcam
cap = cv2.VideoCapture(0)

try:
    while True:
        # Capture and send frame
        ret, frame = cap.read()
        if not ret:
            break

        data = pickle.dumps(frame)
        message = struct.pack("Q", len(data)) + data
        conn.sendall(message)

        # Receive frame from client
        data = b""
        payload_size = struct.calcsize("Q")

        while len(data) < payload_size:
            data += conn.recv(4)

        packed_msg_size = data[:payload_size]
        msg_size = struct.unpack("Q", packed_msg_size)[0]
        data = data[payload_size:]

        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        client_frame = pickle.loads(frame_data)

        cv2.imshow("Client Camera", client_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print("[ERROR]", e)

finally:
    cap.release()
    conn.close()
    server_socket.close()
    cv2.destroyAllWindows()
    print("[ConnectX Host] Connection closed.")
