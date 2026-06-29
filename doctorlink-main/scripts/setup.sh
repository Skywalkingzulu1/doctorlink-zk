#!/usr/bin/env bash
set -euo pipefail

echo "=== DoctorLink ZK MVP Setup ==="

echo "1. Installing Rust toolchain..."
rustup target add wasm32-unknown-unknown

echo "2. Installing Stellar CLI..."
cargo install --locked stellar-cli --features opt

echo "3. Installing Noir..."
if ! command -v nargo &> /dev/null; then
    curl -L https://raw.githubusercontent.com/noir-lang/noirup/main/install | bash
    noirup
fi

echo "4. Installing Python dependencies..."
pip install -r ../doctorlink-health-services/requirements.txt

echo "5. Compiling Soroban contracts..."
cd contracts
cargo build --target wasm32-unknown-unknown --release
cd ..

echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. cd doctorlink-health-services && cp .env.example .env"
echo "  2. Run: python main.py"
echo "  3. See scripts/deploy.sh to deploy contracts to Stellar testnet"
