import jwt
from datetime import datetime, timedelta

# define old token and key needed to decode/encode
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NTM2NjkzNTgsImV4cCI6MTY1NjI2MTM1OCwic2VjIjoiS0h0a3dRY0xleWlHYVdlU1MyTENuMVBRNWJ5OG41RzgiLCJ1aWQiOjQ1MjA0fQ.fMH-Jg66VIjKW6fCLToeSTaW4IV6kP2nqtWedGfzSRE"
hmac = "mvaVXwNo7sMKvDvIGxhNrsNfQUq6jYIu"

# decode old token and replace issued at time and expiration time
claims = jwt.decode(token, hmac, algorithms=["HS256"], options={'verify_exp': False})
claims['iat'] = datetime.now()
claims['exp'] = datetime.now() + timedelta(days=365)

# print new token
print(jwt.encode(claims, hmac, algorithm='HS256'))