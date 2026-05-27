#!/usr/bin/env bash
# Explore the Products API endpoints
# Prerequisites: ecom-backend service running on http://localhost:8000

BASE_URL="http://localhost:8000/api/v1"

echo "============================================"
echo " GET /products/ — List all products (page 1, limit 3)"
echo "============================================"
curl -s -X GET "${BASE_URL}/products/?page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/search?keywords=laptop — Keyword search"
echo "============================================"
curl -s -X GET "${BASE_URL}/products/search?keywords=laptop&page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/id/1 — Get product by ID"
echo "============================================"
curl -s -X GET "${BASE_URL}/products/id/1" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/category/id/1 — Products by category ID"
echo "============================================"
curl -s -X GET "${BASE_URL}/products/category/id/1?page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool

echo ""
echo "============================================"
echo " GET /products/search?category_slug=electronics — Filter by category slug"
echo "============================================"
curl -s -X GET "${BASE_URL}/products/search?category_slug=electronics&page=1&limit=3" \
  -H "Accept: application/json" | python3 -m json.tool
