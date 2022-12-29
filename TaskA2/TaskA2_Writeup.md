
# **Task A2 - Identifying the attacker**

## <ins>Topics:</ins>

Computer Forensics, Packet Analysis

## <ins>Task Description<ins>

Using the timestamp and IP address information from the VPN log, the FBI was able to identify a virtual server that the attacker used for staging their attack. They were able to obtain a warrant to search the server, but key files used in the attack were deleted.

Luckily, the company uses an intrusion detection system which stores packet logs. They were able to find an SSL session going to the staging server, and believe it may have been the attacker transferring over their tools.

The FBI hopes that these tools may provide a clue to the attacker's identity

## <ins>Provided Files<ins>

<ul>
<li>Files captured from root's home directory on the staging server (root.tar.bz2)</li>
<li>PCAP file believed to be of the attacker downloading their tools (session.pcap)</li>
</ul>

## <ins>Solution<ins>

### **1) Investigating root directory and session.pcap**

Looking at `session.pcap` in Wireshark we see a series of packets are TLSv1.2 encrypted. After an initial setup, many packets are sent from `172.29.245.14` (an IP address from one of the Task A1 overlapping sessions) on port `443` to `172.16.0.1` on port `56904`. This is probably the attacker transferring tools, so we look for a way to decrypt this traffic.

After unzipping `root.tar.bz2`, we find from `.bash_history` that the attacker unzipped some tools and ran a script called `runwww.py` with port 443 passed in. This script sets up a `.cert.pem` file and then uses it for a TLSv1.2 server. We have access to `.cert.pem` so we can use it to decrypt traffic in the pcap.

### **2) Extracting the attacker toolset**

In Wireshark, we go to `Edit > Preferences` and then select `TLS` under protocols. Clicking `Edit` near `RSA keys list` lets us add a private key to decrypt traffic. We add an entry with IP address `172.29.245.14`, port `443`, protocol `http`, and the `.cert.pem` file for Key file. This allows us to decrypt the traffic and view it in Wireshark.

Unfortunately, Wireshark does not seem to have a method for automatically exporting this decrypted traffic as a file like other HTTP objects. To get around this, we right click on the HTTP `GET /tools.tar HTTP/1.1` packet (number 12) and select `Follow > TLS STream`. In the new window we can then set `Show and save data as` to `Raw` and click `Save as` to save this data as a file called `raw_tools.tar`.

This saved file also has some bytes from the HTTP traffic that need to be removed. Specifically, 85 bytes need to be removed from the beginning. Using a quick python script (`fix_tools_tar.py`), this can be done leaving a valid `.tar` file. We finally extract the files from this tar for future use and then use the command `tar --list -v --file tools.tar` to list the contents and find the name of the attacker:

SoggyShySlice