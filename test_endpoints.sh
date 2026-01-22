#!/bin/bash

BASE_URL="http://127.0.0.1:5000"
COOKIE_FILE="cookies.txt"

echo "---------------------------------------------------"
echo "1. Testing Registration (GET)"
curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/register"
echo -e "\nExpected: 200"

echo "---------------------------------------------------"
echo "2. Testing Registration (POST - New User 'curl_user')"
# Generating random suffix to avoid duplicates on re-runs
RAND=$((1 + $RANDOM % 1000))
USERNAME="curl_user_$RAND"
EMAIL="curl_$RAND@test.com"
curl -s -L -c $COOKIE_FILE -d "username=$USERNAME&email=$EMAIL&password=password" "$BASE_URL/register" -o /dev/null -w "%{http_code}"
echo -e "\nExpected: 200 (Redirects to Index)"

echo "---------------------------------------------------"
echo "3. Testing Login (POST)"
# Reset cookies to ensure clean login
rm $COOKIE_FILE
curl -s -L -c $COOKIE_FILE -d "username=$USERNAME&password=password" "$BASE_URL/login" -o /dev/null -w "%{http_code}"
echo -e "\nExpected: 200 (Redirects to Dashboard)"

echo "---------------------------------------------------"
echo "4. Testing Protected Dashboard Access"
curl -s -b $COOKIE_FILE "$BASE_URL/dashboard" -o /dev/null -w "%{http_code}"
echo -e "\nExpected: 200"

echo "---------------------------------------------------"
echo "5. Testing Add Book (POST)"
curl -s -L -b $COOKIE_FILE -d "title=Curl Book&author=Robot&category=Tech&type=Physical&location=Server Room" "$BASE_URL/add_book" -o /dev/null -w "%{http_code}"
echo -e "\nExpected: 200 (Redirects to Index)"

echo "---------------------------------------------------"
echo "6. Testing Public Index (List Books)"
# Check if our new book is there
CONTENT=$(curl -s "$BASE_URL/index")
if echo "$CONTENT" | grep -q "Curl Book"; then
    echo "SUCCESS: 'Curl Book' found in index."
else
    echo "FAILURE: 'Curl Book' not found."
fi

echo "---------------------------------------------------"
echo "7. Testing Admin Login"
# Reset cookies
rm $COOKIE_FILE
curl -s -L -c $COOKIE_FILE -d "username=admin&password=admin123" "$BASE_URL/login" -o /dev/null -w "%{http_code}"
echo -e "\nExpected: 200 (Redirects to Dashboard)"

echo "---------------------------------------------------"
echo "8. Testing Admin Dashboard Access"
curl -s -b $COOKIE_FILE "$BASE_URL/admin" -o /dev/null -w "%{http_code}"
echo -e "\nExpected: 200"

echo "---------------------------------------------------"
echo "Test Sequence Complete."
rm $COOKIE_FILE
