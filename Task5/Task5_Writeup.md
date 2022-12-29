
# **Task 5 - Core Dumped**

## <ins>Topics:</ins>

Reverse Engineering, Cryptography

## <ins>Task Description<ins>

The FBI knew who that was, and got a warrant to seize their laptop. It looks like they had an encrypted file, which may be of use to your investigation.

We believe that the attacker may have been clever and used the same RSA key that they use for SSH to encrypt the file. We asked the FBI to take a core dump of `ssh-agent` that was running on the attacker's computer.

Extract the attacker's private key from the core dump, and use it to decrypt the file.

Hint: if you have the private key in PEM format, you should be able to decrypt the file with the command `openssl pkeyutl -decrypt -inkey privatekey.pem -in data.enc`

## <ins>Provided Files<ins>

<ul>
<li>Core dump of ssh-agent from the attacker's computer (core)</li>
<li>ssh-agent binary from the attacker's computer. The computer was running Ubuntu 20.04. (ssh-agent)</li>
<li>Encrypted data file from the attacker's computer (data.enc)</li>
</ul>

## <ins>Solution<ins>

### **1) Investigating the core dump**

We are given a core dump of `ssh-agent` to investigate. Since `ssh-agent` is part of `openssh`, we can refer to the source code in GitHub to orient ourselves. In particular, looking at [ssh-agent.c](https://github.com/openssh/openssh-portable/blob/master/ssh-agent.c) and [sshkey.h](https://github.com/openssh/openssh-portable/blob/master/sshkey.h) we can see how the private key is stored in memory. `ssh-agent` has a pointer `idtab` to a struct called `idtable`, which contains a queue of `identity` structs. These `identity` structs in turn each have a pointer to a `sshkey` struct, which finally has pointers to `shielded_private` and `shield_prekey` byte arrays. `ssh-agent` uses [shielding](https://xorhash.gitlab.io/xhblog/0010.html) to protect ssh keys from certain attacks, so we will need to unshield the private key before we can use it.

We need to actually find these structs in order to go any further. Luckily, the `socket_name` char array in `ssh-agent.c` comes in the form `/tmp/ssh-*/agent.*` which can be [searched for](https://vnhacker.blogspot.com/2009/09/sapheads-hackjam-2009-challenge-6-or.html) to orient ourselves in memory. Using Ghidra to open the `core` file, we use `Search > Memory...` and search for the string `/tmp/ssh`. We find the string `/tmp/ssh-Dl2hIrdntOh2/agent.18` at memory address `0x55754f74b7e0`. The `ssh-agent` executable we were given has debug symbols, so we can load it into Ghidra as well and use `Navigation > Go To...` to find `socket_name`. We see that there are 32 bytes of memory between `socket_name` and `idtab`, so we look in `core` at `0x55754f74b7c0` and find the value `0x55754f78d3c0`, which we use `Navigation > Go To...` to follow to find the `idtable` struct.

The first value we see is a 1, which corresponds to the `nentries` field of the `idtable` struct. Looking at the idtable struct data type in the Ghidra session for `ssh-agent` we see that the `idlist` field has an offset of 8, so we look at `0x55754f78d3c8` and see the value `0x55754f792120`, a pointer to an `identity` struct that we follow.

### **2) Extracting and unshielding the private key**

At this point, we could continue following pointers to the `sshkey` struct, and then follow the `shielded_private` and `shield_prekey` pointers to get the data we need, and finally reimplement the unshielding algorithm to get our key. However, the wheel has already been invented and we can build off of work done by others. Using scripts and methods outlined [here](https://security.humanativaspa.it/openssh-ssh-agent-shielded-private-key-extraction-x86_64-linux/), we can extract the data much more easily.

To use this method, we need to find the comment for the ssh key. Luckily, we already know where the `identity` struct is, so if we look at the `identity` data type in the Ghidra session we see that the `comment` has an offset of 24, putting it at `0x55754f792138`. Looking at this location in memory we see the string `i5P5OCfj3sjdre2hSBtiQ`, which is our comment.

After moving the `ospke.java` script from the above post to the appropriate folder for Ghidra scripts, we can run it in Ghidra from the Script Manager and provide the comment we found. This creates two files, `shield_prekey` and `shielded_private`. 

Next we need to build `ssh-keygen` from source with symbols to take advantage of the `sshkey_unshield_private` and `sshkey_save_private` functions. Using a shell script (`build_keygen.sh`) we clone and build ssh-keygen with debug symbols and without optimization. Then we can run `gdb ./ssh-keygen` and copy commands from the file `gdb_unshield` to save the private key to the file `plaintext_private_key`.

### **3) Decrypting data**

The last steps are to convert the private key to a form we can use and then decrypt the `data.enc` file we were given. After making a copy of `plaintext_private_key` called `privatekey.pem`, we run the command `ssh-keygen -p -f privatekey.pem -m pem -N ""` to convert the private key. Finally we can run `openssl pkeyutl -decrypt -inkey privatekey.pem -in data.enc > data` to decrypt the file. The file now contains a cookie and we get the token we need:

eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NTM2NjkzNTgsImV4cCI6MTY1NjI2MTM1OCwic2VjIjoiS0h0a3dRY0xleWlHYVdlU1MyTENuMVBRNWJ5OG41RzgiLCJ1aWQiOjQ1MjA0fQ.fMH-Jg66VIjKW6fCLToeSTaW4IV6kP2nqtWedGfzSRE