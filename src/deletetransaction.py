import os
import pickle
import sqlite3
from Checkbalance import CheckBalance
from hashfiles import update_file_hashes
clear = lambda: os.system('cls')
class DeleteTransaction:
    
    def deleteTransaction(self, username):
        clear()
        balance_checker = CheckBalance()
        current_balance = balance_checker.check_balance(username)
        
        if current_balance is None:
            print("Error: Unable to retrieve balance. Please try again later.")
            return
        
        print("Current balance:", current_balance)
        
        pool = self.load_pool()
        transaction_indices = self.display_transactions(pool, username)

        if not transaction_indices:
            print("No transactions found in the pool.")
            input("Press [Enter] to return to the main menu...")
            return

        selected_index = self.get_selected_index(transaction_indices)
        if selected_index is None:
            print("Invalid transaction index.")
            input("Press [Enter] to return to the main menu...")
            return
        
        transaction_index = transaction_indices[selected_index]
        
        del pool[transaction_index]
        
        self.save_pool(pool)
        print("Transaction deleted successfully.")
        input("Press [Enter] to return to the main menu...")

    def display_transactions(self, pool, username):
        user_public_key = self.get_public_key_from_db(username)
        print("Your Transactions in the Pool:")
        print("")
        
        user_transaction_indices = []
        
        for idx, transaction in enumerate(pool):
            sender_public_key = transaction.inputs[0][0]
            if sender_public_key == user_public_key:
                user_transaction_indices.append(idx)
                receiver_public_key = transaction.outputs[0][0]
                receiver_username = self.get_username_from_public_key(receiver_public_key)
                amount_sent = transaction.outputs[0][1]
                print(f"{len(user_transaction_indices)}. You sent {amount_sent} coins to {receiver_username}")
        
        print("")
        return user_transaction_indices

    def get_selected_index(self, transaction_indices):
        try:
            selected_index = int(input("Enter the index of the transaction you want to delete: ")) - 1
        except ValueError:
            return None
        return selected_index if 0 <= selected_index < len(transaction_indices) else None

    def load_pool(self):
        filepath = os.path.join('./data', 'pool.dat')
        try:
            with open(filepath, "rb") as loadfile:
                pool = pickle.load(loadfile)
        except EOFError:
            pool = []
        return pool

    def save_pool(self, pool):
        filepath = os.path.join('./data', 'pool.dat')
        with open(filepath, "wb") as savefile:
            pickle.dump(pool, savefile)
        
        update_file_hashes('pool', filepath)

    def get_public_key_from_db(self, username):
        db_path = os.path.join('./data', 'goodchain.db')
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT public_key FROM users WHERE username=?", (username,))
            row = c.fetchone()
        return row[0] if row else None

    def get_username_from_public_key(self, public_key):
        if public_key == "SYSTEM":
            return "SYSTEM"
        db_path = os.path.join('./data', 'goodchain.db')
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE public_key=?", (public_key,))
            row = c.fetchone()
        return row[0] if row else None

if __name__ == '__main__':
    delete_transaction = DeleteTransaction()
    delete_transaction.deleteTransaction('sami')
