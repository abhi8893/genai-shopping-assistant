# Explore the Users API endpoints
# Prerequisites: ecom-backend service running on http://localhost:${ECOM_API_PORT}

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

echo "============================================"
echo " GET /users/ — List all users (paginated)"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/users/?page=1&limit=5" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /users/1 — Get user by ID"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/users/1" \
  -H "Accept: application/json" | python3 -m json.tool
