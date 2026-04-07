#!/usr/bin/env bash
set -e
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <C> <O> <CN>"
  exit 1
fi

C=$1
O=$2
CN=$3
KEY=private.key
CSR=data-catalog.csr

if [ ! -f "$KEY" ]; then
  echo "Generating 2048-bit RSA private key → $KEY"
  openssl genpkey -algorithm RSA -out "$KEY" -pkeyopt rsa_keygen_bits:2048
else
  echo "Using existing private key: $KEY"
fi

echo "Creating CSR → $CSR"
openssl req -new -key "$KEY" -out "$CSR" \
  -subj "/C=${C}/O=${O}/CN=${CN}"

echo "✔ CSR written to $CSR"