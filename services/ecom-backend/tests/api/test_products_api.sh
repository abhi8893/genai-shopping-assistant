#!/usr/bin/env bash
# Explore the Products API endpoints

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
echo " GET /products/ — List all products (page 1, limit 3)"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/products/?page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/search?keywords=laptop — Keyword search"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/products/search?keywords=laptop&page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/id/1 — Get product by ID"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/products/id/1" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/category/id/1 — Products by category ID"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/products/category/id/1?page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/search?category_slug=electronics — Filter by category slug"
echo "============================================"
curl --fail-with-body -s -X GET "${BASE_URL}/products/search?category_slug=electronics&page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool
