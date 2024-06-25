#!/usr/bin/env python3

import heapq

import uuid
import os
import shutil

from flask import Flask, current_app, request, Response, send_file
app = Flask(__name__)

INPUT_DIR = "./input/"
OUTPUT_DIR = "./output/"

def init():
    if os.path.exists(INPUT_DIR):
        shutil.rmtree(INPUT_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.mkdir(INPUT_DIR)
    os.mkdir(OUTPUT_DIR)

def main():
    init()
    app.run(host="0.0.0.0", debug=False, port=8888)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
COMPRESSION
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class CompressionInfo():
    def __init__(self, file_id: str, input_size: int, output_size: int):
        self.file_id = file_id
        self.input_size = input_size
        self.output_size = output_size

def save_file(file) -> str:
    """Save FILE and return its corresponding ID"""
    file_id = uuid.uuid4()
    file.save(get_input_path(file_id))
    return file_id

def compress(file_id: str):
    """Compress file corresponding to FILE_ID"""
    input_path = get_input_path(file_id)
    output_path = get_output_path(file_id)

    compress_file(input_path, output_path)

def get_compression_info(file_id: str) -> CompressionInfo:
    """Retrieve information about size of input and output file for FILE_ID"""
    input_path = get_input_path(file_id)
    output_path = get_output_path(file_id)

    input_size = os.path.getsize(input_path)
    output_size = os.path.getsize(output_path)

    return CompressionInfo(file_id, input_size, output_size)

def cleanup(file_id: str):
    """Clean up any files created relating to FILE_ID"""
    input_path = get_input_path(file_id)
    output_path = get_output_path(file_id)

    os.remove(input_path)
    os.remove(output_path)


def get_input_path(file_id) -> str:
    return f"{INPUT_DIR}/{file_id}"

def get_output_path(file_id) -> str:
    return f"{OUTPUT_DIR}/{file_id}"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
FLASK REST API
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

@app.route("/", methods=["GET"])
def index():
    return current_app.send_static_file('index.html')

@app.route("/api/accept_file", methods=["POST"])
def accept_file():
    if 'file' not in request.files:
        return "File required", 400

    file_id = save_file(request.files['file'])
    compress(file_id)
    compression_info = get_compression_info(file_id)

    response = {
        "file_id": compression_info.file_id,
        "original_size": compression_info.input_size,
        "compressed_size": compression_info.output_size
    }
    return response, 200

@app.route("/api/download_file/<file_id>", methods=["GET"])
def download_file(file_id):
    return send_file(get_output_path(file_id))

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
HUFFMAN CODING
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class TreeNode:
    def __init__(self, byte, count, left = None, right = None):
        self.byte = byte
        self.count = count
        self.left = left
        self.right = right
    
    def __lt__(self, nxt):
        return self.count < nxt.count

    def __repr__(self):
        return f"{self.byte} [{self.left}_{self.right}]"

def get_codes(input_file: str) -> dict[str, str]:
    """
    Given INPUT_FILE, read its contents and return a dictionary containing a code for each byte
    Uses Huffman coding
    """
    # Get frequency of every byte in the file
    char_count = {}
    for i in range(256):
        key = i.to_bytes(1, 'big')
        char_count[key] = 0

    with open(input_file, "rb") as file:
        byte = file.read(1)
        while byte != b"":
            char_count[byte] += 1
            byte = file.read(1)

    # Create the initial heap
    char_queue = []
    for byte, count in char_count.items():
        heapq.heappush(char_queue, TreeNode(byte, count))

    # Create the tree
    while len(char_queue) > 1:
        left = heapq.heappop(char_queue)
        right = heapq.heappop(char_queue)
        new_node = TreeNode(None, left.count + right.count, left, right)
        heapq.heappush(char_queue, new_node)

    codes = {} # {byte: code}
    queue = [(char_queue[0], '')] # (TreeNode, code)
    while queue:
        node, code = queue.pop()

        if not node.left and not node.right:
            codes[node.byte] = code
            continue

        if node.left:
            queue.append((node.left, code + '0'))
        if node.right:
            queue.append((node.right, code + '1'))
    return codes

def to_bytes(data):
    """
    Helper function to convert DATA to valid bytes
    """
    b = bytearray()
    for i in range(0, len(data), 8):
        b.append(int(data[i:i+8], 2))
    return bytes(b)

def write_compressed_file(input_file: str, output_file: str, codes: dict[str, str]):
    """
    Compress contents of INPUT_FILE to OUTPUT_FILE using CODES
    """
    with open(input_file, "rb") as input_file:
        data_str = ""
        byte = input_file.read(1)
        while byte != b"":
            data_str += codes[byte]
            byte = input_file.read(1)
        data_bytes = to_bytes(data_str)

    with open(output_file, "wb") as output_file:
        output_file.write(data_bytes)

def compress_file(input_file: str, output_file: str):
    """
    Compress contents of INPUT_FILE and save to OUTPUT_FILE
    """
    codes = get_codes(input_file)
    write_compressed_file(input_file, output_file, codes)

if __name__ == "__main__":
    main()