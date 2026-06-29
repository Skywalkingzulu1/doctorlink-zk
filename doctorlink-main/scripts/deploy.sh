#!/usr/bin/env bash
set -euo pipefail

echo "=== DoctorLink Contract Deployment to Stellar Testnet ==="

NETWORK="testnet"
IDENTITY="clinic_admin"

echo "1. Generating identity '$IDENTITY'..."
stellar keys generate --network $NETWORK $IDENTITY 2>/dev/null || echo "Identity already exists"

PUBLIC_KEY=$(stellar keys address $IDENTITY)
echo "   Public key: $PUBLIC_KEY"

echo "2. Funding account via Friendbot..."
curl -s "https://friendbot.stellar.org/?addr=$PUBLIC_KEY" > /dev/null
echo "   Funded."

echo "3. Deploying verifier contract..."
VERIFIER_ID=$(stellar contract deploy \
    --wasm contracts/target/wasm32-unknown-unknown/release/doctorlink_verifier.wasm \
    --source $IDENTITY \
    --network $NETWORK)
echo "   Verifier contract ID: $VERIFIER_ID"

echo "4. Deploying token contract..."
TOKEN_ID=$(stellar contract deploy \
    --wasm contracts/target/wasm32-unknown-unknown/release/doctorlink_token.wasm \
    --source $IDENTITY \
    --network $NETWORK)
echo "   Token contract ID: $TOKEN_ID"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Add these to your .env file:"
echo "  ZK_VERIFIER_CONTRACT=$VERIFIER_ID"
echo ""
echo "Get your secret key:"
echo "  stellar keys show-secret-key $IDENTITY"
