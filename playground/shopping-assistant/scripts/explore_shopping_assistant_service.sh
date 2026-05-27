#!/usr/bin/env bash
# Multi-turn conversation exploring all four agents (user_id=1, thread_id=1)

BASE_URL="http://localhost:8010"
USER_ID="1"
THREAD_ID="1"

send() {
  local label="$1"
  local query="$2"
  echo "=============================="
  echo ">>> $label"
  echo "Query: $query"
  echo "Response:"
  curl -s -X POST "$BASE_URL/chat" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"$USER_ID\", \"query\": \"$query\", \"thread_id\": \"$THREAD_ID\"}" | python3 -m json.tool
  echo ""
}

# --- customer_service ---
send "Turn 1 — CustomerServiceAgent (greeting)" \
  "Hello!"

# --- product_search ---
send "Turn 2 — ProductSearchAgent (product discovery)" \
  "I am looking for black sunglasses under 100 dollars"

# --- shopping_actions ---
send "Turn 3 — ShoppingActionsAgent (add to cart)" \
  "Can you add the first one to my cart?"

# --- customer_service ---
send "Turn 4 — CustomerServiceAgent (return policy)" \
  "What is your return policy?"
