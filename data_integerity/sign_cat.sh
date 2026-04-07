#!/usr/bin/env bash
set -e
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <data-catalog.ttl> <output-signature>"
  exit 1
fi

FILE=$1
OUT=$2
KEY=private.key

echo "Signing '$FILE' with SHA-256 private key → binary signature"
openssl dgst -sha256 -sign "$KEY" -out sig.bin "$FILE"

echo "Encoding signature to Base64 → $OUT"
openssl base64 -in sig.bin -out "$OUT"

rm sig.bin
echo "✔ Signature written to $OUT"
