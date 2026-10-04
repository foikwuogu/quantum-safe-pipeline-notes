# Release notes

Quantum-Safe Pipeline Notes: one issue per month on post-quantum cryptography and OT security for U.S. pipelines. Each issue is released on its date and archived on Zenodo with its own DOI.

## Issue 02: Harvest-now-decrypt-later for SCADA telemetry

**Series slot:** October 2026  
**Published:** 2026-10-03  
**Read it:** https://foikwuogu.github.io/quantum-safe-pipeline-notes/#issue-2  
**Archived:** https://doi.org/10.5281/zenodo.23130292  
**PDF:** [`pdf/2026-10-hndl-scada-telemetry.pdf`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/pdf/2026-10-hndl-scada-telemetry.pdf)  
**Source:** [`posts/2026-10-hndl-scada-telemetry.md`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/posts/2026-10-hndl-scada-telemetry.md)

Harvest-now-decrypt-later (HNDL) is the threat EO 14412 names first: adversaries recording encrypted traffic today to decrypt once a cryptographically relevant quantum computer exists. This note asks whether HNDL matters for pipeline SCADA telemetry, starting from the fact that much SCADA traffic still crosses links unencrypted.

It locates the quantum-vulnerable public-key operations in typical telemetry paths, applies Mosca's inequality to classify telemetry by how long it stays sensitive, separates the HNDL confidentiality risk from the long-term risk to signing keys, and quantifies the bandwidth cost of ML-KEM and ML-DSA on narrowband links (an ML-KEM-768 exchange moves 2,272 bytes versus 64 for X25519, about 1.89 seconds at 9,600 bps). It closes with six prioritized actions for operators.

**Companion code:** [`code/compute_stats.py`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/code/compute_stats.py)

**Cite as:** Friday Ogochukwu Ikwuogu, "Harvest-now-decrypt-later for SCADA telemetry," Quantum-Safe Pipeline Notes, issue 2, 2026. https://doi.org/10.5281/zenodo.23130292

License: text CC BY 4.0; code MIT.

## Issue 01: What EO 14412 means for a pipeline operator's certificate inventory

**Series slot:** September 2026  
**Published:** 2026-10-03  
**Read it:** https://foikwuogu.github.io/quantum-safe-pipeline-notes/#issue-1  
**Archived:** https://doi.org/10.5281/zenodo.23130001  
**PDF:** [`pdf/2026-09-eo-14412-certificate-inventory.pdf`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/pdf/2026-09-eo-14412-certificate-inventory.pdf)  
**Source:** [`posts/2026-09-eo-14412-certificate-inventory.md`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/posts/2026-09-eo-14412-certificate-inventory.md)

Executive Order 14412 (June 22, 2026) sets federal deadlines for post-quantum cryptography: key establishment by December 31, 2030 and digital signatures by December 31, 2031. The order is addressed to federal agencies and does not mention pipelines, but it reaches private critical infrastructure through Sector Risk Management Agency assistance, a forthcoming FAR rule for federal contractors, and CISA/NIST guidance on a cryptographic bill of materials.

This note argues that a pipeline operator's practical first step is an inventory of X.509 certificates in operational technology. It maps where certificates live in pipeline OT, explains how to collect them without disturbing the process, proposes a triage aligned to the order's two deadlines, and lists five actions for the next 90 days. A companion tool, cert_inventory.py, builds the inventory from exported certificates without connecting to any device.

**Companion code:** [`tools/cert_inventory.py`](https://github.com/foikwuogu/quantum-safe-pipeline-notes/blob/main/tools/cert_inventory.py)

**Cite as:** Friday Ogochukwu Ikwuogu, "What EO 14412 means for a pipeline operator's certificate inventory," Quantum-Safe Pipeline Notes, issue 1, 2026. https://doi.org/10.5281/zenodo.23130001

License: text CC BY 4.0; code MIT.
