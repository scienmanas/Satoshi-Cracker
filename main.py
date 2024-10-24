import os
import hashlib
import ecdsa
import base58
import bech32
import requests
import csv
from colorama import Fore, init
from datetime import datetime
from smtplib import SMTP
from dotenv import load_dotenv
# import time
from email.message import EmailMessage

load_dotenv()  # take environment variables from .env.

# Initialize colorama for styling and smtp
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
RECEIVER_EMAIl="iamscientistmanas@gmail.com"
init(autoreset=True)
smtp_server = SMTP(host="smtp.gmail.com", port=587)
smtp_server.starttls()
smtp_server.login(user=EMAIL, password=PASSWORD)

# Helper functions
def ripemd160(x):
    d = hashlib.new('ripemd160')
    d.update(x)
    return d

def sha256(x):
    return hashlib.sha256(x).digest()

# Generate a random private key
def generate_private_key():
    return os.urandom(32)

# Generate public key from private key
def generate_public_key(private_key, compressed):
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    if compressed:
        return (b'\x02' if vk.to_string()[32] % 2 == 0 else b'\x03') + vk.to_string()[:32]
    else:
        return b'\x04' + vk.to_string()  # Uncompressed public key

# Generate legacy (P2PKH) Bitcoin address
def generate_legacy_address(public_key):
    sha256_pk = sha256(public_key)
    ripemd160_pk = ripemd160(sha256_pk).digest()
    pre_address = b'\00' + ripemd160_pk  # Prepend version byte
    checksum = sha256(sha256(pre_address))[:4]
    address = pre_address + checksum
    return base58.b58encode(address).decode()

# Generate SegWit (Bech32) Bitcoin address
def generate_segwit_address(public_key):
    sha256_bpk = sha256(public_key)
    ripemd160_bpk = ripemd160(sha256_bpk).digest()
    return bech32_encode('bc', 0, ripemd160_bpk)

# Bech32 encoding function
def bech32_encode(hrp, witver, witprog):
    witprog_bits = bech32.convertbits(witprog, 8, 5)
    return bech32.bech32_encode(hrp, [witver] + witprog_bits)

# Function to get balance and transaction details from Blockstream API
def get_address_info(address):
    url = f'https://blockstream.info/api/address/{address}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Address: ",data["address"])
        return {
            "total_transactions": data["chain_stats"]["tx_count"],
            "balance": data["chain_stats"]["funded_txo_sum"] - data["chain_stats"]["spent_txo_sum"]
        }
    else:
        return {"error": "Unable to fetch data"}

# Save key and address info to CSV
def save_to_csv(private_key, public_key, address, address_type, compressed, balance, total_transactions):
    # Save in csv
    with open('keys_and_addresses.csv', mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([private_key.hex(), public_key.hex(), address , address_type, compressed, balance, total_transactions])

    # Send email
    # Construct the message with a subject line
    msg = EmailMessage()
    subject = "Found something, please check!"
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = RECEIVER_EMAIl
    subject = "Found something, please check!"
    body = (
        "Found something, please check the details below:\n\n"
        f"Private key: {private_key.hex()}\n"
        f"Public key: {public_key.hex()}\n"
        f"Address: {address}\n"
        f"Address type: {address_type}\n"
        f"Compressed: {compressed}\n"
        f"Balance: {balance}\n"
        f"Total Transactions: {total_transactions}"
    )
    msg.set_content(body)
    smtp_server.send_message(msg=msg)
    

# Function to display logs
def display_log(address_type, compressed, balance, total_transactions):
    if total_transactions == 0 and balance == 0:
        print(Fore.RED + f"[{address_type} - {'Compressed' if compressed else 'Uncompressed'}] No transactions found.")
    else:
        print(Fore.GREEN + f"[{address_type} - {'Compressed' if compressed else 'Uncompressed'}] Found: {balance} satoshis and {total_transactions} transaction(s).")

# Main loop
while True:
    # Generate a random private key for testing
    # private_key = bytes.fromhex("20536951acc1f347f922e64a62aec1ce3b73f038a99cb9d56f3d313f2f8caac5")
    private_key = generate_private_key()
    public_key = generate_public_key(private_key=private_key, compressed=False)
    public_key_compressed = generate_public_key(private_key=private_key, compressed=True)

    # Generate addresses
    legacy_address = generate_legacy_address(public_key)
    legacy_address_compressed = generate_legacy_address(public_key_compressed)
    segwit_address = generate_segwit_address(public_key)
    segwit_address_compressed = generate_segwit_address(public_key_compressed)

    # Fetch and display address information
    legacy_info = get_address_info(legacy_address)
    legacy_compressed_info = get_address_info(legacy_address_compressed)
    segwit_info = get_address_info(segwit_address)
    segwit_compressed_info = get_address_info(segwit_address_compressed)

    print("*******************************************************")

    # Check for balance or transactions and save to CSV if any are found
    if legacy_info.get("total_transactions") > 0 or legacy_info.get("balance") > 0:
        print(Fore.GREEN + "[Legacy - Uncompressed] Found something!")
        save_to_csv(private_key, public_key, legacy_address , "Legacy", "Uncompressed", legacy_info["balance"], legacy_info["total_transactions"])


    if legacy_compressed_info.get("total_transactions") > 0 or legacy_compressed_info.get("balance") > 0:
        print(Fore.GREEN + "[Legacy - Compressed] Found something!")
        save_to_csv(private_key, public_key_compressed,legacy_address_compressed ,"Legacy", "Compressed", legacy_compressed_info["balance"], legacy_compressed_info["total_transactions"])

    if segwit_info.get("total_transactions") > 0 or segwit_info.get("balance") > 0:
        print(Fore.GREEN + "[SegWit - Uncompressed] Found something!")
        save_to_csv(private_key, public_key,segwit_address ,"SegWit", "Uncompressed", segwit_info["balance"], segwit_info["total_transactions"])

    if segwit_compressed_info.get("total_transactions") > 0 or segwit_compressed_info.get("balance") > 0:
        print(Fore.GREEN + "[SegWit - Compressed] Found something!")
        save_to_csv(private_key, public_key_compressed, segwit_address_compressed, "SegWit", "Compressed", segwit_compressed_info["balance"], segwit_compressed_info["total_transactions"])

    # Display logs for each address
    display_log("Legacy", False, legacy_info.get("balance"), legacy_info.get("total_transactions"))
    display_log("Legacy", True, legacy_compressed_info.get("balance"), legacy_compressed_info.get("total_transactions"))
    display_log("SegWit", False, segwit_info.get("balance"), segwit_info.get("total_transactions"))
    display_log("SegWit", True, segwit_compressed_info.get("balance"), segwit_compressed_info.get("total_transactions"))

    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    time_str = Fore.CYAN + f"Time: {current_time}"
    print("\nTime: ", time_str)
    print(Fore.YELLOW + "Scanning completed for one key pair. Starting next...")
    print("*******************************************************\n")
    # time.sleep(20)  # Pause for 5 seconds before scanning the next pair
