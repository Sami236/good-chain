import os
import pickle
import sqlite3
from blockchain import TxBlock, time
from hashfiles import check_blockchain_integrity

def display_transaction_history(username):
    blockchain = load_blockchain()
    pool = load_pool()
    notifications = generate_block_notifications(blockchain, pool, username)
    os.system('cls')
    print("Your Transaction history:")
    print("")
    for notification in notifications:
        if "You received" in notification or "You sent" in notification:
            print(notification)
    print("")
    input('Press [ENTER] to continue..')

def generate_block_notifications(blockchain, pool, username):
    notifications = []

    # Process transactions in the blockchain
    for block in blockchain:
        if isinstance(block, TxBlock):
            block_timestamp = time.strftime('%m-%d %H:%M:%S', time.localtime(block.timestamp))
            for transaction in block.data:
                sender_public_key, receiver_public_key = transaction.inputs[0][0], transaction.outputs[0][0]
                sender_username = get_username_from_public_key(sender_public_key)
                receiver_username = get_username_from_public_key(receiver_public_key)

                if username in [sender_username, receiver_username]:
                    amount = transaction.inputs[0][1] if sender_username == username else transaction.outputs[0][1]
                    transaction_type = "sent" if sender_username == username else "received"
                    reward_type = "signup reward" if sender_public_key == "SYSTEM_SIGNUP_REWARD" else "mining reward" if sender_public_key == "SYSTEM_MINING_FEE" else None
                    if reward_type:
                        if(block.isvalid):
                            new_notification = f"{block_timestamp}: You received {amount} coins as a {reward_type}"
                        elif(not block.isvalid):
                            new_notification = f"{block_timestamp}: You received {amount} coins as a {reward_type} ( BLOCK NOT VALIDATED YET )"
                    else:
                        if(transaction_type == "sent" and block.isvalid):
                            new_notification = f"{block_timestamp}: You {transaction_type} {amount} coins to {receiver_username}"
                        if(transaction_type == "sent" and not block.isvalid):
                            new_notification = f"{block_timestamp}: You {transaction_type} {amount} coins to {receiver_username} ( BLOCK NOT VALIDATED YET )"
                        if(transaction_type == "received" and block.isvalid):
                            new_notification = f"{block_timestamp}: You {transaction_type} {amount} coins from {sender_username}"
                        if(transaction_type == "received" and not block.isvalid):
                            new_notification = f"{block_timestamp}: You {transaction_type} {amount} coins from {sender_username} ( BLOCK NOT VALIDATED YET )"
                
                    notifications.append(new_notification)

    # Process transactions in the pool
    for transaction in pool:
        transaction_timestamp = time.strftime('%m-%d %H:%M:%S', time.localtime(transaction.timestamp))
        sender_public_key, receiver_public_key = transaction.inputs[0][0], transaction.outputs[0][0]
        sender_username = get_username_from_public_key(sender_public_key)
        receiver_username = get_username_from_public_key(receiver_public_key)

        if username in [sender_username, receiver_username]:
            amount = transaction.inputs[0][1] if sender_username == username else transaction.outputs[0][1]
            transaction_type = "sent" if sender_username == username else "received"
            reward_type = "signup reward" if sender_public_key == "SYSTEM_SIGNUP_REWARD" else "mining reward" if sender_public_key == "SYSTEM_MINING_FEE" else None
            if reward_type:
                new_notification = f"{transaction_timestamp}: You received {amount} coins as a {reward_type} (IN POOL)"
            else:
                if(transaction_type == "sent"):
                    new_notification = f"{transaction_timestamp}: You {transaction_type} {amount} coins to {receiver_username} (IN POOL)"
                if(transaction_type == "received"):
                    new_notification = f"{transaction_timestamp}: You {transaction_type} {amount} coins from {sender_username} (IN POOL)"
            notifications.append(new_notification)

    # Process mined blocks
    for block in blockchain:
        if isinstance(block, TxBlock) and block.miner == username:
            block_timestamp = time.strftime('%m-%d %H:%M:%S', time.localtime(block.timestamp)) 
            block_status = "VALID" if block.isvalid else "INVALID"
            new_block_notification = f"{block_timestamp}: Block {block.block_id} mined by you is {block_status}."
            notifications.append(new_block_notification)

    return notifications

def load_blockchain():
    check_blockchain_integrity()
    filepath = os.path.join('./data', 'blockchain.dat')
    with open(filepath, "rb") as loadfile:
        try:
            blockchain = pickle.load(loadfile)
        except EOFError:
            blockchain = []
    return blockchain

def load_pool():
    filepath = os.path.join('./data', 'pool.dat')
    with open(filepath, "rb") as loadfile:
        try:
            pool = pickle.load(loadfile)
        except EOFError:
            pool = []
    return pool

def get_public_key_from_db(username):
    db_path = os.path.join('./data', 'goodchain.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT public_key FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_username_from_public_key(public_key):
    if public_key == "SYSTEM_SIGNUP_REWARD":
        return "System Signup Reward"
    elif public_key == "SYSTEM_MINING_FEE":
        return "System Mining Fee"
    
    db_path = os.path.join('./data', 'goodchain.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE public_key=?", (public_key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
