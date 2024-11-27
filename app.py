import hashlib
import ecdsa
import time
import base58
from tqdm import tqdm
from bitcoin import encode_privkey
import os
import signal

# Target Public Key Hash (Hash160) and Bitcoin address
target_public_key_hash = "739437bb3dd6d1983e66629c5f08c70e52769371"
target_address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"

# Define the start and end range for private keys (in hexadecimal format)
start_range = 0x70000000000ca4a5c  # Start range (integer form)
end_range = 0x7ffffffffffffffff  # End range (integer form)

# File to store the last searched private key
progress_file = "/tmp/search_progress.txt"  # Use a temp directory for compatibility with Render

def generate_public_key_hash(public_key_hex):
    sha256 = hashlib.sha256(bytes.fromhex(public_key_hex)).digest()
    public_key_hash = hashlib.new('ripemd160', sha256).hexdigest()
    return public_key_hash

def generate_btc_address(public_key_hex):
    try:
        public_key_bytes = bytes.fromhex(public_key_hex)
        sha256 = hashlib.sha256(public_key_bytes).digest()
        ripemd160 = hashlib.new('ripemd160', sha256).digest()
        network_prefix = b'\x00'
        extended_key = network_prefix + ripemd160
        checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
        address_bytes = extended_key + checksum
        address = base58.b58encode(address_bytes).decode('utf-8')
        return address
    except Exception as e:
        print(f"Error generating Bitcoin address: {e}")
        return None

def check_private_key(private_key):
    private_key_hex = hex(private_key)[2:].zfill(64)
    try:
        sk = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)
        generated_public_key = sk.get_verifying_key().to_string('compressed').hex()
        generated_public_key_hash = generate_public_key_hash(generated_public_key)
        if generated_public_key_hash == target_public_key_hash:
            generated_address = generate_btc_address(generated_public_key)
            if generated_address == target_address:
                wif_private_key = encode_privkey(private_key, 'wif')
                with open('/tmp/found.txt', 'w') as f:  # Save to a temp directory
                    f.write(f"Private Key (Hex): {private_key_hex}\n")
                    f.write(f"Public Key: {generated_public_key}\n")
                    f.write(f"Address: {generated_address}\n")
                    f.write(f"WIF Private Key: {wif_private_key}\n")
                return private_key_hex, generated_public_key, generated_address, wif_private_key
    except Exception as e:
        print(f"Error checking private key: {e}")
        return None

def load_progress():
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            try:
                last_private_key = int(f.read().strip(), 16)
                return last_private_key
            except ValueError:
                return start_range
    else:
        return start_range

def save_progress(private_key):
    with open(progress_file, 'w') as f:
        f.write(hex(private_key)[2:].zfill(64))

def handle_exit_signal(signum, frame):
    print("\nInterrupt received. Saving progress...")
    save_progress(current_private_key)
    exit(0)

def search_private_key_forward():
    global current_private_key
    key_found = False
    start_time = time.time()

    last_private_key = load_progress()
    print(f"Resuming search from private key: {hex(last_private_key)}")

    progress_bar = tqdm(total=end_range - last_private_key + 1, desc="Searching Private Keys", ncols=100)

    for private_key in range(last_private_key, end_range + 1):
        current_private_key = private_key
        result = check_private_key(private_key)
        progress_bar.update(1)

        if private_key % 100000 == 0:
            save_progress(private_key)

        if result:
            print(f"Private Key (Hex): {result[0]}")
            print(f"Public Key: {result[1]}")
            print(f"Address: {result[2]}")
            print(f"WIF Private Key: {result[3]}")
            key_found = True
            break

    progress_bar.close()

    if not key_found:
        print(f"No matching private key was found in the given range. Search completed.")
    else:
        print(f"Search completed.")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTSTP, handle_exit_signal)

    print("Starting the forward search...")
    search_private_key_forward()
