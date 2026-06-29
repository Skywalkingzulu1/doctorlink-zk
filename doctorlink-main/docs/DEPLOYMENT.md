# DoctorLink Smart Contract Deployment Guide

This guide explains how to compile, deploy, fund, and connect the DoctorLink Soroban smart contracts to Stellar Testnet.

## Prerequisites

```bash
rustup target add wasm32-unknown-unknown
cargo install --locked stellar-cli --features opt
```

## Step 1: Compile Contracts

```bash
cd contracts
cargo build --target wasm32-unknown-unknown --release
```

Output:
- `contracts/target/wasm32-unknown-unknown/release/doctorlink_verifier.wasm`
- `contracts/target/wasm32-unknown-unknown/release/doctorlink_token.wasm`

## Step 2: Configure & Fund Testnet Account

```bash
# Create identity
stellar keys generate --network testnet clinic_admin
# Get address
stellar keys address clinic_admin
# Fund via Friendbot
curl "https://friendbot.stellar.org/?addr=<PUBLIC_ADDRESS>"
# Get secret key
stellar keys show-secret-key clinic_admin
```

## Step 3: Deploy

```bash
# Deploy verifier
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/doctorlink_verifier.wasm \
  --source clinic_admin --network testnet

# Deploy token
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/doctorlink_token.wasm \
  --source clinic_admin --network testnet
```

## Step 4: Configure Backend

```ini
# doctorlink-health-services/.env
STELLAR_NETWORK=testnet
ZK_VERIFIER_CONTRACT=<VERIFIER_CONTRACT_ID>
STELLAR_SECRET_KEY=<SECRET_KEY_S...>
```

## Step 5: Initialize Token

```bash
stellar contract invoke \
  --id <TOKEN_CONTRACT_ID> \
  --source clinic_admin --network testnet \
  -- initialize \
  --admin <ADMIN_PUBLIC_KEY> \
  --name "DoctorLink Health" \
  --symbol "DLH"
```
