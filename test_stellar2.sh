#!/bin/bash
set -e
CMD='stellar contract invoke --id CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2 --network testnet --source-account funded --send=yes -- store_verification --circuit LicenseVerify --proof_hash "f5c85e2a41824ce34d064e6b00181fc14b7db5534033696e6b48e26d60f8b11f" --public_inputs '"'"'["5bb2ffa105d865d5000000000000000000000000000000000000000000000000","0100000000000000000000000000000000000000000000000000000000000000"]'"'"' --verified true'
echo "Running: $CMD"
eval "$CMD"
echo "---DONE---"
