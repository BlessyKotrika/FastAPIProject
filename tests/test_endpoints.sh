#!/bin/bash

# Configuration
API_URL="http://localhost:8000"
USER_ID="farmer_123"

echo "=== KhetiPulse AI Backend Testing Script ==="

# 1. Health Check
echo -e "\n1. Testing Health Check..."
curl -s "$API_URL/" | grep -q "healthy" && echo "✅ Success" || echo "❌ Failed"

# 2. Update Language Preference (Telugu)
echo -e "\n2. Updating Language Preference to Telugu..."
curl -s -X POST "$API_URL/preferences/language" \
     -H "Content-Type: application/json" \
     -d "{\"user_id\": \"$USER_ID\", \"language\": \"te\"}"

# 3. Get Today Action Cards (Hindi)
echo -e "\n3. Testing Today Action Cards (Hindi)..."
curl -s -X POST "$API_URL/today/" \
     -H "Content-Type: application/json" \
     -d "{
       \"user_id\": \"$USER_ID\",
       \"crop\": \"wheat\",
       \"location\": \"Barabanki\",
       \"sowing_date\": \"2025-11-01\",
       \"language\": \"hi\"
     }" | python3 -m json.tool | head -n 15

# 4. Sell Smart (Bengali)
echo -e "\n4. Testing Sell Smart (Bengali)..."
curl -s -X POST "$API_URL/sell-smart/" \
     -H "Content-Type: application/json" \
     -d "{
       \"crop\": \"wheat\",
       \"location\": \"Barabanki\",
       \"language\": \"bn\"
     }" | python3 -m json.tool

# 5. Ask KhetiPulse RAG Chat (Tamil)
echo -e "\n5. Testing Ask KhetiPulse RAG Chat (Tamil)..."
curl -s -X POST "$API_URL/chat/" \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"How to manage pests in paddy?\",
       \"language\": \"ta\",
       \"crop\": \"paddy\",
       \"location\": \"Guntur\"
     }" | python3 -m json.tool | head -n 15

# 6. Scheme Helper (Telugu)
echo -e "\n6. Testing Scheme Helper (Telugu)..."
curl -s -X POST "$API_URL/schemes/" \
     -H "Content-Type: application/json" \
     -d "{
       \"state\": \"Andhra Pradesh\",
       \"land_size\": 2.5,
       \"category\": \"Small\",
       \"crop\": \"paddy\",
       \"language\": \"te\"
     }" | python3 -m json.tool

echo -e "\n=== Testing Complete ==="
