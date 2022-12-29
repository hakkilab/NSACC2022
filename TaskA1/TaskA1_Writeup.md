
# **Task A1 - Initial access**

## <ins>Topics:</ins>

Log analysis

## <ins>Task Description<ins>

We believe that the attacker may have gained access to the victim's network by phishing a legitimate users credentials and connecting over the company's VPN. The FBI has obtained a copy of the company's VPN server log for the week in which the attack took place. Do any of the user accounts show unusual behavior which might indicate their credentials have been compromised?

Note that all IP addresses have been anonymized.

## <ins>Provided Files<ins>

<ul>
<li>Access log from the company's VPN server for the week in question. (vpn.log)</li>
</ul>

## <ins>Solution<ins>

### **1) Searching for odd events**

We start by opening the vpn log to see what information it contains. A good first guess of odd activity would be finding user sessions that overlap. We make a script that parses through the vpn log keeping track of user vpn sessions with start and end times, and then print any sessions for a user that overlap in time (`parse_vpn.py`). This overlap only occurs for one user, with sessions from two different ip addressed overlapping. This gives us our answer for this task:

Judy.A