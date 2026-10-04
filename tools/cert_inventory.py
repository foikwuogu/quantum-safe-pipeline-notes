#!/usr/bin/env python3
"""cert_inventory.py - build a quantum-readiness inventory from X.509 certificates.

Companion to the post "What EO 14412 means for a pipeline operator's certificate inventory".

Reads every PEM/DER/CRT/CER file under a folder (certificates exported from HMIs,
historians, OPC UA trust lists, VPN gateways, AD CS, vendor portals), and writes one
CSV row per certificate with the fields the post recommends tracking.

It never connects to a device. Collect certificates by export or passive capture first.

Usage:
    pip install cryptography
    python cert_inventory.py ./exported_certs inventory.csv

License: MIT
"""
import csv
import datetime as dt
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import dsa, ec, ed448, ed25519, rsa

# NIST CSOR object identifiers for the FIPS 204/205 signature algorithms.
PQC_SIG_OIDS = {
    "2.16.840.1.101.3.4.3.17": "ML-DSA-44",
    "2.16.840.1.101.3.4.3.18": "ML-DSA-65",
    "2.16.840.1.101.3.4.3.19": "ML-DSA-87",
}
PQC_SIG_OIDS.update({f"2.16.840.1.101.3.4.3.{n}": "SLH-DSA" for n in range(20, 32)})

EO_SIGNATURE_DEADLINE = dt.datetime(2031, 12, 31, tzinfo=dt.timezone.utc)

FIELDS = [
    "file", "subject", "issuer", "self_signed", "is_ca", "public_key_alg", "key_size",
    "signature_alg", "not_before", "not_after", "lifetime_years",
    "outlives_2031_signature_deadline", "quantum_vulnerable", "priority",
    # Filled in by hand: the parts no parser can know.
    "asset_or_location", "zone_or_purdue_level", "critical_cyber_system",
    "renewal_owner", "can_change_algorithm", "notes",
]


def load(path: Path):
    data = path.read_bytes()
    certs = []
    if b"-----BEGIN CERTIFICATE-----" in data:
        try:
            certs = x509.load_pem_x509_certificates(data)
        except ValueError:
            pass
    else:
        try:
            certs = [x509.load_der_x509_certificate(data)]
        except ValueError:
            pass
    return certs


def key_info(cert):
    try:
        pk = cert.public_key()
    except Exception:  # unknown key type, e.g. a PQC key this library cannot parse
        oid = cert.signature_algorithm_oid.dotted_string
        return PQC_SIG_OIDS.get(oid, "unknown"), ""
    if isinstance(pk, rsa.RSAPublicKey):
        return "RSA", pk.key_size
    if isinstance(pk, ec.EllipticCurvePublicKey):
        return f"ECDSA-{pk.curve.name}", pk.key_size
    if isinstance(pk, ed25519.Ed25519PublicKey):
        return "Ed25519", 256
    if isinstance(pk, ed448.Ed448PublicKey):
        return "Ed448", 456
    if isinstance(pk, dsa.DSAPublicKey):
        return "DSA", pk.key_size
    return type(pk).__name__, ""


def sig_name(cert):
    oid = cert.signature_algorithm_oid
    return PQC_SIG_OIDS.get(oid.dotted_string, getattr(oid, "_name", oid.dotted_string))


def row(path, cert):
    alg, size = key_info(cert)
    sig = sig_name(cert)
    nb, na = cert.not_valid_before_utc, cert.not_valid_after_utc
    try:
        is_ca = cert.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    except x509.ExtensionNotFound:
        is_ca = False
    pqc = alg.startswith(("ML-DSA", "SLH-DSA")) or sig.startswith(("ML-DSA", "SLH-DSA"))
    outlives = na > EO_SIGNATURE_DEADLINE
    if pqc:
        priority = "C - already PQC"
    elif is_ca or outlives:
        priority = "A - long-lived trust anchor or outlives 2031"
    else:
        priority = "B - quantum-vulnerable, replace on renewal"
    return {
        "file": str(path),
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "self_signed": cert.subject == cert.issuer,
        "is_ca": is_ca,
        "public_key_alg": alg,
        "key_size": size,
        "signature_alg": sig,
        "not_before": nb.date().isoformat(),
        "not_after": na.date().isoformat(),
        "lifetime_years": round((na - nb).days / 365.25, 1),
        "outlives_2031_signature_deadline": outlives,
        "quantum_vulnerable": not pqc,
        "priority": priority,
    }


def main(folder, out):
    rows = []
    for p in sorted(Path(folder).rglob("*")):
        if p.is_file() and p.suffix.lower() in {".pem", ".crt", ".cer", ".der"}:
            for c in load(p):
                rows.append(row(p, c))
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    a = sum(r["priority"].startswith("A") for r in rows)
    print(f"{len(rows)} certificates -> {out}; {a} flagged priority A")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: cert_inventory.py <cert_folder> <out.csv>")
    main(sys.argv[1], sys.argv[2])
