import os
import pickle
from blockchain import *
import time
from Transaction import *
import sqlite3
from hashfiles import update_file_hashes, check_blockchain_integrity
clear = lambda: os.system('cls')

class MineBlock():
    def __init__(self):
        self.amount = 0

    def mineBlock(self, username):
        clear()
        check_blockchain_integrity()
        path = os.path.join('./data', 'pool.dat')

        with open(path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                print("No transactions found in the pool.")
                input("Press [Enter] to return to the main menu...")
                return
        
        valid_transactions = [tx for tx in pool if tx.validtx]
        valid_transactions.sort(key=lambda tx: tx.fee, reverse=True)

        # Select the top 5 transactions with the highest fees
        top_transactions = valid_transactions[:5]

        # Select additional transactions if available, without including the top transactions
        additional_transactions = [tx for tx in pool if tx.validtx and tx not in top_transactions]
        additional_transactions = additional_transactions[:4]
        transactions = top_transactions + additional_transactions
        
        if len(transactions) < 5:
            print("Not enough transactions to mine ( AT LEAST 5 ).")
            input("Press [ENTER] to continue")
            return
    
        ledger_path = os.path.join('./data', 'blockchain.dat')

        with open(ledger_path, 'rb') as ledger_file:
            try:
                ledger  = pickle.load(ledger_file)
            except EOFError:
                ledger = []
        
        
        if len(ledger) > 0 and not ledger[-1].isvalid:
            print("Last block has not been validated. Cannot mine a new block.")
            input("Press [ENTER] key to continue")
            return
        
        if len(ledger) > 0:
            previous_block = ledger[-1]
            previous_block_timestamp = previous_block.timestamp
            current_time = time.time()
            time_diff = current_time - previous_block_timestamp
            
   
            if time_diff < 180: # Dit kan je aanpassen naar 0 voor testen
                remaining_time = 180 - time_diff
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                
                time_diff_formatted = "{:02d}:{:02d}".format(minutes, seconds)
                print("Minimum 3 minutes interval not reached since the last block was mined.")
                print("Time remaining:", time_diff_formatted)
                input("Press [ENTER] key to continue")
                return

        
        block_id = len(ledger)  
        
        if len(ledger) == 0:
            new_block = TxBlock(None, block_id)
        else:
            new_block = TxBlock(ledger[-1], block_id)
        
        invald_flag = False
        for tx in transactions:
            if not tx.is_valid():
                invald_flag = True
            else:
                new_block.addTx(tx)
        
        if invald_flag:
            path = os.path.join('./data', 'pool.dat')
            with open(path, 'wb') as pool_file:
                pickle.dump(pool, pool_file)
            print("One or more transactions are invalid. Flagging all invalid transactions.")
            update_file_hashes('pool', "./data/pool.dat")
            input("Press [ENTER] key to continue")
            return

        fee = new_block.get_total_fee()
        pbkey = self.GetPublcKey(username)
        total_fee = fee + REWARD_VALUE
        tx = Tx(REWARD)
        tx.add_input("SYSTEM_MINING_FEE", total_fee)
        tx.add_fee(fee)
        tx.add_output(pbkey, total_fee)
        tx.is_valid()
        new_block.addTx(tx)
        
        start_time = time.time()
        new_block.mine(leading_zero=3)
        end_time = time.time()
        print("Block mined in " + str(end_time - start_time) + " seconds.")

        if not new_block.is_valid():    
            print("Error! Invalid block detected.")
            input("Press [ENTER] to continue")
            return

        new_block.miner = username
        
        ledger.append(new_block)

        with open(ledger_path, 'wb') as ledger_file:
            pickle.dump(ledger, ledger_file)
        
        update_file_hashes('blockchain', ledger_path)
            
        pool_path = os.path.join('./data', 'pool.dat')
        remaining_transactions = [tx for tx in pool if tx not in transactions]
        with open(pool_path, 'wb') as pool_file:
            pickle.dump(remaining_transactions, pool_file)

        update_file_hashes('pool', pool_path)
        print("Block added to the blockchain.")
        input("Press [ENTER] to continue")
    
    def GetPublcKey(self, username):
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if(user == None):
            return
        conn.close()
        return user[3]

if __name__ == '__main__':
    mineblock = MineBlock()
    mineblock.mineBlock("miner")