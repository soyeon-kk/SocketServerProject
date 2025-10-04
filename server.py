import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # 버퍼 크기 설정
        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)
        
        # 응답 파일 읽기
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def save_request(self, data):
        """클라이언트 요청 데이터를 request 폴더에 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = f"{self.DIR_PATH}/{timestamp}.bin"
        with open(filename, 'wb') as f:
            f.write(data)
        print(f"Saved request data to {filename}")
        return filename

    def save_image(self, data, image_name="uploaded_image.jpg"):
        """멀티파트로 전송된 이미지 데이터를 별도 파일로 저장"""
        image_path = os.path.join(self.DIR_PATH, image_name)
        with open(image_path, 'wb') as f:
            f.write(data)
        print(f"Saved image to {image_path}")
        return image_path

    def run(self, ip, port):
        """서버 실행"""
        # 소켓 생성
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:
                # 클라이언트 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)  # 타임아웃 설정(5초)
                print("Request message...\r\n")

                request_data = b""
                while True:
                    try:
                        chunk = clnt_sock.recv(self.bufsize)
                        if not chunk:
                            break
                        request_data += chunk
                    except socket.timeout:
                        break

                # 요청 저장
                self.save_request(request_data)

                # 간단히 멀티파트에서 이미지 데이터 추출 (실제는 HTTP 파싱 필요)
                if b'Content-Type: image' in request_data:
                    start = request_data.find(b'\r\n\r\n') + 4
                    self.save_image(request_data[start:], "uploaded_image.jpg")

                # 응답 전송
                clnt_sock.sendall(self.RESPONSE)

                # 클라이언트 소켓 닫기
                clnt_sock.close()

        except KeyboardInterrupt:
            print("\r\nStop the server...")
            self.sock.close()


if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
