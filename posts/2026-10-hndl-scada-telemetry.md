---
title: "Harvest-now-decrypt-later for SCADA telemetry"
series_slot: October 2026
issue: 2
published: "2026-10-03"
author: Friday Ogochukwu Ikwuogu
license: CC BY 4.0
status: published
doi: "10.5281/zenodo.23130292"
---

# Harvest-now-decrypt-later for SCADA telemetry

Executive Order 14412 opens by naming the threat that makes post-quantum migration urgent before any quantum computer exists: adversaries recording encrypted U.S. data today so they can decrypt it once a cryptographically relevant quantum computer is available. Security people call it harvest-now-decrypt-later, or HNDL.

HNDL is usually discussed in terms of diplomatic cables, health records, and trade secrets. This post asks a narrower question: does it matter for the telemetry that moves between a pipeline control center and its field sites? My answer is yes, but not where most people look first, and not before a more basic problem.

## First, the uncomfortable baseline

HNDL assumes the traffic is encrypted. A great deal of SCADA telemetry is not. Modbus and DNP3 were designed for closed serial networks, and many links still carry them in cleartext, sometimes inside a VPN tunnel across the WAN, sometimes not even that. For cleartext links the threat model is simpler and worse: harvest now, read now. No quantum computer required.

So the first-order fix is still the old one: encrypt and authenticate the links that are not. The quantum question changes *how* you should do that, because every link you encrypt this year with classical key exchange becomes a link an adversary can record and set aside.

## Where the vulnerable math sits in a telemetry path

Quantum attacks threaten the public-key parts of a protocol, the parts that agree on keys and prove identity. The symmetric parts that actually encrypt the bulk data (AES) and authenticate messages (HMAC) are only modestly weakened, and NIST continues to treat AES with 128-bit and larger keys as acceptable. In a typical pipeline telemetry path, the public-key exposure sits in:

- **WAN VPNs** (IPsec with IKEv2), where Diffie-Hellman or elliptic-curve Diffie-Hellman sets up the tunnel keys.
- **TLS** wrapping DNP3 or IEC 60870-5-104 under IEC 62351-3, and TLS to cloud historians and MQTT brokers.
- **OPC UA secure channels**, whose standard security policies use RSA or elliptic curves for key agreement and signatures.
- **Cellular and satellite backhaul**, where the carrier or vendor IPsec configuration decides the algorithms.
- **DNP3 Secure Authentication**, whose session keys are symmetric (HMAC) but whose optional asymmetric update-key change method in IEEE 1815-2012 relies on classical public-key cryptography.

An adversary who records the handshake and the session today can, with a sufficiently capable quantum computer later, recover the session key from the handshake and read everything that followed.

## The shelf-life test

The useful tool here is Michele Mosca's inequality. Let **x** be how long the data must stay confidential, **y** how long your migration will take, and **z** how long until a cryptographically relevant quantum computer exists. If x + y is greater than z, data you send today is already at risk.

Nobody knows z. The federal deadlines in EO 14412 (2030 for key establishment, 2031 for signatures) and NIST's proposed transition schedule in NIST IR 8547 (released as an initial public draft in November 2024: RSA and elliptic-curve algorithms at the 112-bit security level deprecated after 2030, and all of them disallowed after 2035) tell you where the government has placed its bet. For an operator, y is the number you control, and for field equipment it is measured in years.

Applying x to telemetry is where judgment comes in. Here is how I classify it:

| What crosses the link | How long it stays sensitive (x) | HNDL concern |
|---|---|---|
| Individual pressure, flow, and temperature readings | Minutes to hours | Low on its own |
| Aggregated operating history (normal envelopes, setpoints, seasonal patterns, compressor run profiles) | Years | Moderate: reveals how the system behaves and where its margins are |
| Network and asset detail visible in traffic (device addresses, models, firmware versions, polling schedules) | Years, until the equipment is replaced | High: a map for a future intrusion |
| Credentials, keys, and engineering files sent over the link (logins, configuration downloads, ladder logic) | As long as they remain valid | Highest: a recorded password that is never rotated is a future login |
| Commercial data (nominations, custody-transfer measurement) | Months to years | Moderate |


The pattern is that the single reading is rarely the prize. The prize is the accumulated picture, and anything in the stream that stays valid for years.

