
# **Task 6 - Gaining Access**

## <ins>Topics:</ins>

Web Hacking, [redacted]

## <ins>Task Description<ins>

We've found the login page on the ransomware site, but we don't know anyone's username or password. Luckily, the file you recovered from the attacker's computer looks like it could be helpful.

Generate a new token value which will allow you to access the ransomware site.

## <ins>Provided Files<ins>

None

## <ins>Solution<ins>

### **1) Generating a new token**

The token from the last task is a JSON Web Token. Looking at the source code we found we see that in `util.py` the token is decoded with a static HMAC key `mvaVXwNo7sMKvDvIGxhNrsNfQUq6jYIu` using the algorithm `HS256`. Attempting to decode using these settings fails since the token is expired, so the expiration must be explicitly ignored.

We can also see in `util.py` then when a new token is generated, the token contains information on issue time `iat`, expiration time `exp`, user secret `sec`, and user id `uid`. Of these, only `iat` and `exp` need to be replaced to generate a token that will no longer give an expiration error.

Using a python script (`generate_new_token.py`) we can create a new token with an updated `iat` and `exp`. We can check this works by adding a cookie with the name `tok` in the Developer tools of a browser under the Storage tab and going to https://padytccfzhyzlaza.ransommethis.net/nukoscislzmqpewx/

<img src='token_auth.png'>

Access with this token works, so we have the answer:

eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NjE0MjU4MzMsImV4cCI6MTY5Mjk2MTg2MSwic2VjIjoiS0h0a3dRY0xleWlHYVdlU1MyTENuMVBRNWJ5OG41RzgiLCJ1aWQiOjQ1MjA0fQ.z2f5C3mFmM_x53L3pBvDpe-kr47BxblQGagjZQ656aw