---
title: "What EO 14412 means for a pipeline operator's certificate inventory"
series_slot: September 2026
issue: 1
published: "2026-10-03"
author: Friday Ogochukwu Ikwuogu
license: CC BY 4.0
status: published
---

# What EO 14412 means for a pipeline operator's certificate inventory

On June 22, 2026, the White House signed Executive Order 14412, *Securing the Nation Against Advanced Cryptographic Attacks*. It sets the federal government's deadlines for moving to post-quantum cryptography (PQC): high value assets and high impact systems must use PQC for key establishment by December 31, 2030, and for digital signatures by December 31, 2031.

If you run cybersecurity for a natural gas or hazardous liquids pipeline, the honest first reading is that the order does not bind you directly. It is addressed to federal agencies. The order never mentions pipelines, energy, OT, or TSA. So why write about it for pipeline operators?

Because the order reaches private critical infrastructure through three side doors, and all three lead to the same place: an inventory of where your systems use public-key cryptography. For most operators the most tractable piece of that inventory, and the right place to start, is certificates.

## The three side doors

**1. Sector Risk Management Agencies.** Section 5 directs the Sector Risk Management Agencies, working through CISA, to assist critical infrastructure owners and operators with PQC migration planning. Under National Security Memorandum 22 (April 2024), pipelines fall in the Transportation Systems sector, where DHS (through TSA) and the Department of Transportation are the SRMAs, and oil and natural gas also sit in the Energy sector, where the Department of Energy is the SRMA. "Assistance" is not a mandate, but it is how guidance becomes expectation.

**2. Procurement.** Within 180 days of signing (about December 19, 2026), the FAR Council must propose a rule requiring covered federal contractors to comply with NIST PQC standards by December 31, 2030. The SCADA, historian, firewall, and remote-access vendors that sell to federal customers sell to you too. Their product roadmaps will move on the federal clock, and their legacy firmware will stop being the default sooner than your asset lifecycle assumes.

**3. The cryptographic bill of materials.** Within 270 days (about March 19, 2027), CISA and NIST must publish guidance on the minimum elements of a cryptographic bill of materials (CBOM): a machine-readable statement of the cryptography inside a hardware or software product. Once that format exists, expect it to show up in vendor questionnaires, in assessment programs, and eventually in audit requests.

Add to this the regulation that already binds you. Operators designated as critical under TSA's Security Directive Pipeline-2021-02 series maintain a TSA-approved Cybersecurity Implementation Plan, a Cybersecurity Incident Response Plan, and an annual Cybersecurity Assessment Plan for their Critical Cyber Systems. The directives do not yet ask about quantum-vulnerable algorithms. But an operator that can describe its authentication and encryption controls algorithm by algorithm is in a far better position when they do, and TSA's proposed rule *Enhancing Surface Cyber Risk Management* (89 FR 88488, November 7, 2024) shows the direction of travel toward codified, auditable cyber risk management. As of mid-2026 that rule had not been finalized.

## Why certificates first

A full cryptographic inventory covers protocols, libraries, key stores, hardware security modules, and firmware. That is a multi-year project. Certificates are where you can start this month, for three reasons.

- **They are self-describing.** Every X.509 certificate states its public-key algorithm, key size, signature algorithm, issuer, and validity period. You do not need vendor cooperation to read them.
- **They are where both of the order's deadlines meet.** A certificate's key is often used for key establishment (the 2030 date) and its signature carries trust (the 2031 date).
- **OT certificates live a long time.** In IT, public TLS certificates now turn over in months, and the CA/Browser Forum's schedule takes their maximum lifetime down to 47 days by 2029. In OT, a self-signed certificate generated when an HMI or historian was commissioned can carry a 10- or 20-year validity, and a vendor root of trust used to sign firmware can outlast the equipment generation that shipped it. Anything valid past December 31, 2031 is, by definition, a certificate that will need to be replaced or justified.

## Where the certificates are in a pipeline environment

A starting map, from the enterprise edge toward the field:

| Location | Typical certificate use | Who usually controls renewal |
|---|---|---|
| Remote-access gateways and VPN concentrators | Device identity, IKE/TLS authentication | Operator (IT/OT security) |
| Active Directory Certificate Services in the OT domain | Smart-card logon, machine identity, LDAPS | Operator |
| Historian and HMI web servers | HTTPS for thin clients and dashboards | Operator, often self-signed by default |
| OPC UA servers and clients | Application instance certificates and trust lists | Integrator or operator |
| RTU, PLC, and flow-computer TLS (for example DNP3 or IEC 60870-5-104 secured per IEC 62351-3) | Mutual TLS between control center and field | Vendor tooling, operator-run |
| Cellular and satellite backhaul equipment | Management interfaces, IPsec | Carrier or vendor |
| Vendor firmware and software signing | Code-signing roots embedded in devices | Vendor only |

