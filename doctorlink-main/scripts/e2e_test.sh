#!/bin/bash
# End-to-end test: Store a verification on-chain
set -e

echo "=== Storing verification on-chain ==="
stellar contract invoke \
  --id CC3D4TOHNYZUTMENJN4OUQRIEMHD4TNIGJ6RYHMLQ4M4FQFTNWSR2WBY \
  --network testnet \
  --source-account funded \
  --send=yes \
  -- store_verification \
  --circuit AgeEligibility \
  --proof_hash '"e2e-test-proof-hash"' \
  --public_inputs '["1","1"]' \
  --verified true

echo ""
echo "=== Retrieving last verification ==="
stellar contract invoke \
  --id CC3D4TOHNYZUTMENJN4OUQRIEMHD4TNIGJ6RYHMLQ4M4FQFTNWSR2WBY \
  --network testnet \
  --source-account funded \
  --send=yes \
  -- get_last_verification

echo ""
echo "=== E2E test complete ==="
