
# **Task 7 - Privilege Escalation**

## <ins>Topics:</ins>

Web Hacking, [redacted]

## <ins>Task Description<ins>

With access to the site, you can access most of the functionality. But there's still that admin area that's locked off.

Generate a new token value which will allow you to access the ransomware site as an administrator.

## <ins>Provided Files<ins>

None

## <ins>Solution<ins>

### **1) Searching for a vulnerability**

Once we gain access to the website, the first thing we need to look for is an admin to compromise. Going to the Admin List tab at https://padytccfzhyzlaza.ransommethis.net/nukoscislzmqpewx/adminlist we see there is one active admin, `SedateImpropriety`. In order to make a token for this admin, we will need the admin's secret and user id.

Looking through the source code for the site, we notice that in `server.py` in the `userinfo` function, a database is queried for user information. This database query is based on the `user` query parameter of the GET request, and this input is not properly sanitized, rather just being placed in the SQL string directly. This means there is a SQL injection vulnerability we can exploit. To confirm this, we can 

Looking more at the `userinfo` function we see that this is for the User Info tab in the website. The database is queried for the `memberSince`, `clientsHelped`, `hackersHelped`, `programsContributed` columns from the `UserInfo` table for the queried user. These values are all cast to integers, meaning any text values from a `SELECT` will result in an error. Further, the first value from the `SELECT` (`memberSince`) is converted to a date, so we can likely only get three useful pieces of information per query.

### **2) Exploiting the SQL injection vulnerability**

We can test that an SQL injection indeed exists by using the query string `' UNION SELECT isAdmin, uid, uid, isAdmin FROM Accounts WHERE userName = 'SedateImpropriety'--` which will make the original `SELECT` be empty and then fill the data in with values for `isAdmin` (should be true or 1 for `SedateImpropriety`) and the `uid ` of `SedateImpropriety`. This indeed is the case when we navigate to https://padytccfzhyzlaza.ransommethis.net/nukoscislzmqpewx/userinfo?user=%27%20UNION%20SELECT%20isAdmin,%20uid,%20uid,%20isAdmin%20FROM%20Accounts%20WHERE%20userName%20=%20%27SedateImpropriety%27--

<img src='test_injection.png'>

This proof of concept gets us the `uid` of `SedateImpropriety`, `20270`.

We also need the secret to generate a token. Using another injection query `' UNION SELECT isAdmin, uid, uid, LENGTH(secret) FROM Accounts WHERE TYPEOF(secret) = 'text' AND userName = 'SedateImpropriety'--`, we find that the secret is a text type and has 32 characters. Since values from our query will be cast to integers, we can not directly get the string. However, we can take one character from the secret using `SUBSTR` and convert it to a Unicode value using `UNICODE`, which will make it past the integer casting, and we can build the secret a few characters at a time. A proof of concept of this is the query `' UNION SELECT isAdmin, uid, uid, UNICODE(SUBSTR(secret, 1, 1) FROM Accounts WHERE userName = 'SedateImpropriety'--`, which gives a Unicode value of `112`, which is `p`.

### **3) Generating an admin token**

Using these SQL injection queries, we can run a python script (`generate_admin_token.py`) which uses SQL injection and HTML parsing to extract the `uid` and `secret` (which happens to be `pbiMhO8Ea7SByDgfD84gaUpgxMvhECH6`) for `SedateImpropriety` and then generates a JSON Web Token for this admin. The resulting token is used to replace the `tok` cookie from the last part, and indeed gives admin access.

<img src='admin_access.png'>

This means the answer for this part is:

eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NjE0MzUyNDEsImV4cCI6MTY5Mjk3MTI0MSwic2VjIjoicGJpTWhPOEVhN1NCeURnZkQ4NGdhVXBneE12aEVDSDYiLCJ1aWQiOjIwMjcwfQ.zUI2elH6WFg3j52iG8j2ZWRB0QqakdRNPdwJEnqn8UE