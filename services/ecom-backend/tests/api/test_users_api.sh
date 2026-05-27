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

# Define user roles for testing
ADMIN_USER_ID=1      # Assumed admin user
NON_ADMIN_USER_ID="" # Will be created dynamically
NEW_USER_ID=""       # Will be created dynamically during the test

# Ensure created users are cleaned up from the DB under any exit status
cleanup() {
  if [ -n "${NEW_USER_ID}" ]; then
    echo "Cleaning up created test user with ID: ${NEW_USER_ID}..."
    curl -s -o /dev/null -X DELETE "${BASE_URL}/users/${NEW_USER_ID}" \
      -H "X-User-Id: ${ADMIN_USER_ID}"
  fi
  if [ -n "${NON_ADMIN_USER_ID}" ]; then
    echo "Cleaning up temporary non-admin user with ID: ${NON_ADMIN_USER_ID}..."
    curl -s -o /dev/null -X DELETE "${BASE_URL}/users/${NON_ADMIN_USER_ID}" \
      -H "X-User-Id: ${ADMIN_USER_ID}"
  fi
}
trap cleanup EXIT

echo "============================================"
echo " Setup: Create a temporary non-admin user"
echo "============================================"
# Create a non-admin user using the admin credentials
TEMP_USER=$(curl --fail-with-body -s -X POST "${BASE_URL}/users/" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: ${ADMIN_USER_ID}" \
  -d '{
    "first_name": "Temp",
    "last_name": "NonAdmin",
    "role": "user"
  }')

NON_ADMIN_USER_ID=$(echo "${TEMP_USER}" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo "Created Temporary Non-Admin User ID: ${NON_ADMIN_USER_ID}"

if [ -z "${NON_ADMIN_USER_ID}" ]; then
  echo "Error: Failed to create temporary non-admin user"
  exit 1
fi

echo ""
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
# User creation should fail with 403 Forbidden for non-admin
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/users/" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: ${NON_ADMIN_USER_ID}" \
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
# User creation should succeed with 201 Created for admin
CREATED_USER=$(curl --fail-with-body -s -X POST "${BASE_URL}/users/" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: ${ADMIN_USER_ID}" \
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
# User deletion should fail with 403 Forbidden for non-admin
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${BASE_URL}/users/${NEW_USER_ID}" \
  -H "Accept: application/json" \
  -H "X-User-Id: ${NON_ADMIN_USER_ID}")

echo "HTTP Status for non-admin delete: ${HTTP_STATUS} (Expected: 403)"
if [ "${HTTP_STATUS}" -ne 403 ]; then
  echo "Error: Expected 403 but got ${HTTP_STATUS}"
  exit 1
fi

echo ""
echo "============================================"
echo " DELETE /users/${NEW_USER_ID} — Delete user (should SUCCEED for admin)"
echo "============================================"
# User deletion should succeed with 200 OK for admin
DELETED_USER=$(curl --fail-with-body -s -X DELETE "${BASE_URL}/users/${NEW_USER_ID}" \
  -H "Accept: application/json" \
  -H "X-User-Id: ${ADMIN_USER_ID}")
echo "${DELETED_USER}" | python3 -m json.tool

# Clear NEW_USER_ID since it is successfully deleted from DB
NEW_USER_ID=""

echo ""
echo "============================================"
echo " Teardown: Delete temporary non-admin user"
echo "============================================"
DELETED_TEMP_USER=$(curl --fail-with-body -s -X DELETE "${BASE_URL}/users/${NON_ADMIN_USER_ID}" \
  -H "Accept: application/json" \
  -H "X-User-Id: ${ADMIN_USER_ID}")
echo "${DELETED_TEMP_USER}" | python3 -m json.tool

# Clear NON_ADMIN_USER_ID since it is successfully deleted from DB
NON_ADMIN_USER_ID=""




