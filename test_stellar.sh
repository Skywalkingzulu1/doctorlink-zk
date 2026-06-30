#!/bin/bash
set -e
stellar contract invoke \
  --id CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2 \
  --network testnet \
  --source-account funded \
  --send=yes \
  -- \
  store_verification \
  --circuit LicenseVerify \
  --proof_hash test123 \
  --public_inputs '["0100000000000000000000000000000000000000000000000000000000000000","0100000000000000000000000000000000000000000000000000000000000000"]' \
  --verified true
echo "---DONE---"
