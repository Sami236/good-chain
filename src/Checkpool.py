import pickle
import os
import sqlite3

clear = lambda: os.system('cls')

class Checkpool():
    def PrintPool(self):
        clear()
        filepath = os.path.join('./data', 'pool.dat')
        with open(filepath ,"rb") as loadfile:
            transactions = pickle.load(loadfile)
            print("\nTransaction Details:")
            print("====================")
            for transaction in transactions:
                self.print_transaction_with_username(transaction)
            print("====================\n")
        input("Press [ENTER] to return to the main menu")

    def print_transaction_with_username(self, transaction):
        print("Inputs:")
        for addr, amt in transaction.inputs:
            if addr == "SYSTEM_SIGNUP_REWARD":
                print(str(amt) + " from System Signup Reward\n")
            elif addr == "SYSTEM_MINING_FEE":
                print(str(amt) + " from System Mining Fee\n")
            else:
                username = self.get_username_from_public_key(addr)
                print(str(amt) + " from " + username + "\n")
        print("Outputs:")
        for addr, amt in transaction.outputs:
            if addr == "SYSTEM_SIGNUP_REWARD":
                print(str(amt) + " to System Signup Reward\n")
            elif addr == "SYSTEM_MINING_FEE":
                print(str(amt) + " to System Mining Fee\n")
            else:
                username = self.get_username_from_public_key(addr)
                print(str(amt) + " to " + username + "\n")
        print("Signature:")
        for s in transaction.sigs:
            print(str(s) + "\n")
        print("Validity:", transaction.validtx)
        print("Fee:", transaction.fee)
        print("====================\n")

    def get_username_from_public_key(self, public_key):
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE public_key=?", (public_key,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
        elif(public_key == "SYSTEM_SIGNUP_REWARD"):
            return "SIGNUP REWARD"  # If no username found for the public key
        elif(public_key == "SYSTEM_MINING_REWARD"):
            return "MINING REWARD"
        else:
            return "Unknown User"

if __name__ == '__main__':
    checkpool = Checkpool()
    checkpool.PrintPool()