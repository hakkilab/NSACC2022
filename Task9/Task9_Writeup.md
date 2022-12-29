
# **Task 9 - The End of the Road**

## <ins>Topics:</ins>

Cryptanalysis, Software Development

## <ins>Task Description<ins>

Unfortunately, looks like the ransomware site suffered some data loss, and doesn't have the victim's key to give back! I guess they weren't planning on returning the victims' files, even if they paid up.

There's one last shred of hope: your cryptanalysis skills. We've given you one of the encrypted files from the victim's system, which contains an important message. Find the encryption key, and recover the message.

## <ins>Provided Files<ins>

<ul>
<li>Encrypted file recovered from the victim's system (important_data.pdf.enc)</li>
</ul>

## <ins>Solution<ins>

### **1) Understanding encryption process and key generation**

In Task A2, the tools used by the attacker to carry out the ransomware attack were found. In particular we found `ransom.sh`, which takes in an encryption key, converts it to hex and takes the first 16 bytes, and then for each file it finds using a regex, it generates 16 random bytes for an IV and does AES-128-CBC encryption of the file contents using the 16 bytes of the key and the IV. At the end, the encrypted file starts with the hex characters of the 16 byte IV (32 characters) and then is followed by the encrypted file contents.

The key that is used for this encryption comes from `keyMaster`, and we saw that it is generated using `github.com/google/uuid.NewUUID`. Looking at the [documentation](https://pkg.go.dev/github.com/google/UUID#NewUUID) we see that this function generates a `Version 1 UUID` based on the time. Luckily, the documentation also links to the [RFC](https://www.rfc-editor.org/rfc/rfc4122.html) for this UUID. We see that UUIDs come in the form `[time-low]-[time-mid]-[time-high-and-version]-[clock-seq-and-reserved][clock-seq-low]-[node]`. `time-low` is 4 bytes in hex, `time-mid` is 2 bytes in hex, `time-high-and-version` is 2 bytes in hex, `clock-seq-and-reserved` and `clock-seq-low` are each 1 byte in hex, and `node` is 6 bytes in hex. One thing to note here is that the UUIDs returned by `keyMaster` have the last two bytes of `node` removed so that the total UUID has 32 characters instead of 36, so form now on we will refer to `node` as having 4 bytes.

To generate the UUID, a 60 bit number integer representing the number of 100 nanosecond intervals since midnight (00:00:00) October 15, 1582 is calculated from the current UTC time, the 48 bit node id is derived from the IEEE address, and the 14 bit clock sequence is taken from the state of the UUID generator. Bits 0-31 of the timestamp become `time-low`, bits 32-47 become `time-mid`, and bits 48-59 become the lowest 12 bits of `time-high-and-version`. The highest 4 bits of `time-high-and-version` are then set based on the UUID version (always `0001` for Version 1). Bits 0-7 of the clock sequence become `clock-seq-low`. Bits 8-13 of the clock sequence become the lowest 6 bits of `clock-seq-and-reserved` and bits 6 and 7 are always set to `0` and `1` respectively. Finally, all bits of node id cecome `node`.

Luckily, since the encryption process takes the key, converts it to hex, and only uses the first 32 characters (16 bytes) as the AES key, we only need to guess the first 16 characters of a UUID. This means we need to guess `time-low`, `time-mid`, and `time-high-and-version`, which all just depend on a timestamp, to start guessing at the encryption key used.

### **2) Investigating guesses for timestamps**

Based on the `cid` (`66207`) we saw in Task B2 used for the ransomware site API, we can see that the key generation was logged in `keygeneration.log` at `2022-06-01T10:44:37-04:00` but an entry is missing from `keyMaster.db`. Looking at the key generation events that are present in both files, we can see that the time stamps are different, with `keygeneration.log` having a later timestamp. On top of that, the time in `keyMaster.db` has less precision than the precision used for UUID generation, so there is some error in using the database timestamp.

Using a python script (`time_difference.py`), we calculate the time difference between UUID time (time of generation derived from UUID) and `keygeneration.log` time and see that the range of this time difference is `6.027159` to `11.862509` seconds. Since the time for the ransom attack is missing from `keyMaster.db`, we can test a range of times from `6` to `12` seconds before the timestamp in `keygeneration.log` to get times for generating UUIDs for decryption.

### **3) Brute force decryption of PDF**

Based on what we found, we can create a script that generates UUID guesses and attempts to decrypt the .pdf using these guesses (`crack_encryption.py`).

Beyond the optimization of only needing the timestamp, another optimization comes from the fact that only the highest byte of `time-high-and-version` is needed for the key. We in fact always know this value is `0x11` because the highest 4 bits of that byte are `0001` for the version number, and the next 4 bits are the highest 4 bits of the timestamp. This restricts the value of those 4 bits to `0001` because if the bits were `0000`, the latest UUID would look like `ffffffff-ffff-10ff-xxxx-xxxxxxxx` which is generated at `1811-02-16 23:50:03.792793+00:00`, and if the bits were `0010`, the earliest UUID would look like `00000000-0000-1200-xxxx-xxxxxxxx` which is generated at `2039-06-20 23:40:07.585587+00:00`. Since these times are way outside the range of the time of the attack, they can not be valid. The last optimization is to only decrypt the first block for each check and look for the magic bytes of a PDF file (`%PDF-`), and only if this pattern is seen, decrypt the remaining contents.

After running the script, the PDF is decrypted and we can look inside to find the answer for this task:

XraPicXV8yv3riHtmA4Cp75AYeKDHGcl