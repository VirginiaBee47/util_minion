BASE_52 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def hash(inp: str) -> int:
    """Generates a hash for the input string."""
    hash_value = 0
    for char in inp:
        hash_value = (hash_value * 52 + BASE_52.index(char)) % (2**64)
    return hash_value
    