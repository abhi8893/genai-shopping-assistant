#!/usr/bin/env bash
# Explore the Carts API endpoints

# get port from 1st argument
PORT="$1"

# fallback to ECOM_API_PORT if not specified
if [ -z "$PORT" ] && [ -n "$ECOM_API_PORT" ]; then
  PORT="$ECOM_API_PORT"
fi

# raise error if port is still empty
if [ -z "$PORT" ]; then
  echo "Error: Port not specified. Please provide port as first argument or set ECOM_API_PORT environment variable."
  exit 1
fi

echo "Using port: ${PORT}"

BASE_URL="http://localhost:${PORT}/api/v1"
USER_ID=1

echo "============================================"
echo " GET /carts/ — List user's carts"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/carts/?page=1&limit=10" \
  -H "Accept: application/json" \
  -H "X-User-Id: ${USER_ID}" | python3 -m json.tool

echo ""
echo "============================================"
echo " POST /carts/ — Create a new cart"
echo "============================================"
CREATED_CART=$(curl --fail-with-body -s -X POST "${BASE_URL}/carts/" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: ${USER_ID}" \
  -d '{
    "cart_items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }')
echo "${CREATED_CART}" | python3 -m json.tool

CART_ID=$(echo "${CREATED_CART}" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")

echo ""
echo "============================================"
echo " GET /carts/${CART_ID} — Get cart by ID"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/carts/${CART_ID}" \
  -H "Accept: application/json" \
  -H "X-User-Id: ${USER_ID}" | python3 -m json.tool

echo ""
echo "============================================"
echo " PUT /carts/${CART_ID} — Update cart items"
echo "============================================"
curl --fail-with-body -s -X PUT "${BASE_URL}/carts/${CART_ID}" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: ${USER_ID}" \
  -d '{
    "cart_items": [
      {"product_id": 1, "quantity": 5}
    ]
  }' | python3 -m json.tool

echo ""
echo "============================================"
echo " DELETE /carts/${CART_ID} — Delete cart"
echo "============================================"
curl --fail-with-body -s -X DELETE "${BASE_URL}/carts/${CART_ID}" \
  -H "Accept: application/json" \
  -H "X-User-Id: ${USER_ID}" | python3 -m json.tool
