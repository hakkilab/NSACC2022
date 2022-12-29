from datetime import datetime, timedelta
from base64 import b64decode
from Crypto.Cipher import AES

# function for converting time since epoch to key
def timestamp_to_key(time_int):
    hex_time = hex(time_int)[-12:]
    return f"{hex_time[4:]}-{hex_time[:4]}-11".encode('utf-8')

# extract IV characters and encrypted contents from PDF
with open('important_data.pdf.enc', 'rb') as f:
	contents = f.read()
	iv = bytes.fromhex(contents[:32].decode('utf-8'))
	contents = contents[32:]

# create small block for testing decryption
test_block = contents[:AES.block_size]

# calculate time to offset from
epoch = datetime.fromisoformat('1582-10-15T00:00:00+00:00')
log_time = datetime.fromisoformat('2022-06-01T10:44:37-04:00')
time_since_epoch = 1e7 * int((log_time - epoch).total_seconds())

# iterate over time range attempting decryption with generated key
for t in range(int(time_since_epoch - 12e7), int(time_since_epoch - 6e7)+1):
    key = timestamp_to_key(t)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_block = cipher.decrypt(test_block)
    if decrypted_block[:5] == b'%PDF-':
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        decrypted_contents = cipher.decrypt(contents)
        with open(f"important_data.pdf", 'wb') as fhand:
            fhand.write(decrypted_contents)
        print('Encryption cracked!')
        break
    if t % 100000 == 0:
        print(t)