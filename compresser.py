import heapq
from collections import Counter

class _HuffmanNode:
    def __init__(self, byte=None, freq=None, left=None, right=None):
        self.byte = byte
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq
    
class Compresser:
    def compress(self, bytes):
        self.frequency = Counter(bytes)
        self.huffman_tree = self._build_huffman_tree()
        self.codebook = self._generate_huffman_codes(self.huffman_tree)
        encoded_bytes = self._huffman_encode(bytes)
        return encoded_bytes
    
    def decompress(self, encoded_bytes):
        return self._huffman_decode(encoded_bytes)
    
    def compute_compression_ratio(self, original_data, encoded_data):
        original_size_in_bits = len(original_data) * 8
        encoded_size_in_bits = len(encoded_data)
        compression_ratio = original_size_in_bits / encoded_size_in_bits if encoded_size_in_bits != 0 else float('inf')
        # compression_percentage = 100 * (1 - (encoded_size_in_bits / original_size_in_bits)) if original_size_in_bits != 0 else 0
        return compression_ratio

    def _build_huffman_tree(self):
        heap = [_HuffmanNode(byte, freq) for byte, freq in self.frequency.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            merged = _HuffmanNode(None, node1.freq + node2.freq, node1, node2)
            heapq.heappush(heap, merged)
        return heap[0]

    def _generate_huffman_codes(self, tree: _HuffmanNode, prefix="", codebook=None):
        if codebook is None:
            codebook = {}
        if tree.byte is not None:
            codebook[tree.byte] = prefix
        else:
            self._generate_huffman_codes(tree.left, prefix + "0", codebook)
            self._generate_huffman_codes(tree.right, prefix + "1", codebook)
        return codebook

    def _serialize_huffman_tree(self, node):
        if node is None:
            return ""
        if node.byte is not None:
            return f"1{chr(node.byte)}"
        return f"0{self._serialize_huffman_tree(node.left)}{self._serialize_huffman_tree(node.right)}"

    def _deserialize_huffman_tree(self, data, index=0):
        def helper(index):
            if data[index] == '1': # Leaf node
                byte = ord(data[index + 1])
                return _HuffmanNode(byte=byte), index + 2
            elif data[index] == '0': # Internal node
                left_child, next_index = helper(index + 1)
                right_child, next_index = helper(next_index)
                return _HuffmanNode(left=left_child, right=right_child), next_index
        root, next_index = helper(index)
        return root, next_index

    def _huffman_encode(self, data):
        serialized_tree = self._serialize_huffman_tree(self.huffman_tree)
        encoded_data = ''.join(self.codebook[byte] for byte in data)
        return serialized_tree + encoded_data

    def _huffman_decode(self, encoded_data):
        huffman_tree, offset = self._deserialize_huffman_tree(encoded_data, index=0)
        encoded_bits = encoded_data[offset:]
        return self._huffman_decode_bits(encoded_bits, huffman_tree)

    def _huffman_decode_bits(self, encoded_data, tree):
        decoded_bytes = []
        node = tree
        for bit in encoded_data:
            if bit == '0':
                node = node.left
            else:
                node = node.right
            if node.byte is not None:
                decoded_bytes.append(node.byte)
                node = tree
        return bytes(decoded_bytes)