## Integrity is a different clock

HNDL is a confidentiality problem. The more dangerous failure for a pipeline is integrity: a forged command or forged firmware. Forging a signature requires the quantum capability at the moment of attack, so it is not a "harvest now" risk. But it has its own long tail: a firmware-signing key or root certificate deployed today may still be trusted by field devices when that capability arrives. That is why the previous issue put long-lived trust anchors at the top of the certificate inventory.

## OT bandwidth makes this an engineering problem, not a checkbox

Post-quantum key exchange is not free on narrow links. Using the sizes in FIPS 203:

- An ML-KEM-768 exchange (encapsulation key plus ciphertext) moves **2,272 bytes**; a classical X25519 exchange moves **64 bytes**, about **36 times** less.
- On a 9,600 bps serial radio, that ML-KEM payload alone takes about **1.89 seconds** to transmit, against roughly **0.05 seconds** for X25519, before protocol overhead or retries. At 19,200 bps it is about **0.95 seconds**.
- Signatures are larger still. An ML-DSA-65 public key plus one signature (FIPS 204) is **5,261 bytes**, about **4.38 seconds** at 9,600 bps.

On a fiber or LTE link these are rounding errors. On a licensed radio polling dozens of remote sites, they change poll cycles. The practical implications: do key establishment rarely and rekey symmetric sessions in between; terminate post-quantum tunnels at the most capable hop instead of at every RTU; and test on the actual link before committing to a design.

## What to do now, in order

1. **Close the cleartext gap.** Inventory links that carry SCADA protocols without encryption or authentication. That is today's exposure, quantum or not.
2. **Prefer hybrid key exchange when you encrypt.** Hybrid schemes combine a classical algorithm with ML-KEM, so a link is at least as strong as the stronger of the two. The TLS 1.3 hybrid group X25519MLKEM768 ships in OpenSSL 3.5 and is on by default in major browsers, and IKEv2 has standards for adding post-quantum protection (RFC 8784 for mixing in pre-shared keys; RFC 9370 for multiple key exchanges). Support in OT gateways and field devices varies, so check each product.
3. **Use AES-256 for long-lived links.** It is cheap insurance and matches NSA's CNSA 2.0 suite.
4. **Shrink what is worth harvesting.** Keep engineering downloads and credential exchange off long-haul links where possible, rotate credentials that cross them, and avoid static secrets that never change.
5. **Rank links by shelf life, not by bandwidth.** The link carrying configuration files and remote-access sessions deserves post-quantum protection before the link carrying a single tank level.
6. **Put the question to vendors and carriers.** Which key-exchange algorithms do your VPN, cellular, and satellite products negotiate, and when will hybrid ML-KEM be supported?

Telemetry is not the crown jewel of a pipeline. But the traffic around it, the maps, credentials, and accumulated operating history, is exactly what someone patient would want to keep. The time to decide which links matter is before the recording becomes readable.

---

*Views are my own and do not represent any employer or client. This post uses only public sources and contains no non-public operator information. Byte counts and transmission times are computed in [`code/compute_stats.py`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/code/compute_stats.py) from the published FIPS parameter sets and exclude protocol overhead.*

**Sources**

- The White House, [Securing the Nation Against Advanced Cryptographic Attacks (EO 14412)](https://www.whitehouse.gov/presidential-actions/2026/06/securing-the-nation-against-advanced-cryptographic-attacks/), June 22, 2026, Section 1.
- NIST, FIPS 203, *Module-Lattice-Based Key-Encapsulation Mechanism Standard*, August 2024.
- NIST, FIPS 204, *Module-Lattice-Based Digital Signature Standard*, August 2024.
- NIST, IR 8547 (initial public draft), *Transition to Post-Quantum Cryptography Standards*, November 2024.
- IETF, RFC 8784, *Mixing Preshared Keys in IKEv2 for Post-quantum Security*, 2020; RFC 9370, *Multiple Key Exchanges in IKEv2*, 2023.
- NSA, *Commercial National Security Algorithm Suite 2.0* (CNSA 2.0).
- M. Mosca, "Cybersecurity in an era with quantum computers: will we be ready?", *IEEE Security & Privacy*, 2018.