The last row deserves emphasis. You cannot replace a vendor's firmware-signing root yourself, and the devices that trust it may be in service until the 2040s. Those entries are less a task than a question to put to each vendor, in writing.

## How to collect without disturbing the process

1. **Export before you scan.** Engineering workstations, OPC UA trust-list folders, AD CS, and gateway admin consoles all let you export certificates without touching a field device.
2. **Capture passively where you must.** A SPAN or tap copy of control-center traffic shows server certificates in TLS 1.2 handshakes. TLS 1.3 encrypts the server certificate inside the handshake, so passive capture will miss TLS 1.3 servers entirely; those need export or host-side collection.
3. **Keep active scanning on the IT side** or inside planned maintenance windows, under your normal change control. Field devices with limited TLS stacks have been known to misbehave when probed.
4. **Run everything through one parser.** I have published a small companion tool, [`cert_inventory.py`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/tools/cert_inventory.py), that reads a folder of exported certificates and writes one CSV row per certificate: algorithm, key size, signature algorithm, validity, whether it is a CA, whether it outlives the 2031 signature date, and a first-pass priority. It never connects to a device. Columns the parser cannot know (asset, zone, whether it is part of a Critical Cyber System, who renews it, whether the device can change algorithms) are left for you to fill in.

## A triage that fits the order's two deadlines

- **Priority A: trust anchors and anything valid past 2031.** Root and issuing CAs, firmware-signing roots, and long-lived self-signed device certificates. These have the longest replacement lead time and the most dependents. Ask vendors for their PQC signature roadmap now.
- **Priority B: quantum-vulnerable leaf certificates that renew on a cycle.** RSA and elliptic-curve certificates that expire well before 2031. Replace them on their normal renewal schedule once your platform supports ML-DSA (FIPS 204) or hybrid certificates, and record which devices cannot.
- **Cross-cutting: key establishment that protects long-lived data.** Where a certificate's key negotiates sessions carrying information that must stay confidential for years, the risk is not in 2030 but today, because traffic recorded now can be decrypted later. That is the subject of the next issue.

## What I would do in the next 90 days

1. Name an owner for cryptographic inventory, the way the order requires each federal agency to name a PQC migration lead.
2. Export certificates from the five or six systems in the table above that you control directly, and run them through one parser.
3. Add an "algorithm" and "can change algorithm?" column to whatever asset inventory already supports your TSA Cybersecurity Implementation Plan.
4. Send every OT vendor the same three questions: Which public-key algorithms does the product use, and where? Can they be changed by firmware update? When will you ship ML-KEM and ML-DSA support?
5. Watch for the CISA/NIST CBOM guidance (due around March 19, 2027) and align your inventory fields to it when it lands.

None of this requires a quantum computer to exist. It requires knowing what you have, which is what every cybersecurity program already claims to do.

---

*Views are my own and do not represent any employer or client. This post uses only public sources and contains no non-public operator information. It is not legal advice.*

**Sources**

- The White House, [Securing the Nation Against Advanced Cryptographic Attacks (EO 14412)](https://www.whitehouse.gov/presidential-actions/2026/06/securing-the-nation-against-advanced-cryptographic-attacks/), June 22, 2026.
- Skadden, [New Executive Orders and Government Strategy Advance US Quantum Innovation and Mandate Post-Quantum Cryptography Transition](https://www.skadden.com/insights/publications/2026/06/new-executive-orders-and-government-strategy), June 2026.
- TSA, [Security Directives and Emergency Amendments](https://www.tsa.gov/sd-and-ea) (SD Pipeline-2021-02 series).
- Federal Register, [Pipeline Corporate Security Reviews and TSA Security Directive Pipeline-2021-02 Series, information collection notice](https://www.federalregister.gov/documents/2026/01/02/2025-24198/revision-of-agency-information-collection-activity-under-omb-review-pipeline-corporate-security), January 2, 2026.
- Federal Register, [Enhancing Surface Cyber Risk Management (proposed rule)](https://www.federalregister.gov/documents/2024/11/07/2024-24704/enhancing-surface-cyber-risk-management), November 7, 2024.
- NIST, FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), August 2024.
