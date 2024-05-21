from blockchain import *
import pickle
import os
import sqlite3

from hashfiles import update_file_hashes, check_blockchain_integrity

class ValidateBlock:
    def __init__(self):
        pass

    def validate_block(self, username):
        check_blockchain_integrity()
        filepath = os.path.join('./data', 'blockchain.dat')
        try:
            with open(filepath, "rb") as loadfile:
                blockchain = pickle.load(loadfile)
        except (FileNotFoundError, EOFError):
            # If the file doesn't exist or is empty, initialize an empty blockchain
            blockchain = []
            
        for block in blockchain:
            if(username == block.miner):
                continue
            if any(entry.get('username') == username for entry in block.validity.values()):
                continue
            # Count the number of valid entries in the validity dictionary
            valid_count = sum(1 for entry in block.validity.values() if entry.get('valid', False))
            invalid_count = sum(1 for entry in block.validity.values() if not entry.get('valid', False))
            # If there are already 3 valid entries, skip adding more validators
            if valid_count >= 3:
                block.isvalid = True
                continue
            # If there are already 3 invalid entries, skip adding more validators
            if invalid_count >= 3:
                block.isvalid = False
                continue
            
            # Update the validity dictionary with the validation status
            block.validity[len(block.validity)] = {
                "valid": block.is_valid(),
                "username" : username
            }
            # Example: Save the updated blockchain back to the file
            with open(filepath, "wb") as savefile:
                pickle.dump(blockchain, savefile)
            update_file_hashes('blockchain', filepath)
            valid_count = sum(1 for entry in block.validity.values() if entry.get('valid', False))
            if valid_count == 3:
                block.isvalid = True
                with open(filepath, "wb") as savefile:
                    pickle.dump(blockchain, savefile)
                update_file_hashes('blockchain', filepath)
                continue

            invalid_count = sum(1 for entry in block.validity.values() if not entry.get('valid', False))
            if invalid_count == 3:
                block.isvalid = False
                rejection_message = f"Block {block.block_id} has 3 invalid flags, so it has been rejected"
                # Store the rejection message in the database
                with sqlite3.connect('./data/goodchain.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET rejected_block = ? WHERE username = ?", (rejection_message, block.miner))
                    conn.commit()
                update_file_hashes('db','./data/goodchain.db')
                self.return_tx_to_pool(block)
                continue

    def return_tx_to_pool(self, invalid_block):
        pool_path = os.path.join('./data', 'pool.dat')
        try:
            with open(pool_path, "rb") as loadfile:
                pool = pickle.load(loadfile)
        except (FileNotFoundError, EOFError):
            pool = []
        
        for tx in invalid_block.data:
            tx.is_valid()
            if not tx.inputs[0][0] == "SYSTEM_MINING_FEE":
                pool.append(tx)
            

        with open(pool_path, "wb") as savefile:
            pickle.dump(pool, savefile)
        
        update_file_hashes('pool', pool_path)
        #delete the block from the blockchain

        blockchain_path = os.path.join('./data', 'blockchain.dat')
        try:
            with open(blockchain_path, "rb") as loadfile:
                blockchain = pickle.load(loadfile)
        except (FileNotFoundError, EOFError):
            blockchain = []

        for i, block in enumerate(blockchain):
            if block.block_id == invalid_block.block_id:
                del blockchain[i]
                break
            

        with open(blockchain_path, "wb") as savefile:
            pickle.dump(blockchain, savefile)
        
        update_file_hashes('blockchain', blockchain_path)

if __name__ == '__main__':
    validateblock = ValidateBlock()
    validateblock.validate_block()
