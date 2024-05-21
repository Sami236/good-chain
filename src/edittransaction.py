import os
import pickle
import sqlite3
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from Checkbalance import CheckBalance
from hashfiles import update_file_hashes
clear = lambda: os.system('cls')

class EditTransaction:
    def editTransaction(self, username):
        clear()
        balance_checker = CheckBalance()
        current_balance = balance_checker.check_balance(username)
        
        if current_balance is None:
            print("Error: Unable to retrieve balance. Please try again later.")
            return
        
        pool = self.load_pool()
        transaction_indices = self.display_transactions(pool, username)

        if not transaction_indices:
            print("You haven't made any transactions yet.")
            input("Press [Enter] to return to the main menu...")
            return

        selected_index = self.get_selected_index(transaction_indices)
        if selected_index is None:
            print("Invalid transaction index.")
            input("Press [Enter] to return to the main menu...")
            return
        
        transaction_index = transaction_indices[selected_index]
        transaction = pool[transaction_index]
        
        new_amount, new_fee = self.get_new_values()
        new_balance = current_balance + transaction.outputs[0][1] - (new_amount + new_fee)
        
        if new_balance < 0:
            print("Error: Insufficient balance to edit transaction.")
            input("Press [Enter] to return to the main menu...")
            return
        
        self.modify_transaction(transaction, new_amount, new_fee, username)
        self.save_pool(pool)
        print("Transaction edited successfully.")
        input("Press [Enter] to return to the main menu.")

    def display_transactions(self, pool, username):
        user_public_key = self.get_public_key_from_db(username)
        print("Your Transactions in the Pool:")
        print("")
        
        user_transaction_indices = []
        
        for transaction in pool:
            sender_public_key = transaction.inputs[0][0]
            if sender_public_key == user_public_key:
                user_transaction_indices.append(pool.index(transaction))
                receiver_public_key = transaction.outputs[0][0]
                receiver_username = self.get_username_from_public_key(receiver_public_key)
                amount_sent = transaction.outputs[0][1]
                print(f"{len(user_transaction_indices)}. You sent {amount_sent} coins to {receiver_username}")
        
        print("")
        return user_transaction_indices

    def get_selected_index(self, transaction_indices):
        try:
            selected_index = int(input("Enter the index of the transaction you want to edit: ")) - 1
        except ValueError:
            return None
        return selected_index if 0 <= selected_index < len(transaction_indices) else None

    def get_new_values(self):
        while True:
            try:
                new_amount_input = input("Enter the new amount (or press Enter to keep the same): ").strip()
                new_amount = float(new_amount_input) if new_amount_input else 0
                if new_amount <= 0:
                    print("Error: Amount cannot be negative.")
                    continue

                new_fee_input = input("Enter the new fee (or press Enter to keep the same): ").strip()
                new_fee = float(new_fee_input) if new_fee_input else 0
                if new_fee < 0:
                    print("Error: Fee cannot be negative.")
                    continue

                return new_amount, new_fee
            except ValueError:
                print("Error: Please enter a valid number.")


    def modify_transaction(self, transaction, new_amount, new_fee , username):
        prv_key = self.get_private_key_from_db(username)
        decodedprvkey = load_pem_private_key(prv_key, password=None)
        transaction.inputs = [(transaction.inputs[0][0], new_amount)]
        transaction.outputs[0] = (transaction.outputs[0][0], new_amount)
        transaction.fee = new_fee
        transaction.sign(decodedprvkey)

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
    
    def get_private_key_from_db(self, username):
        db_path = os.path.join('./data', 'goodchain.db')
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT private_key FROM users WHERE username=?", (username,))
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
    edit_transaction = EditTransaction()
    edit_transaction.editTransaction('jq')
