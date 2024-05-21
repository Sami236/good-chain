import os
import pickle
from Checkchain import CheckChain
import sqlite3
from hashfiles import check_blockchain_integrity
clear = lambda: os.system('cls')
class BlockInfo:

    def __init__(self):
        self.check_chain = CheckChain()

    def get_block_info(self):
        clear()
        check_blockchain_integrity()
        with open(os.path.join('./data', 'blockchain.dat'), "rb") as loadfile:
            try:
                pickle.load(loadfile)
            except EOFError:
                print("Blockchain is empty.")
                input("Press [ENTER] to return to the main menu.")
                return
        
        block_id = input("Block ID: ")
        if not block_id.isdigit():
            print("Invalid block ID. Please enter a number.")
            input("Press [ENTER] to return to the main menu.")
            return
        else:
            block_id = int(block_id)
        
        filepath = os.path.join('./data', 'blockchain.dat')
        with open(filepath, "rb") as loadfile:
            try:
                blockchain = pickle.load(loadfile)
                for block in blockchain:
                    if block.block_id == block_id:
                        print("\nBlock Information:")
                        print("====================")
                        self.print_block_info_with_usernames(block)
                        print("\nTransactions:")
                        print("====================")
                        for tx in block.data:
                            self.print_transaction_with_username(tx)
                        print("====================\n")
                        input("\nPress [ENTER] to return to the main menu.")
                        return
                print(f"Block with ID {block_id} not found in the blockchain.")
                input("Press [ENTER] to return to the main menu.")
                return
            except EOFError:
                print("Blockchain is empty")

    def print_block_info_with_usernames(self, block):
        print("Block ID:", block.block_id)
        print("Previous Block Hash:", block.previousHash)
        print("Miner:", block.miner)
        print("Timestamp:", block.timestamp)
        print("Nonce:", block.nonce)
        print("Validity:", block.validity)
        print("Is Valid:", block.isvalid)
        print("Block Hash:", block.blockHash)
        print("====================")

    def print_transaction_with_username(self, transaction):
        print("Inputs:")
        for addr, amt in transaction.inputs:
            username = self.get_username_from_public_key(addr)
            print(str(amt) + " from " + username + "\n")
        print("Outputs:")
        for addr, amt in transaction.outputs:
            username = self.get_username_from_public_key(addr)
            print(str(amt) + " to " + username + "\n")
        print("Signature:")
        for s in transaction.sigs:
            print(str(s) + "\n")
        print("Validity:", transaction.validtx)
        print("Fee:", transaction.fee)
        print("====================\n")

    def get_username_from_public_key(self, public_key):
        # Check for special system usernames
        if public_key == "SYSTEM_SIGNUP_REWARD":
            return "System Signup Reward"
        elif public_key == "SYSTEM_MINING_FEE":
            return "System Mining Fee"

        # For regular public keys, query the database
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE public_key=?", (public_key,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
        else:
            return "Unknown"  # If no username found for the public key

if __name__ == '__main__':
    block_info = BlockInfo()
    block_info.get_block_info()
