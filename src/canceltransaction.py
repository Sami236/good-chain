import pickle
import os
import sqlite3

from hashfiles import update_file_hashes
clear = lambda: os.system('cls')

class CancelTransaction():
    def __init__(self):
        pass


    def cancel_transaction(self,username):
        clear()
        with open('./data/pool.dat', 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []
        
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if username == user[1]:
            pbkey = user[3]
        
        notify = False
        valid_transactions = []
        for tx in pool:
            for addr, amount in tx.inputs:
                if addr == pbkey or addr == "SYSTEM_SIGNUP_REWARD" or addr == "SYSTEM_MINING_REWARD":
                    if not tx.validtx:
                        notify = True
                        break
            else:
                # Add valid transactions to the new list
                valid_transactions.append(tx)

        if notify:
            print("One or more of your transactions are invalid. Cancelling all transactions.")
            input("Press [ENTER] to return to the main menu")

        with open('./data/pool.dat', 'wb') as file_handle:
            pickle.dump(valid_transactions, file_handle)
        
        update_file_hashes('pool', './data/pool.dat')
    

if __name__ == '__main__':
    cancel = CancelTransaction()
    cancel.cancel_transaction('jq')
            

