# 🧬 IVF Pharmacogenomics Evidence Brief - MVP

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Phase 1 Non-SaMD (Software as a Medical Device)** information service that provides clinicians with pharmacogenomic context for IVF medication selection and patient counseling.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Database Integrations](#database-integrations)
- [Regulatory Compliance](#regulatory-compliance)
- [Evidence Registry](#evidence-registry)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

This application demonstrates a **precision medicine approach** to IVF treatment by integrating:
- Patient genetic variants
- Curated pharmacogenomic evidence
- Real-time connections to 6 major genomic databases
- Evidence-based medication context for 9 IVF drugs

### **What It Does**
✅ Displays patient genotypes with QC status  
✅ Summarizes peer-reviewed PGx associations  
✅ Provides evidence tiers and certainty levels  
✅ Shows label/guideline context (read-only)  
✅ Supports clinical discussion (non-directive)  

### **What It Does NOT Do**
❌ Generate dose recommendations  
❌ Select protocols or medications  
❌ Create treatment instructions  
❌ Interface with EMR systems  
❌ Make automated clinical decisions  

---

## ✨ Features

### **Core Functionality**
- **4-Card Evidence Display System**
  - Card A: Genotype Facts & Database Connections
  - Card B: Efficacy Evidence with Study Cohorts
  - Card C: Safety Context & Monitoring Recommendations
  - Card D: Label/Guideline Awareness (Read-Only)

- **9 IVF Medications Covered**
  - FSH (Follitropin alfa/delta)
  - LH supplementation
  - Corticosteroids
  - Growth Hormone
  - Coenzyme Q10
  - Melatonin
  - Metformin
  - Letrozole
  - Clomiphene citrate

- **6 Database Integrations**
  - 🏥 ClinVar - Clinical variant significance
  - 🧬 dbSNP - Population frequencies
  - 🌍 gnomAD - Population-specific allele frequencies
  - 🔬 Ensembl - Gene information
  - 💊 PharmGKB - Pharmacogenomic annotations
  - 📚 PubMed - Biomedical literature

### **Technical Features**
- Session-based caching for API results
- Rate limit handling with graceful degradation
- Real-time API connections (ClinVar, dbSNP, Ensembl, PubMed)
- Timeout protection (10s per API call)
- Responsive UI with tabbed database interface

### **Patient Data**
- 3 Sample patients with diverse ancestries (EUR, EAS, SAS)
- Complete genotype profiles (10 variants per patient)
- Hormonal markers: FSH, LH, E2, P4, AMH
- Clinical context: Age, BMI, prior response

---

## 🚀 Installation

### **Prerequisites**
- Python 3.9 or higher
- pip package manager

### **Quick Start**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ivf-pgx-mvp.git
cd ivf-pgx-mvp
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open in browser**
```
http://localhost:8501
```

### **Requirements**

Create a `requirements.txt` file with:
```txt
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
```

---

## 💻 Usage

### **Basic Workflow**

1. **Select Patient** from the sidebar (3 sample patients available)
2. **Choose Medication** from the drug catalog
3. **Review Evidence Cards**:
   - Genotype facts with ancestry context
   - Efficacy evidence with study cohorts
   - Safety considerations
   - Label/guideline information
4. **Explore Database Connections** (expand to see 6 databases)
5. **Document Discussion** using discussion prompts
6. **Generate PDF Report** (simulated for MVP)

### **Advanced Features**

#### **Database Exploration**
```python
# Access cached API results
if 'api_cache' in st.session_state:
    cache_keys = list(st.session_state.api_cache.keys())
    print(f"Cached results: {len(cache_keys)}")
```

#### **Custom Evidence Registry**
```python
# Add new gene-drug association
EVIDENCE_REGISTRY["NEW_VARIANT"] = {
    "id": "EDR-000XXX",
    "gene_symbol": "GENE_NAME",
    "rsid": "rsXXXXXXX",
    "tier": "B",
    # ... additional fields
}
```

---

## 🏗️ Architecture

### **Project Structure**
```
ivf-pgx-mvp/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE                # MIT License
├── .gitignore             # Git ignore file
├── docs/                  # Documentation
│   ├── screenshots/       # Application screenshots
│   └── evidence/          # Evidence curation guidelines
└── tests/                 # Unit tests (future)
    └── test_api.py
```

### **Component Architecture**

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
├─────────────────────────────────────────┤
│  - Patient Selection                    │
│  - Drug Selection                       │
│  - 4-Card Evidence Display              │
│  - Database Connection Tabs             │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         Data Layer                      │
├─────────────────────────────────────────┤
│  - Evidence Registry (In-Memory)        │
│  - Patient Genotypes (Simulated)        │
│  - Session Cache (st.session_state)     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         API Integration Layer           │
├─────────────────────────────────────────┤
│  - ClinVar API (Live)                   │
│  - dbSNP via Ensembl (Live)             │
│  - Ensembl REST API (Live)              │
│  - PubMed E-utilities (Live)            │
│  - gnomAD via Ensembl (Live)            │
│  - PharmGKB (Simulated)                 │
└─────────────────────────────────────────┘
```

---

## 🔗 Database Integrations

### **API Details**

| Database | Status | Authentication | Rate Limit | Endpoint |
|----------|--------|---------------|------------|----------|
| **ClinVar** | ✅ Live | None | 3 req/sec | `eutils.ncbi.nlm.nih.gov` |
| **dbSNP** | ✅ Live | None | 15 req/sec | `rest.ensembl.org` |
| **Ensembl** | ✅ Live | None | 15 req/sec | `rest.ensembl.org` |
| **PubMed** | ✅ Live | None | 3 req/sec | `eutils.ncbi.nlm.nih.gov` |
| **gnomAD** | ✅ Live | None | Via Ensembl | `rest.ensembl.org` |
| **PharmGKB** | ⚠️ Simulated | API Key Required | - | `api.pharmgkb.org` |

### **Caching Strategy**

- **Session-based caching**: Results stored in `st.session_state`
- **LRU cache**: Function-level memoization with `@lru_cache`
- **Cache duration**: Session lifetime (until browser refresh)
- **Benefits**: 
  - Reduces API calls by ~90%
  - Improves response time
  - Prevents rate limit issues

### **Error Handling**

```python
# All API calls include:
- Timeout protection (10 seconds)
- Exception handling
- Status-based error messages
- Graceful degradation
```

---

## ⚖️ Regulatory Compliance

### **Phase 1: Non-SaMD Information Service**

This application is designed to remain **outside medical device regulation** by:

✅ **Providing information only** (no prescriptive outputs)  
✅ **Using non-directive language** throughout  
✅ **Showing transparent inputs and sources**  
✅ **Requiring clinician review** for all decisions  
✅ **Not generating automated orders or doses**  

### **Disclaimers**

Every page displays:
> ⚠️ **Information-Only · Not a Medical Device · Clinician Review Required**
>
> This pharmacogenomic brief summarizes peer-reviewed associations and a patient's genotype to support clinician discussion. It does NOT generate treatment instructions, doses, or protocol selection.

### **Regulatory Framework**

| Phase | Status | Requirements |
|-------|--------|-------------|
| **Phase 1** | ✅ Current | Non-SaMD information display |
| **Phase 2** | 🔜 Optional | NATA ISO 15189 lab accreditation |
| **Phase 3** | 🔜 Future | SaMD upgrade with TGA ARTG listing |

### **Quality Management**

- Evidence registry with version control
- Curator approval and review dates
- Quarterly review for Tier A evidence
- Semi-annual review for Tier B/C evidence

---

## 📚 Evidence Registry

### **Tiering System**

| Tier | Definition | Criteria |
|------|------------|----------|
| **Tier A** | Replicated/Relevant | ≥1 meta-analysis OR ≥2 independent cohorts; consistent direction; plausible mechanism |
| **Tier B** | Suggestive/Mixed | Some clinical data with plausible biology; replication incomplete or heterogeneous |
| **Tier C** | Exploratory | Biologically plausible; early or indirect data; context only |

### **Evidence Structure**

Each entry contains:
- Gene symbol and variant ID
- Drug association
- Phenotype description
- Evidence tier (A/B/C)
- Effect direction
- Summary (100-150 words)
- Study cohorts with ancestry information
- Citations
- Last review date and curator initials

### **Current Coverage**

- **11 gene-drug associations**
- **9 IVF medications**
- **10 genetic variants**
- **Ancestries**: EUR, EAS, SAS, Multi

---

## 🛠️ Development

### **Running Tests**

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

### **Code Style**

```bash
# Install formatting tools
pip install black flake8

# Format code
black app.py

# Lint code
flake8 app.py
```

### **Adding New Evidence**

1. Update `EVIDENCE_REGISTRY` in `app.py`
2. Follow the JSON schema structure
3. Assign appropriate tier (A/B/C)
4. Include citations
5. Update `last_review` date

### **Adding New Drugs**

1. Add to `DRUG_CATALOG`
2. Map genes in `DRUG_GENE_MAP`
3. Add evidence entries to `EVIDENCE_REGISTRY`
4. (Optional) Add label info to `render_label_card()`
5. (Optional) Add discussion prompts

### **Environment Variables**

For production deployment:

```bash
# .env file (not included in repo)
PHARMGKB_API_KEY=your_api_key_here
NCBI_API_KEY=your_api_key_here  # Optional, increases rate limits
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### **Getting Started**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Contribution Areas**

- 🧬 **Evidence Curation**: Add new gene-drug associations
- 🔬 **API Integrations**: Enhance database connections
- 📊 **Visualizations**: Improve data presentation
- 🧪 **Testing**: Add unit and integration tests
- 📖 **Documentation**: Improve guides and examples
- 🐛 **Bug Fixes**: Identify and resolve issues

### **Code Standards**

- Follow PEP 8 style guide
- Add docstrings to all functions
- Include type hints where possible
- Write tests for new features
- Update README for significant changes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Eveia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 📞 Contact

**Project Lead**: Emanuel Birru

**Email**: emanuel.birru@eveia.com.au

**Organization**: Eveia

**Project Link**: https://github.com/eveia/ivf-pgx-mvp

---

## 🙏 Acknowledgments

- **NCBI** for ClinVar and PubMed APIs
- **Ensembl** for genomic data access
- **PharmGKB** for pharmacogenomic knowledge base
- **Streamlit** for the application framework
- **IVF Research Community** for evidence contributions

---

## 📊 Project Status

**Current Version**: 1.0.0-MVP  
**Last Updated**: October 28, 2025  
**Status**: 🟢 Active Development

### **Roadmap**

- [ ] v1.1 - Add VCF file upload
- [ ] v1.2 - Implement actual PDF generation
- [ ] v1.3 - Add user authentication
- [ ] v1.4 - Integrate PharmGKB API key
- [ ] v2.0 - NATA ISO 15189 compliance
- [ ] v3.0 - SaMD upgrade with TGA approval

---

## 📖 Additional Resources

- [ESHRE Ovarian Stimulation Guidelines](https://www.eshre.eu/guidelines)
- [TGA Software as Medical Device Guidance](https://www.tga.gov.au/resources/guidance/understanding-clinical-decision-support-software)
- [PharmGKB Documentation](https://www.pharmgkb.org/page/clinAnnLabels)
- [NATA Accreditation](https://nata.com.au/accreditation/medical-laboratory-accreditation-iso-15189/)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/ivf-pgx-mvp&type=Date)](https://star-history.com/#yourusername/ivf-pgx-mvp&Date)

---

**Built with ❤️ for precision medicine in reproductive health**
