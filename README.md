# Compress ECG byte

## Instructions

After downloading the source code, ensure you have Python and Python Flask installed. 
Then, run `python main.py` and navigate to `localhost:8888`.

## Design Considerations and Key Decisions

- 

## Compression Algorithm 

I chose to go with a simple Huffman Coding algorithm

## 

After doing some initial research, I learned there's no 1 standardized format for ECG files.
So there's nothing special we can do in terms of optimizing our compression algorithm for specific headers, special data structures, etc.
So I figured I should treat the entire file with characters being 24 bits (3 bytes) each.

I chose to go with Huffman coding since it was the most common file format.
After compressing, we need information about which code is assigned to which 3 bytes in order to reconstruct the original file.
This requires storing some extra information in the header/front of the compressed file so that we can reliably reconstruct the original file.

Although it isn't explicity stated as part of the requirements, we should ensure that our compressed file can be decompressed into the original file.
This functionality doesn't necessarily need to be available in the Web UI for users to decompress their file.