#!/usr/bin/env bash
# Explore the Users API endpoints
# Prerequisites: ecom-backend service running on http://localhost:${ECOM_API_PORT}

BASE_URL="http://localhost:${ECOM_API_PORT}/api/v1"

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
