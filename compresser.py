import zlib
    
class Compresser:
    def compress(self, bytes_data: bytes) -> bytes:
        return zlib.compress(bytes_data)
    
    def decompress(self, encoded_bytes:bytes) -> bytes:
        return zlib.decompress(encoded_bytes)
    
    def compute_compression_ratio(self, original_data: bytes, encoded_data: bytes):
        original_size = len(original_data)
        encoded_size = len(encoded_data)
        compression_ratio = original_size / encoded_size if encoded_size != 0 else float('inf')
        return compression_ratio