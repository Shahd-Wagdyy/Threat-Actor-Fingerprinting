# Threat Actor Fingerprinting

**Cyber Threat Intelligence + Machine Learning**

Threat Actor Fingerprinting is a project focused on attributing cyberattacks to known threat actors based on *behavior* rather than just surface-level indicators like IP addresses or malware hashes. IPs get burned and hashes change, but the way an actor operates — the techniques they favor, the tools they reach for, the industries they target — tends to stay consistent over time. This project tries to capture that behavioral signature and use it for attribution.

## The Idea

Instead of asking "does this IP match a known bad IP," the system asks "does this incident *behave* like a known threat actor." It builds a fingerprint for each group based on their historical patterns, then compares new incidents against those fingerprints to surface the most likely match, along with a confidence score.

## Pipeline

1. **Collect threat intelligence** — malware reports, MITRE ATT&CK technique mappings, and indicators of compromise (IoCs) from available sources.
2. **Extract behavioral features**, including:
   - MITRE ATT&CK TTPs (tactics, techniques, and procedures)
   - Malware families used
   - Targeted industries
   - Geographic targeting patterns
   - Tools commonly deployed (e.g. Cobalt Strike, Mimikatz)
   - Command-and-control (C2) patterns
3. **Build a fingerprint/profile** for each threat actor or APT group from these features.
4. **Score new incidents** against existing fingerprints using similarity scoring and/or machine learning models.
5. **Return the most likely matching threat actor**, along with a confidence score.

## Tech Stack

- **Python** — core language for data processing and modeling
- **FastAPI** — API layer for querying and serving attribution results
- **Pandas** — data wrangling and feature extraction
- **Scikit-learn** — similarity scoring and ML-based classification
- **PostgreSQL / SQLite** — storing threat actor profiles and incident data
- **MITRE ATT&CK knowledge base** — the backbone for TTP-based feature mapping
- **STIX/TAXII feeds** *(optional)* — for pulling in structured threat intelligence
- **Docker** *(optional)* — for containerized deployment

## Why This Project

Attribution is one of the harder problems in cyber threat intelligence — it sits at the intersection of security research and data science. This project pulls together:

- Cyber Threat Intelligence (CTI)
- Machine Learning
- Security Research

into a single, practical pipeline rather than treating them as separate skills.

## Status

This project is a work in progress. Current focus areas include expanding the feature set, refining the similarity/scoring approach, and building out the API layer.

## Disclaimer

This project is intended for research and educational purposes. Attribution results are probabilistic and should not be treated as definitive proof of actor identity.
