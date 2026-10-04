"""Model the cryptographic payload of a TLS 1.3 handshake over narrowband SCADA links.
Used by issue 05. Counts only key-share, public-key and signature bytes (no DER, record or
link-layer overhead), so every figure is a lower bound. Sizes: FIPS 203, FIPS 204, RFC 8446/7748,
X25519MLKEM768 key shares per draft-ietf-tls-ecdhe-mlkem. Async serial framing = 10 bits per byte."""
import json
from pathlib import Path

KEX = {  # client share, server share (bytes)
    "X25519": (32, 32),
    "X25519MLKEM768 (hybrid)": (32 + 1184, 32 + 1088),
}
AUTH = {  # public key bytes, signature bytes
    "ECDSA P-256": (65, 64),
    "ML-DSA-44": (1312, 2420),
    "ML-DSA-65": (1952, 3309),
}
RATES = [1200, 9600, 19200, 64000]

def auth_bytes(alg, mutual):
    pk, sig = AUTH[alg]
    # per side: leaf cert carries pk + CA signature; CertificateVerify carries one signature
    one = pk + sig + sig
    return one * (2 if mutual else 1)

rows = []
for kex, (c, s) in KEX.items():
    for alg in AUTH:
        if kex.startswith("X25519 ") or kex == "X25519":
            if alg != "ECDSA P-256":
                continue
        total = c + s + auth_bytes(alg, mutual=True)
        row = {"key_exchange": kex, "signature": alg, "mutual_tls_crypto_bytes": total}
        for r in RATES:
            row[f"secs_at_{r}bps_async"] = round(total * 10 / r, 2)
        rows.append(row)

out = {"rows": rows, "rates_bps": RATES,
       "note": "lower bound: crypto payload only, mutual TLS, no chain beyond leaf, no retries"}
Path(__file__).with_name("radio_model.json").write_text(json.dumps(out, indent=2))
for r in rows:
    print(f"{r['key_exchange']:26s} {r['signature']:12s} {r['mutual_tls_crypto_bytes']:6d} B  "
          + "  ".join(f"{k.split('_')[2]}:{v}s" for k, v in r.items() if k.startswith("secs")))
