from collections import defaultdict
from csv import DictReader
import time

# read in data from vpn log file
with open("vpn.log", 'r') as f:
    data = list(DictReader(f))

# extract start and end times for each session and record for that user
users = defaultdict(list)
for session in data:
    start = time.mktime(time.strptime(session["Start Time"].replace("EDT", "-04:00"), "%Y.%m.%d %H:%M:%S %z"))
    end = start + int(session["Duration"] if session["Duration"] else 0)
    users[session["Username"]].append((start, end, session["Real Ip"]))

# print any users with sessions that overlap in time
for user, sessions in users.items():
    for i in range(1, len(sessions)):
        prev_start, prev_end, prev_ip = sessions[i-1]
        curr_start, curr_end, curr_ip = sessions[i]
        if curr_start < prev_end:
            print(user, prev_ip, curr_ip)
