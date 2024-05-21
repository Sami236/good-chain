import hashlib
import os
import pickle
import time

def generate_hash(file_path):
    """Generate a SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read()  # Read the file in chunks to conserve memory
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def check_integrity(file_path, stored_hash):
    """Check if the current hash of the file matches the stored hash."""
    current_hash = generate_hash(file_path)
    return current_hash == stored_hash

def update_file_hashes(type, db_path):
    db_hash = generate_hash(db_path)
    filehashes_path = os.path.join('./data', 'filehashes.dat')
    if os.path.exists(filehashes_path):
        with open(filehashes_path, 'rb') as file:
            file_hashes = pickle.load(file)
            
        file_hashes[type] = db_hash
        with open(filehashes_path, 'wb') as file:
            pickle.dump(file_hashes, file)
    else:
        print("Error: filehashes.dat not found.")

def load_file_hash_blockchain():
    filehashes_path = os.path.join('./data', 'filehashes.dat')
    if os.path.exists(filehashes_path):
        with open(filehashes_path, 'rb') as file:
            for(key, value) in pickle.load(file).items():
                if key == 'blockchain':
                    filehash = value
    return filehash

    
def check_blockchain_integrity():
        loadedhash = load_file_hash_blockchain()
        blockchain_file_path = os.path.join('./data', 'blockchain.dat')

        # Generate current hashes
        current_hash = {
            'blockchain': generate_hash(blockchain_file_path)
        }

        # Compare current hashes with stored hashes
        if current_hash['blockchain'] != loadedhash:
   
            print(f"Integrity check failed for blockchain file. Potential tampering detected.")
            print("Exiting...")
            time.sleep(2)
            exit()
            


