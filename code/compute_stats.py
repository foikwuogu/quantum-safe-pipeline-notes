"""Compute every number quoted in the posts and write stats.json.
Sizes are from FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA); dates from EO 14412 (signed 2026-06-22)."""
import json, datetime as dt
signed = dt.date(2026, 6, 22)
day = lambda n: (signed + dt.timedelta(days=n)).isoformat()
mlkem768 = {"ek": 1184, "ct": 1088}      # FIPS 203 Table 3 (bytes)
mldsa65 = {"pk": 1952, "sig": 3309}       # FIPS 204 Table 2 (bytes)
x25519 = {"pk": 32, "share": 32}
def secs(nbytes, bps): return round(nbytes * 8 / bps, 2)
kem_bytes = mlkem768["ek"] + mlkem768["ct"]
hybrid_bytes = kem_bytes + x25519["pk"] + x25519["share"]
stats = {
  "eo_signed": signed.isoformat(),
  "eo_day30": day(30), "eo_day90": day(90), "eo_day180": day(180), "eo_day270": day(270),
  "mlkem768_exchange_bytes": kem_bytes,
  "x25519_exchange_bytes": x25519["pk"] + x25519["share"],
  "hybrid_exchange_bytes": hybrid_bytes,
  "kem_ratio_vs_x25519": round(kem_bytes / 64),
  "mlkem768_secs_9600bps": secs(kem_bytes, 9600),
  "mlkem768_secs_19200bps": secs(kem_bytes, 19200),
  "x25519_secs_9600bps": secs(64, 9600),
  "mldsa65_pk_plus_sig_bytes": mldsa65["pk"] + mldsa65["sig"],
  "mldsa65_secs_9600bps": secs(mldsa65["pk"] + mldsa65["sig"], 9600),
}
json.dump(stats, open(__import__("pathlib").Path(__file__).with_name("stats.json"), "w"), indent=2)
print(json.dumps(stats, indent=2))
