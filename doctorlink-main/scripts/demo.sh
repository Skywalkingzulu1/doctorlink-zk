#!/usr/bin/env bash
set -euo pipefail

echo "=== DoctorLink ZK MVP Demo ==="
echo ""

echo "1. Compiling Noir circuits..."
cd circuits
nargo compile
cd ..

echo "2. Starting backend..."
cd doctorlink-health-services
python main.py &
BACKEND_PID=$!
sleep 2
cd ..

echo "3. Creating test patient..."
curl -s -X POST http://localhost:8001/api/v1/patients \
    -H "Content-Type: application/json" \
    -d '{"first_name":"Demo","last_name":"Patient","email":"demo@test.com","date_of_birth":"1998-05-12","gender":"female"}'

echo ""
echo "4. Creating test doctor..."
curl -s -X POST http://localhost:8001/api/v1/doctors \
    -H "Content-Type: application/json" \
    -d '{"first_name":"Alice","last_name":"Doctor","email":"alice@doctorlink.com","license_number":"DEMO-001-MD","specialization":"General"}'

echo ""
echo "5. Running age eligibility ZK proof..."
curl -s -X POST http://localhost:8001/api/v1/contraceptives \
    -H "Content-Type: application/json" \
    -d '{"patient_id":4,"contraceptive_type":"Oral Contraceptive Pill","brand_name":"Yasmin","start_date":"2026-07-01","offline":true}'

echo ""
echo "6. Running doctor credential ZK proof..."
curl -s -X POST http://localhost:8001/api/v1/verifications \
    -H "Content-Type: application/json" \
    -d '{"doctor_id":3,"verification_type":"Medical License","provider":"State Board","credential_data":"DEMO-001-MD","offline":true}'

echo ""
echo "7. Checking sync queue..."
curl -s http://localhost:8001/api/v1/sync/queue | python -m json.tool

echo ""
echo "=== Demo Complete! ==="
echo "Backend running at http://localhost:8001"
echo "Kill with: kill $BACKEND_PID"
