#!/bin/bash
stellar contract invoke \
  --id CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT \
  --network testnet \
  --source-account funded \
  -- initialize \
  --admin GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7 \
  --name "DoctorLink Health Token" \
  --symbol "DLHT"
