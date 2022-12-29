import sqlite3
from datetime import datetime, timedelta
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# convert uuid to time of uuid generation
epoch = datetime.fromisoformat('1582-10-15T00:00:00+00:00')
def uuid2time(uuid):
    time_lo = uuid[:8]
    time_mid = uuid[9:13]
    time_hi = uuid[15:18]
    time_since_epoch = int(time_hi + time_mid + time_lo, 16) / 1e7 # convert to seconds from 100s of ns
    return epoch + timedelta(seconds=time_since_epoch)

# read in data from key generation log file
log_data = {}
with open('keygeneration.log', 'r') as f:
    for line in f:
        timestamp, user, cid, ransom = line.strip().split('\t')
        log_data[int(cid)] = datetime.fromisoformat(timestamp)

aes_key = b64decode("2ibhZ9dBff7trI9UdE5I+41KYEmSqT7YZcMsXgPlZ4k=")
db = sqlite3.connect('keyMaster.db')

# read in data from keyMaster database and calculate time from UUID
db_data = {}
for row in db.execute("SELECT customerId, encryptedKey from customers;"):
    cid = row[0]
    encrypted_key = b64decode(row[1])
    iv, encrypted_key = encrypted_key[:16], encrypted_key[16:]
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
    decrypted_key = unpad(cipher.decrypt(encrypted_key), AES.block_size).decode('utf-8')
    db_data[cid] = uuid2time(decrypted_key)

# find the range of time differences between log timestamp and uuid actual time
min_diff = float('inf')
max_diff = float('-inf')
for cid in db_data:
    time_diff = (log_data[cid] - db_data[cid]).total_seconds()
    min_diff = min(min_diff, time_diff)
    max_diff = max(max_diff, time_diff)

print(min_diff, max_diff)