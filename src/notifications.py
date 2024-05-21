import os
import sqlite3
from blockchain import TxBlock, time
import pickle
from hashfiles import *

def generate_block_notifications(blockchain, username):
    stored_notifications = get_stored_notifications(username)
    notifications = []

    user_public_key = get_public_key_from_db(username)
    user_username = get_username_from_public_key(user_public_key)

    # Get the last recorded block ID from the database
    last_recorded_block_id = get_last_recorded_block_id(username)
    
    # Count total number of blocks and transactions
    total_blocks = len(blockchain)
    total_transactions = sum(len(block.data) for block in blockchain if isinstance(block, TxBlock))

    notifications.append(f"Total number of blocks in the blockchain: {total_blocks}")
    notifications.append(f"Total number of transactions: {total_transactions}")

    # Check for new blocks and successful transactions
    new_block_ids = []
    for block in blockchain:
        if isinstance(block, TxBlock):
            block_timestamp = time.strftime('%d-%m %H:%M', time.localtime(block.timestamp))
            if block.miner == username:  # Check if the user mined this block
                if block.isvalid:
                    notifications.append(f"{block_timestamp}: Block {block.block_id} mined by you is VALID.")
                else:
                    notifications.append(f"{block_timestamp}: Block {block.block_id} mined by you has not been validated yet.")
                    # Don't store notifications about invalid blocks
                    continue

            # Check for successful transactions of the user
            for transaction in block.data:
                sender_public_key, receiver_public_key = transaction.inputs[0][0], transaction.outputs[0][0]
                if sender_public_key == user_public_key or receiver_public_key == user_public_key:
                    sender_username = get_username_from_public_key(sender_public_key)
                    receiver_username = get_username_from_public_key(receiver_public_key)

                    if sender_username == user_username and block.isvalid:  # Only notify if the block is valid
                        amount_sent = transaction.inputs[0][1]
                        notifications.append(f"{block_timestamp}: You sent {amount_sent} coins to {receiver_username}")
                    elif receiver_username == user_username and block.isvalid:  # Only notify if the block is valid
                        amount_received = transaction.outputs[0][1]
                        if sender_public_key == "SYSTEM_SIGNUP_REWARD":
                            notifications.append(f"{block_timestamp}: You received {amount_received} coins as a signup reward")
                        elif sender_public_key == "SYSTEM_MINING_FEE":
                            notifications.append(f"{block_timestamp}: You received {amount_received} coins as a mining reward")
                        else:
                            notifications.append(f"{block_timestamp}: You received {amount_received} coins from {sender_username}")

    # Record new block IDs
    if last_recorded_block_id is not None and block.block_id > last_recorded_block_id:
        new_block_ids.append(block.block_id)

    # Add notifications for new blocks
    if new_block_ids:
        new_block_ids.sort()
        blocks_added = max(new_block_ids) - last_recorded_block_id
        notifications.append(f"Blocks added since last login: {blocks_added}")

    # Store only new notifications except for notifications about invalid blocks
    new_notifications = [notification for notification in notifications if notification not in stored_notifications or "INVALID" in notification]
    store_notifications(username, stored_notifications + new_notifications)

    # Update the last recorded block ID in the database
    update_last_recorded_block_id(username, max(new_block_ids, default=last_recorded_block_id))
    
    # If last_recorded_block_id is None, update it to the latest block ID
    last_recorded_block_id = get_last_recorded_block_id(username)
    latest_block_id = get_latest_block_id(blockchain)
    if last_recorded_block_id is None:
        update_last_recorded_block_id(username, latest_block_id)

    return new_notifications

def get_last_recorded_block_id(username):
    db_path = os.path.join('./data', 'goodchain.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT last_recorded_block_id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None  # Return None if no record is found for the user

def update_last_recorded_block_id(username, block_id):
    db_path = os.path.join('./data', 'goodchain.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE users SET last_recorded_block_id=? WHERE username=?", (block_id, username))
    conn.commit()
    conn.close()


def get_stored_notifications(username):
    db_path = os.path.join('./data', 'goodchain.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT notifications FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        stored_notifications = row[0]
        if stored_notifications:
            return stored_notifications.split('\n')
    return []

def store_notifications(username, new_notifications):
    existing_notifications = get_stored_notifications(username)
    exempt_lines = ["Blocks added since last login: ", "Total number of blocks in the blockchain: ", "Your mined blocks:", "Total number of transactions:", "Transactions in the pool (awaiting validation):", "Transactions with/by you:",]
    filtered_notifications = [notification for notification in new_notifications if not any(exempt_line in notification for exempt_line in exempt_lines)]
    all_notifications = existing_notifications + filtered_notifications
    stored_notifications = '\n'.join(all_notifications)
    db_path = os.path.join('./data', 'goodchain.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE users SET notifications=? WHERE username=?", (stored_notifications, username))
    conn.commit()
    conn.close()
    update_file_hashes('db', db_path)
    
def get_latest_block_id(blockchain):
    latest_block_id = None
    for block in blockchain:
        if isinstance(block, TxBlock):
            if latest_block_id is None or block.block_id > latest_block_id:
                latest_block_id = block.block_id
    return latest_block_id


def get_public_key_from_db(username):
    db_path = os.path.join('./data', 'goodchain.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT public_key FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def get_username_from_public_key(public_key):
    if public_key == "SYSTEM_SIGNUP_REWARD":
        return "SYSTEM_SIGNUP_REWARD"
    elif public_key == "SYSTEM_MINING_FEE":
        return "SYSTEM_MINING_FEE"
    else:
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE public_key=?", (public_key,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
        return None
