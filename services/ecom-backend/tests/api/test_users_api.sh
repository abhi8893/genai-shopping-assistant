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

echo ""
echo "============================================"
echo " POST /users/ — Create user (should FAIL for non-admin)"
echo "============================================"
# User 1 (John Doe) has role 'user'
# User creation should fail with 403 Forbidden.
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/users/" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d '{
    "first_name": "Charlie",
    "last_name": "Brown",
    "role": "user"
  }')

echo "HTTP Status for non-admin: ${HTTP_STATUS} (Expected: 403)"
if [ "${HTTP_STATUS}" -ne 403 ]; then
  echo "Error: Expected 403 but got ${HTTP_STATUS}"
  exit 1
fi

echo ""
echo "============================================"
echo " POST /users/ — Create user (should SUCCEED for admin)"
echo "============================================"
# User 2 (Jane Smith) has role 'admin'
# User creation should succeed with 201 Created.
CREATED_USER=$(curl --fail-with-body -s -X POST "${BASE_URL}/users/" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 2" \
  -d '{
    "first_name": "Charlie",
    "last_name": "Brown",
    "role": "user"
  }')
echo "${CREATED_USER}" | python3 -m json.tool

NEW_USER_ID=$(echo "${CREATED_USER}" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo "Created User ID: ${NEW_USER_ID}"

if [ -z "${NEW_USER_ID}" ]; then
  echo "Error: Failed to parse created user ID"
  exit 1
fi

echo ""
echo "============================================"
echo " DELETE /users/${NEW_USER_ID} — Delete user (should FAIL for non-admin)"
echo "============================================"
# User 1 (John Doe) has role 'user'
# User deletion should fail with 403 Forbidden.
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${BASE_URL}/users/${NEW_USER_ID}" \
  -H "Accept: application/json" \
  -H "X-User-Id: 1")

echo "HTTP Status for non-admin delete: ${HTTP_STATUS} (Expected: 403)"
if [ "${HTTP_STATUS}" -ne 403 ]; then
  echo "Error: Expected 403 but got ${HTTP_STATUS}"
  exit 1
fi

echo ""
echo "============================================"
echo " DELETE /users/${NEW_USER_ID} — Delete user (should SUCCEED for admin)"
echo "============================================"
# User 2 (Jane Smith) has role 'admin'
# User deletion should succeed with 200 OK.
DELETED_USER=$(curl --fail-with-body -s -X DELETE "${BASE_URL}/users/${NEW_USER_ID}" \
  -H "Accept: application/json" \
  -H "X-User-Id: 2")
echo "${DELETED_USER}" | python3 -m json.tool


