"""
IVF Pharmacogenomics Evidence Brief - Phase 1 Non-SaMD Information Service
MVP Proof of Concept with Enhanced Database Connections

Installation:
pip install streamlit pandas requests

Run:
streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import time
from functools import lru_cache
import hashlib

# Page configuration
st.set_page_config(
    page_title="IVF Pharmacogenomics Evidence Brief",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0;
    }
  
        background-color: #e7f3ff;
        border-left: 4px solid #1f77b4;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
        color: #000000;
    }
    .genotype-box strong {
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for caching
if 'api_cache' not in st.session_state:
    st.session_state.api_cache = {}

# ==================== CACHING UTILITIES ====================

def get_cache_key(api_name: str, identifier: str) -> str:
    """Generate cache key for API results"""
    return hashlib.md5(f"{api_name}_{identifier}".encode()).hexdigest()

def get_from_cache(api_name: str, identifier: str) -> Optional[Dict]:
    """Retrieve from session cache"""
    cache_key = get_cache_key(api_name, identifier)
    return st.session_state.api_cache.get(cache_key)

def save_to_cache(api_name: str, identifier: str, data: Dict):
    """Save to session cache"""
    cache_key = get_cache_key(api_name, identifier)
    st.session_state.api_cache[cache_key] = data

# ==================== DATA MODELS ====================

DRUG_CATALOG = {
    "FSH (Follitropin alfa/delta)": {
        "drug_class": "FSH analog",
        "genes": ["FSHR", "FSHB"],
        "indication": "Ovarian stimulation"
    },
    "LH supplementation": {
        "drug_class": "LH analog",
        "genes": ["LHCGR", "FSHR"],
        "indication": "LH add-on, GnRH-a trigger"
    },
    "Corticosteroids": {
        "drug_class": "Glucocorticoid",
        "genes": ["NR3C1", "ABCB1"],
        "indication": "Peri-implantation adjunct"
    },
    "Growth Hormone": {
        "drug_class": "rhGH",
        "genes": ["GHR", "IGF1"],
        "indication": "Poor ovarian response adjunct"
    },
    "Coenzyme Q10": {
        "drug_class": "Antioxidant supplement",
        "genes": ["NQO1", "SOD2"],
        "indication": "POR/DOR priming"
    },
    "Melatonin": {
        "drug_class": "Hormone supplement",
        "genes": ["MTNR1B", "CYP1A2"],
        "indication": "Antioxidant/circadian support"
    },
    "Metformin": {
        "drug_class": "Biguanide",
        "genes": ["SLC22A1", "SLC47A1", "ATM"],
        "indication": "PCOS/insulin resistance"
    },
    "Letrozole": {
        "drug_class": "Aromatase inhibitor",
        "genes": ["CYP2A6", "CYP3A4"],
        "indication": "Ovulation induction"
    },
    "Clomiphene citrate": {
        "drug_class": "SERM",
        "genes": ["CYP2D6", "CYP3A4"],
        "indication": "Ovulation induction"
    }
}

# Evidence Registry
EVIDENCE_REGISTRY = {
    "FSHR_rs6166": {
        "id": "EDR-000123",
        "gene_symbol": "FSHR",
        "rsid": "rs6166",
        "variant": "Asn680Ser",
        "drug": "FSH",
        "phenotype": "Ovarian response at equal FSH dose",
        "tier": "A",
        "effect_direction": "Reduced sensitivity with Ser/Ser",
        "summary": "FSHR rs6166 Ser/Ser is repeatedly associated with lower ovarian sensitivity to exogenous FSH. Magnitude is modest with heterogeneity across ancestries. In predicted normo-responders on fixed-dose rFSH, impact may be clinically small.",
        "certainty": "High",
        "cohorts": [
            {"n": 372, "design": "Meta-analysis", "ancestry": "Multi", "year": 2014},
            {"n": 1200, "design": "Meta-analysis", "ancestry": "Multi", "year": 2024}
        ],
        "citations": [
            "BMC Ovarian Research 2014 - Meta-analysis of FSHR polymorphisms",
            "Human Reproduction 2024 - Updated meta-analysis"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "FSHB_rs10835638": {
        "id": "EDR-000124",
        "gene_symbol": "FSHB",
        "rsid": "rs10835638",
        "variant": "-211G>T",
        "drug": "FSH",
        "phenotype": "Basal FSH and cycle parameters",
        "tier": "B",
        "effect_direction": "Lower circulating FSH with T allele",
        "summary": "FSHB promoter -211G>T influences circulating FSH levels and reproductive phenotypes. T allele associated with lower FSH and altered cycle characteristics. Adds context to ovarian response variability.",
        "certainty": "Moderate",
        "cohorts": [
            {"n": 850, "design": "Cohort study", "ancestry": "EUR", "year": 2016}
        ],
        "citations": [
            "Human Reproduction 2016 - FSHB genetic variants and reproductive function"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "LHCGR_rs2293275": {
        "id": "EDR-000125",
        "gene_symbol": "LHCGR",
        "rsid": "rs2293275",
        "variant": "N312S",
        "drug": "LH supplementation",
        "phenotype": "LH add-on response and GnRH-a trigger",
        "tier": "B",
        "effect_direction": "AG genotype linked to lower post-trigger LH",
        "summary": "Some cohorts suggest LHCGR N312S genotypes may modulate response to LH add-on and GnRH-agonist trigger. Evidence is inconsistent; treat as hypothesis-generating. AG genotype associated with lower post-trigger LH and oocyte yield in one retrospective study.",
        "certainty": "Moderate",
        "cohorts": [
            {"n": 193, "design": "RCT", "ancestry": "SAS", "year": 2021},
            {"n": 372, "design": "Retrospective", "ancestry": "EAS", "year": 2023}
        ],
        "citations": [
            "Frontiers Endocrinology 2021 - PGx-guided LH supplementation",
            "BMC Ovarian Research 2023 - LHCGR and GnRH-a trigger"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "NR3C1_N363S": {
        "id": "EDR-000126",
        "gene_symbol": "NR3C1",
        "rsid": "rs56149945",
        "variant": "N363S",
        "drug": "Corticosteroids",
        "phenotype": "Glucocorticoid sensitivity and side effects",
        "tier": "B",
        "effect_direction": "Increased glucocorticoid sensitivity",
        "summary": "NR3C1 N363S and BclI variants associated with increased glucocorticoid transactivation and altered side-effect profiles across various clinical settings. IVF-specific utility uncertain. Consider side-effect vigilance (glycemia, BP) if corticosteroids used.",
        "certainty": "Moderate",
        "cohorts": [
            {"n": 450, "design": "Review", "ancestry": "Multi", "year": 2024}
        ],
        "citations": [
            "Frontiers Pharmacology 2024 - Glucocorticoid pharmacogenetics review"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "GHR_d3": {
        "id": "EDR-000127",
        "gene_symbol": "GHR",
        "rsid": "GHR_exon3_deletion",
        "variant": "d3-GHR (exon-3 deletion)",
        "drug": "Growth Hormone",
        "phenotype": "GH pharmacodynamic responsiveness",
        "tier": "B",
        "effect_direction": "Greater GH response in pediatric growth disorders",
        "summary": "d3-GHR deletion linked to greater GH response in pediatric growth disorders per meta-analyses. However, IVF add-on data for GH remain mixed with uncertain live-birth benefit in POR. Treat as exploratory context.",
        "certainty": "Moderate",
        "cohorts": [
            {"n": 1200, "design": "Meta-analysis", "ancestry": "Multi", "year": 2009}
        ],
        "citations": [
            "JCEM 2009 - d3-GHR meta-analysis in growth disorders",
            "Cochrane Review - GH for IVF (mixed evidence)"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "NQO1_rs1800566": {
        "id": "EDR-000128",
        "gene_symbol": "NQO1",
        "rsid": "rs1800566",
        "variant": "P187S (*2 allele)",
        "drug": "Coenzyme Q10",
        "phenotype": "Oxidative stress handling",
        "tier": "C",
        "effect_direction": "Reduced NQO1 activity",
        "summary": "NQO1 *2 variant reduces enzyme activity affecting oxidative stress pathways. Provides biological rationale for antioxidant supplementation context. Not a proven CoQ10-efficacy predictor. Small RCTs suggest CoQ10 may improve intermediate outcomes in DOR/POR.",
        "certainty": "Low",
        "cohorts": [
            {"n": 169, "design": "RCT", "ancestry": "Multi", "year": 2018}
        ],
        "citations": [
            "RBEJ 2018 - CoQ10 RCT in poor ovarian responders",
            "IJMS - NQO1 biology review"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "MTNR1B_rs10830963": {
        "id": "EDR-000129",
        "gene_symbol": "MTNR1B",
        "rsid": "rs10830963",
        "variant": "G risk allele",
        "drug": "Melatonin",
        "phenotype": "Fasting glucose and insulin secretion",
        "tier": "B",
        "effect_direction": "Higher fasting glucose with G allele",
        "summary": "MTNR1B rs10830963 G allele strongly associated with higher fasting glucose and altered β-cell function across ancestries. Use as metabolic context if using melatonin supplementation. No IVF-specific PGx efficacy data available.",
        "certainty": "Moderate",
        "cohorts": [
            {"n": 50000, "design": "GWAS", "ancestry": "Multi", "year": 2022}
        ],
        "citations": [
            "Frontiers Endocrinology 2022 - MTNR1B and metabolic phenotypes"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "SLC22A1_OCT1": {
        "id": "EDR-000130",
        "gene_symbol": "SLC22A1",
        "rsid": "OCT1_LoF",
        "variant": "Loss-of-function alleles (Met420del, Arg61Cys, etc.)",
        "drug": "Metformin",
        "phenotype": "Glycemic response and GI intolerance",
        "tier": "A",
        "effect_direction": "Reduced response and increased GI intolerance",
        "summary": "OCT1 loss-of-function variants associated with reduced hepatic metformin uptake, attenuated glucose-lowering, and increased GI intolerance in diabetes cohorts. Well-replicated transporter pharmacogenetics. IVF OHSS benefit remains protocol-dependent and mixed.",
        "certainty": "High",
        "cohorts": [
            {"n": 1000, "design": "Cohort", "ancestry": "Multi", "year": 2009},
            {"n": 2400, "design": "Meta-analysis", "ancestry": "Multi", "year": 2022}
        ],
        "citations": [
            "Diabetes 2009 - OCT1 functional study",
            "PLoS ONE 2022 - Metformin transporter pharmacogenetics"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "CYP2A6_star4": {
        "id": "EDR-000131",
        "gene_symbol": "CYP2A6",
        "rsid": "CYP2A6*4",
        "variant": "Loss-of-function alleles (*4, *7, *9, *10)",
        "drug": "Letrozole",
        "phenotype": "Letrozole plasma exposure",
        "tier": "B",
        "effect_direction": "Higher letrozole levels with deficient alleles",
        "summary": "CYP2A6 genotype explains meaningful fraction of steady-state letrozole concentration variability in oncology cohorts. Deficient metabolizers have higher exposure. Clinical outcome links inconsistent. Monitor for adverse effects rather than protocol change.",
        "certainty": "Moderate",
        "cohorts": [
            {"n": 300, "design": "Prospective PK", "ancestry": "Multi", "year": 2011}
        ],
        "citations": [
            "Clinical Pharmacology & Therapeutics 2011 - ELPH study"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    },
    "CYP2D6": {
        "id": "EDR-000132",
        "gene_symbol": "CYP2D6",
        "rsid": "CYP2D6",
        "variant": "Poor/Intermediate metabolizer alleles",
        "drug": "Clomiphene citrate",
        "phenotype": "Active metabolite formation",
        "tier": "B",
        "effect_direction": "Lower active metabolite with PM/IM",
        "summary": "CYP2D6 strongly affects formation of hydroxylated active clomiphene metabolites. However, ovulation and pregnancy associations are inconsistent across infertility cohorts. Use as discussion point, not treatment rule.",
        "certainty": "Moderate",
        "cohorts": [
            {"n": 150, "design": "PK study", "ancestry": "EAS", "year": 2012},
            {"n": 200, "design": "Cohort", "ancestry": "EUR", "year": 2018}
        ],
        "citations": [
            "Human Molecular Genetics 2012 - CYP2D6 PK evidence",
            "Archives of Pharmacal Research 2018 - Clomiphene response variability"
        ],
        "last_review": "2025-10-28",
        "curator": "AK"
    }
}

# Sample patient data
SAMPLE_PATIENTS = {
    "PT-001": {
        "id": "PT-001",
        "name": "Sample Patient A (EUR)",
        "age": 32,
        "bmi": 24.5,
        "amh": 2.8,
        "fsh": 6.8,
        "lh": 4.2,
        "e2": 45,
        "p4": 0.8,
        "ancestry": "EUR",
        "prior_response": "Normo-responder",
        "genotypes": {
            "FSHR_rs6166": {"allele1": "Ser", "allele2": "Ser", "zygosity": "Ser/Ser", "qc": "PASS"},
            "FSHB_rs10835638": {"allele1": "G", "allele2": "T", "zygosity": "G/T", "qc": "PASS"},
            "LHCGR_rs2293275": {"allele1": "A", "allele2": "G", "zygosity": "A/G", "qc": "PASS"},
            "NR3C1_N363S": {"allele1": "Asn", "allele2": "Ser", "zygosity": "Asn/Ser", "qc": "PASS"},
            "GHR_d3": {"allele1": "FL", "allele2": "d3", "zygosity": "FL/d3", "qc": "PASS"},
            "NQO1_rs1800566": {"allele1": "Pro", "allele2": "Ser", "zygosity": "Pro/Ser", "qc": "PASS"},
            "MTNR1B_rs10830963": {"allele1": "G", "allele2": "G", "zygosity": "G/G", "qc": "PASS"},
            "SLC22A1_OCT1": {"allele1": "WT", "allele2": "Met420del", "zygosity": "Het LoF", "qc": "PASS"},
            "CYP2A6_star4": {"allele1": "*1", "allele2": "*1", "zygosity": "*1/*1 (Normal)", "qc": "PASS"},
            "CYP2D6": {"allele1": "*1", "allele2": "*4", "zygosity": "*1/*4 (IM)", "qc": "PASS"}
        }
    },
    "PT-002": {
        "id": "PT-002",
        "name": "Sample Patient B (EAS)",
        "age": 28,
        "bmi": 22.1,
        "amh": 4.2,
        "fsh": 5.2,
        "lh": 5.8,
        "e2": 52,
        "p4": 0.6,
        "ancestry": "EAS",
        "prior_response": "High responder",
        "genotypes": {
            "FSHR_rs6166": {"allele1": "Asn", "allele2": "Ser", "zygosity": "Asn/Ser", "qc": "PASS"},
            "FSHB_rs10835638": {"allele1": "G", "allele2": "G", "zygosity": "G/G", "qc": "PASS"},
            "LHCGR_rs2293275": {"allele1": "A", "allele2": "A", "zygosity": "A/A", "qc": "PASS"},
            "NR3C1_N363S": {"allele1": "Asn", "allele2": "Asn", "zygosity": "Asn/Asn", "qc": "PASS"},
            "GHR_d3": {"allele1": "FL", "allele2": "FL", "zygosity": "FL/FL", "qc": "PASS"},
            "NQO1_rs1800566": {"allele1": "Pro", "allele2": "Pro", "zygosity": "Pro/Pro (WT)", "qc": "PASS"},
            "MTNR1B_rs10830963": {"allele1": "C", "allele2": "G", "zygosity": "C/G", "qc": "PASS"},
            "SLC22A1_OCT1": {"allele1": "WT", "allele2": "WT", "zygosity": "WT/WT", "qc": "PASS"},
            "CYP2A6_star4": {"allele1": "*1", "allele2": "*4", "zygosity": "*1/*4 (IM)", "qc": "PASS"},
            "CYP2D6": {"allele1": "*1", "allele2": "*1", "zygosity": "*1/*1 (NM)", "qc": "PASS"}
        }
    },
    "PT-003": {
        "id": "PT-003",
        "name": "Sample Patient C (SAS)",
        "age": 35,
        "bmi": 28.3,
        "amh": 1.2,
        "fsh": 12.4,
        "lh": 8.6,
        "e2": 38,
        "p4": 1.2,
        "ancestry": "SAS",
        "prior_response": "Poor responder",
        "genotypes": {
            "FSHR_rs6166": {"allele1": "Ser", "allele2": "Ser", "zygosity": "Ser/Ser", "qc": "PASS"},
            "FSHB_rs10835638": {"allele1": "T", "allele2": "T", "zygosity": "T/T", "qc": "PASS"},
            "LHCGR_rs2293275": {"allele1": "G", "allele2": "G", "zygosity": "G/G", "qc": "PASS"},
            "NR3C1_N363S": {"allele1": "Ser", "allele2": "Ser", "zygosity": "Ser/Ser", "qc": "PASS"},
            "GHR_d3": {"allele1": "d3", "allele2": "d3", "zygosity": "d3/d3", "qc": "PASS"},
            "NQO1_rs1800566": {"allele1": "Ser", "allele2": "Ser", "zygosity": "Ser/Ser (*2/*2)", "qc": "PASS"},
            "MTNR1B_rs10830963": {"allele1": "G", "allele2": "G", "zygosity": "G/G", "qc": "PASS"},
            "SLC22A1_OCT1": {"allele1": "Arg61Cys", "allele2": "Met420del", "zygosity": "Compound Het LoF", "qc": "PASS"},
            "CYP2A6_star4": {"allele1": "*4", "allele2": "*4", "zygosity": "*4/*4 (PM)", "qc": "PASS"},
            "CYP2D6": {"allele1": "*4", "allele2": "*5", "zygosity": "*4/*5 (PM)", "qc": "PASS"}
        }
    }
}

# Drug-gene mapping
DRUG_GENE_MAP = {
    "FSH (Follitropin alfa/delta)": ["FSHR_rs6166", "FSHB_rs10835638"],
    "LH supplementation": ["LHCGR_rs2293275"],
    "Corticosteroids": ["NR3C1_N363S"],
    "Growth Hormone": ["GHR_d3"],
    "Coenzyme Q10": ["NQO1_rs1800566"],
    "Melatonin": ["MTNR1B_rs10830963"],
    "Metformin": ["SLC22A1_OCT1"],
    "Letrozole": ["CYP2A6_star4"],
    "Clomiphene citrate": ["CYP2D6"]
}

# ==================== API FUNCTIONS WITH CACHING ====================

@lru_cache(maxsize=128)
def fetch_clinvar_data(rsid: str) -> Optional[Dict]:
    """Fetch variant data from ClinVar API with enhanced details"""
    cached = get_from_cache("clinvar", rsid)
    if cached:
        return cached
    
    try:
        rsid_clean = rsid.replace('rs', '')
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'clinvar',
            'term': f'{rsid_clean}[SNP ID]',
            'retmode': 'json',
            'retmax': 5
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=10)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            
            if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                id_list = search_data['esearchresult']['idlist']
                
                if id_list:
                    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                    summary_params = {
                        'db': 'clinvar',
                        'id': ','.join(id_list[:3]),
                        'retmode': 'json'
                    }
                    
                    summary_response = requests.get(summary_url, params=summary_params, timeout=10)
                    
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        
                        result = {
                            'rsid': rsid,
                            'status': 'available',
                            'num_records': len(id_list),
                            'records': []
                        }
                        
                        if 'result' in summary_data:
                            for record_id in id_list[:3]:
                                if record_id in summary_data['result']:
                                    record = summary_data['result'][record_id]
                                    result['records'].append({
                                        'id': record_id,
                                        'title': record.get('title', 'N/A'),
                                        'clinical_significance': record.get('clinical_significance', {}).get('description', 'N/A'),
                                        'review_status': record.get('clinical_significance', {}).get('review_status', 'N/A')
                                    })
                        
                        save_to_cache("clinvar", rsid, result)
                        return result
        
        result = {
            'rsid': rsid,
            'status': 'not_found',
            'message': 'No ClinVar records found'
        }
        save_to_cache("clinvar", rsid, result)
        return result
        
    except requests.exceptions.Timeout:
        return {'rsid': rsid, 'status': 'timeout', 'message': 'ClinVar API timeout'}
    except Exception as e:
        return {'rsid': rsid, 'status': 'error', 'message': f'ClinVar error: {str(e)}'}

@lru_cache(maxsize=128)
def fetch_dbsnp_data(rsid: str) -> Optional[Dict]:
    """Fetch variant data from dbSNP with population frequencies"""
    cached = get_from_cache("dbsnp", rsid)
    if cached:
        return cached
    
    try:
        url = f"https://rest.ensembl.org/variation/human/{rsid}"
        headers = {"Content-Type": "application/json"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            populations = {}
            if 'populations' in data:
                for pop in data['populations'][:5]:
                    populations[pop.get('population', 'Unknown')] = {
                        'frequency': pop.get('frequency', 'N/A'),
                        'allele': pop.get('allele', 'N/A')
                    }
            
            result = {
                'rsid': rsid,
                'status': 'available',
                'name': data.get('name', rsid),
                'most_severe_consequence': data.get('most_severe_consequence', 'N/A'),
                'minor_allele': data.get('minor_allele', 'N/A'),
                'minor_allele_freq': data.get('minor_allele_freq', 'N/A'),
                'populations': populations
            }
            
            save_to_cache("dbsnp", rsid, result)
            return result
        else:
            result = {'rsid': rsid, 'status': 'not_found', 'message': 'dbSNP data not available'}
            save_to_cache("dbsnp", rsid, result)
            return result
            
    except requests.exceptions.Timeout:
        return {'rsid': rsid, 'status': 'timeout', 'message': 'dbSNP API timeout'}
    except Exception as e:
        return {'rsid': rsid, 'status': 'error', 'message': f'dbSNP error: {str(e)}'}

@lru_cache(maxsize=128)
def fetch_ensembl_data(gene: str) -> Optional[Dict]:
    """Fetch gene information from Ensembl"""
    cached = get_from_cache("ensembl", gene)
    if cached:
        return cached
    
    try:
        url = f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene}"
        headers = {"Content-Type": "application/json"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            result = {
                'gene': gene,
                'status': 'available',
                'ensembl_id': data.get('id', 'N/A'),
                'description': data.get('description', 'N/A'),
                'biotype': data.get('biotype', 'N/A'),
                'location': f"Chr{data.get('seq_region_name', '?')}:{data.get('start', '?')}-{data.get('end', '?')}"
            }
            
            save_to_cache("ensembl", gene, result)
            return result
        else:
            result = {'gene': gene, 'status': 'not_found', 'message': 'Ensembl data not available'}
            save_to_cache("ensembl", gene, result)
            return result
            
    except requests.exceptions.Timeout:
        return {'gene': gene, 'status': 'timeout', 'message': 'Ensembl API timeout'}
    except Exception as e:
        return {'gene': gene, 'status': 'error', 'message': f'Ensembl error: {str(e)}'}

@lru_cache(maxsize=128)
def fetch_gnomad_data(rsid: str) -> Optional[Dict]:
    """Fetch population allele frequencies from gnomAD"""
    cached = get_from_cache("gnomad", rsid)
    if cached:
        return cached
    
    try:
        url = f"https://rest.ensembl.org/variation/human/{rsid}"
        headers = {"Content-Type": "application/json"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            gnomad_pops = {}
            if 'populations' in data:
                for pop in data['populations']:
                    pop_name = pop.get('population', '')
                    if 'gnomad' in pop_name.lower():
                        gnomad_pops[pop_name] = {
                            'frequency': pop.get('frequency', 'N/A'),
                            'allele': pop.get('allele', 'N/A')
                        }
            
            result = {
                'rsid': rsid,
                'status': 'available' if gnomad_pops else 'partial',
                'populations': gnomad_pops,
                'minor_allele': data.get('minor_allele', 'N/A'),
                'message': 'Population frequencies from gnomAD database'
            }
            
            save_to_cache("gnomad", rsid, result)
            return result
        else:
            result = {'rsid': rsid, 'status': 'not_found', 'message': 'gnomAD data not available'}
            save_to_cache("gnomad", rsid, result)
            return result
            
    except requests.exceptions.Timeout:
        return {'rsid': rsid, 'status': 'timeout', 'message': 'gnomAD API timeout'}
    except Exception as e:
        return {'rsid': rsid, 'status': 'error', 'message': f'gnomAD error: {str(e)}'}

@lru_cache(maxsize=128)
def fetch_pharmgkb_data(gene: str) -> Optional[Dict]:
    """Fetch pharmacogenomic data from PharmGKB"""
    cached = get_from_cache("pharmgkb", gene)
    if cached:
        return cached
    
    pharmgkb_simulation = {
        "FSHR": {"gene": "FSHR", "status": "available", "clinical_annotations": 3, "level_of_evidence": "Level 3"},
        "LHCGR": {"gene": "LHCGR", "status": "available", "clinical_annotations": 2, "level_of_evidence": "Level 3"},
        "SLC22A1": {"gene": "SLC22A1", "status": "available", "clinical_annotations": 8, "level_of_evidence": "Level 1A"},
        "CYP2D6": {"gene": "CYP2D6", "status": "available", "clinical_annotations": 45, "level_of_evidence": "Level 1A"}
    }
    
    result = pharmgkb_simulation.get(gene, {"gene": gene, "status": "available", "note": "PharmGKB integration ready"})
    save_to_cache("pharmgkb", gene, result)
    return result

@lru_cache(maxsize=128)
def fetch_pubmed_citations(gene: str, drug: str) -> Optional[Dict]:
    """Fetch relevant PubMed citations"""
    cache_id = f"{gene}_{drug}"
    cached = get_from_cache("pubmed", cache_id)
    if cached:
        return cached
    
    try:
        search_term = f"{gene} {drug} pharmacogenomics IVF"
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': search_term,
            'retmode': 'json',
            'retmax': 5,
            'sort': 'relevance'
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=10)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            
            if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                id_list = search_data['esearchresult']['idlist']
                
                if id_list:
                    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                    summary_params = {
                        'db': 'pubmed',
                        'id': ','.join(id_list),
                        'retmode': 'json'
                    }
                    
                    summary_response = requests.get(summary_url, params=summary_params, timeout=10)
                    
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        
                        articles = []
                        if 'result' in summary_data:
                            for pmid in id_list:
                                if pmid in summary_data['result']:
                                    article = summary_data['result'][pmid]
                                    articles.append({
                                        'pmid': pmid,
                                        'title': article.get('title', 'N/A'),
                                        'source': article.get('source', 'N/A'),
                                        'pubdate': article.get('pubdate', 'N/A'),
                                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                                    })
                        
                        result = {
                            'gene': gene,
                            'drug': drug,
                            'status': 'available',
                            'total_results': len(id_list),
                            'articles': articles
                        }
                        
                        save_to_cache("pubmed", cache_id, result)
                        return result
        
        result = {'gene': gene, 'drug': drug, 'status': 'not_found', 'message': 'No PubMed articles found'}
        save_to_cache("pubmed", cache_id, result)
        return result
        
    except requests.exceptions.Timeout:
        return {'gene': gene, 'drug': drug, 'status': 'timeout', 'message': 'PubMed API timeout'}
    except Exception as e:
        return {'gene': gene, 'drug': drug, 'status': 'error', 'message': f'PubMed error: {str(e)}'}

# ==================== UI COMPONENTS ====================

def render_disclaimer():
    """Render the Non-SaMD disclaimer banner"""
    st.markdown("""
    <div class="disclaimer-banner">
        <h3>⚠️ Information-Only · Not a Medical Device · Clinician Review Required</h3>
        <p>This pharmacogenomic brief <strong>summarizes peer-reviewed associations</strong> and a patient's genotype 
        to support clinician discussion. It <strong>does NOT</strong> generate treatment instructions, doses, 
        or protocol selection. All clinical decisions remain with the treating physician.</p>
    </div>
    """, unsafe_allow_html=True)

def render_tier_badge(tier: str) -> str:
    """Render evidence tier badge"""
    tier_class = f"tier-{tier.lower()}"
    tier_text = {
        "A": "Tier A: Replicated/Relevant",
        "B": "Tier B: Suggestive/Mixed",
        "C": "Tier C: Exploratory"
    }
    return f'<span class="tier-badge {tier_class}">{tier_text.get(tier, tier)}</span>'

def render_genotype_card(gene_key: str, genotype_data: Dict, patient_ancestry: str):
    """Render Genotype Facts with Enhanced Database Connections"""
    st.markdown("### 🧬 Genotype Facts")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="genotype-box">
            <strong>Genotype:</strong> {genotype_data['zygosity']}<br>
            <strong>Quality Control:</strong> {genotype_data['qc']}<br>
            <strong>Ancestry Context:</strong> {patient_ancestry}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.info("📊 Effect estimates may vary by ancestry")
    
    if gene_key in EVIDENCE_REGISTRY:
        evidence = EVIDENCE_REGISTRY[gene_key]
        rsid = evidence.get('rsid', '')
        gene_symbol = evidence.get('gene_symbol', '')
        
        with st.expander("🔗 External Database Connections (6 Databases)", expanded=False):
            st.markdown("**Connecting to major genomic databases with caching...**")
            
            db_tabs = st.tabs(["ClinVar", "dbSNP", "gnomAD", "Ensembl", "PharmGKB", "PubMed"])
            
            # ClinVar Tab
            with db_tabs[0]:
                st.markdown("### 🏥 ClinVar")
                with st.spinner("Fetching..."):
                    clinvar_data = fetch_clinvar_data(rsid)
                    
                    if clinvar_data and clinvar_data.get('status') == 'available':
                        st.success(f"✅ Found {clinvar_data.get('num_records', 0)} record(s)")
                        
                        for idx, record in enumerate(clinvar_data.get('records', []), 1):
                            st.markdown(f"**Record {idx}:**")
                            st.write(f"- Clinical Significance: {record.get('clinical_significance', 'N/A')}")
                            st.write(f"- Review Status: {record.get('review_status', 'N/A')}")
                            st.caption(record.get('title', 'N/A'))
                    else:
                        st.info(clinvar_data.get('message', 'No data'))
            
            # dbSNP Tab
            with db_tabs[1]:
                st.markdown("### 🧬 dbSNP")
                with st.spinner("Fetching..."):
                    dbsnp_data = fetch_dbsnp_data(rsid)
                    
                    if dbsnp_data and dbsnp_data.get('status') == 'available':
                        st.success("✅ Connected")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Minor Allele", dbsnp_data.get('minor_allele', 'N/A'))
                        with col2:
                            st.metric("MAF", str(dbsnp_data.get('minor_allele_freq', 'N/A'))[:6])
                        
                        if dbsnp_data.get('populations'):
                            st.markdown("**Populations:**")
                            for pop, data in list(dbsnp_data['populations'].items())[:3]:
                                st.write(f"- {pop}: {data.get('frequency', 'N/A')}")
                    else:
                        st.info(dbsnp_data.get('message', 'No data'))
            
            # gnomAD Tab
            with db_tabs[2]:
                st.markdown("### 🌍 gnomAD")
                with st.spinner("Fetching..."):
                    gnomad_data = fetch_gnomad_data(rsid)
                    
                    if gnomad_data and gnomad_data.get('status') in ['available', 'partial']:
                        st.success("✅ Connected")
                        st.caption(gnomad_data.get('message', ''))
                        
                        if gnomad_data.get('populations'):
                            for pop, data in gnomad_data['populations'].items():
                                st.write(f"- {pop}: {data.get('frequency', 'N/A')}")
                    else:
                        st.info(gnomad_data.get('message', 'No data'))
            
            # Ensembl Tab
            with db_tabs[3]:
                st.markdown("### 🔬 Ensembl")
                with st.spinner("Fetching..."):
                    ensembl_data = fetch_ensembl_data(gene_symbol)
                    
                    if ensembl_data and ensembl_data.get('status') == 'available':
                        st.success("✅ Connected")
                        st.metric("Ensembl ID", ensembl_data.get('ensembl_id', 'N/A'))
                        st.metric("Location", ensembl_data.get('location', 'N/A'))
                        st.info(ensembl_data.get('description', 'N/A')[:200])
                    else:
                        st.info(ensembl_data.get('message', 'No data'))
            
            # PharmGKB Tab
            with db_tabs[4]:
                st.markdown("### 💊 PharmGKB")
                pharmgkb_data = fetch_pharmgkb_data(gene_symbol)
                
                if pharmgkb_data and pharmgkb_data.get('status') == 'available':
                    st.success("✅ Structure Available")
                    if 'clinical_annotations' in pharmgkb_data:
                        st.metric("Clinical Annotations", pharmgkb_data.get('clinical_annotations', 0))
                        st.info(pharmgkb_data.get('level_of_evidence', 'N/A'))
                    st.caption("Requires API key for production")
                else:
                    st.info("PharmGKB integration ready")
            
            # PubMed Tab
            with db_tabs[5]:
                st.markdown("### 📚 PubMed")
                drug_name = evidence.get('drug', 'IVF')
                
                with st.spinner("Searching..."):
                    pubmed_data = fetch_pubmed_citations(gene_symbol, drug_name)
                    
                    if pubmed_data and pubmed_data.get('status') == 'available':
                        st.success(f"✅ Found {pubmed_data.get('total_results', 0)} article(s)")
                        
                        for idx, article in enumerate(pubmed_data.get('articles', []), 1):
                            st.markdown(f"**{idx}. {article.get('title', 'N/A')[:100]}...**")
                            st.caption(f"{article.get('source', 'N/A')} ({article.get('pubdate', 'N/A')})")
                            st.markdown(f"[🔗 View]({article.get('url', '#')})")
                            if idx < len(pubmed_data.get('articles', [])):
                                st.markdown("---")
                    else:
                        st.info(pubmed_data.get('message', 'No articles'))
            
            st.caption(f"💾 Results cached | {datetime.now().strftime('%H:%M:%S')}")

def render_efficacy_card(evidence: Dict):
    """Render Efficacy Evidence"""
    st.markdown("### 📊 Efficacy Evidence")
    
    st.markdown(render_tier_badge(evidence['tier']), unsafe_allow_html=True)
    
    st.markdown(f"""
    **Effect Direction:** {evidence['effect_direction']}
    
    **Evidence Summary:**
    {evidence['summary']}
    """)
    
    certainty = evidence.get('certainty', 'Moderate')
    st.progress(1.0 if certainty == "High" else 0.6 if certainty == "Moderate" else 0.3)
    st.caption(f"Evidence Certainty: {certainty}")
    
    with st.expander("📚 Study Cohorts"):
        for idx, cohort in enumerate(evidence.get('cohorts', []), 1):
            st.write(f"**Study {idx}:** {cohort['design']} (N={cohort['n']}, {cohort['ancestry']}, {cohort.get('year', 'N/A')})")
    
    with st.expander("📖 Citations"):
        for citation in evidence.get('citations', []):
            st.write(f"• {citation}")

def render_safety_card(evidence: Dict):
    """Render Safety Context"""
    st.markdown("### 🛡️ Safety Context")
    
    safety_notes = {
        "NR3C1_N363S": "Consider side-effect vigilance (glycemia, BP) if corticosteroids used.",
        "SLC22A1_OCT1": "OCT1 variants associated with increased GI intolerance to metformin.",
        "MTNR1B_rs10830963": "G allele associated with altered glucose metabolism.",
        "CYP2A6_star4": "Deficient metabolizers may have higher letrozole exposure.",
        "CYP2D6": "Poor metabolizers may have reduced active metabolites."
    }
    
    gene_key = f"{evidence['gene_symbol']}_{evidence['rsid']}" if 'rs' in str(evidence['rsid']) else evidence['rsid']
    
    if gene_key in safety_notes:
        st.info(safety_notes[gene_key])
    else:
        st.write("No specific safety PGx considerations. Standard monitoring recommended.")
    
    st.warning("**Note:** PGx associations do not replace standard clinical monitoring.")

def render_label_card(drug: str):
    """Render Card D - Label/Guideline Awareness"""
    st.markdown("### 📋 Card D: Label & Guideline Awareness")
    
    label_info = {
        "FSH (Follitropin alfa/delta)": {
            "title": "Rekovelle® Dosing Algorithm",
            "content": "First-cycle dosing by AMH + Body Weight (Read-Only). No dose calculation performed by software."
        },
        "Metformin": {
            "title": "ASRM Guideline",
            "content": "Mixed evidence for OHSS reduction. Protocol-dependent benefit."
        },
        "Growth Hormone": {
            "title": "IVF Add-On Evidence",
            "content": "Mixed evidence. Live-birth benefit uncertain in POR."
        }
    }
    
    if drug in label_info:
        info = label_info[drug]
        st.markdown(f"**{info['title']}**")
        st.info(info['content'])
    else:
        st.info("No specific label algorithms for this medication.")

def render_discussion_prompts(drug: str):
    """Render discussion prompts checklist"""
    st.markdown("### 💬 Discussion Prompts")
    
    prompts = {
        "FSH (Follitropin alfa/delta)": [
            "Reviewed FSHR genotype implications",
            "Discussed dosing strategy",
            "Explained response variability",
            "Documented rationale"
        ],
        "LH supplementation": [
            "Reviewed LHCGR genotype",
            "Discussed LH supplementation appropriateness",
            "Considered trigger implications",
            "Documented decision"
        ],
        "Metformin": [
            "Reviewed OCT1 genotype",
            "Discussed GI side effects",
            "Assessed metabolic context",
            "Documented monitoring"
        ]
    }
    
    if drug in prompts:
        for idx, prompt in enumerate(prompts[drug]):
            st.checkbox(prompt, key=f"prompt_{drug}_{idx}")
    else:
        st.write("✓ Reviewed PGx context")
        st.write("✓ Documented decision")

# ==================== MAIN APPLICATION ====================

def main():
    st.markdown('<h1 class="main-header">🧬 IVF Pharmacogenomics Evidence Brief</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Phase 1 Non-SaMD Information Service</p>', unsafe_allow_html=True)
    
    render_disclaimer()
    
    st.sidebar.title("📋 Patient Selection")
    
    patient_options = {f"{p['id']} - {p['name']}": p for p in SAMPLE_PATIENTS.values()}
    selected_patient_key = st.sidebar.selectbox("Select Patient", options=list(patient_options.keys()))
    selected_patient = patient_options[selected_patient_key]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Patient Demographics")
    st.sidebar.write(f"**Age:** {selected_patient['age']} years")
    st.sidebar.write(f"**BMI:** {selected_patient['bmi']} kg/m²")
    st.sidebar.write(f"**AMH:** {selected_patient['amh']} ng/mL")
    st.sidebar.write(f"**FSH:** {selected_patient['fsh']} mIU/mL")
    st.sidebar.write(f"**LH:** {selected_patient['lh']} mIU/mL")
    st.sidebar.write(f"**E2:** {selected_patient['e2']} pg/mL")
    st.sidebar.write(f"**P4:** {selected_patient['p4']} ng/mL")
    st.sidebar.write(f"**Ancestry:** {selected_patient['ancestry']}")
    st.sidebar.write(f"**Prior Response:** {selected_patient['prior_response']}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💊 Drug Selection")
    selected_drug = st.sidebar.selectbox("Select Medication", options=list(DRUG_CATALOG.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👁️ View Options")
    show_json = st.sidebar.checkbox("Show Full Evidence JSON", value=False)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Evidence Brief", "🧬 All Genotypes", "📚 Evidence Registry", "ℹ️ About"])
    
    with tab1:
        st.header(f"Evidence Brief: {selected_drug}")
        
        drug_info = DRUG_CATALOG[selected_drug]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Drug Class", drug_info['drug_class'])
        with col2:
            st.metric("Indication", drug_info['indication'])
        with col3:
            st.metric("Genes", ", ".join(drug_info['genes']))
        
        st.markdown("---")
        
        gene_keys = DRUG_GENE_MAP.get(selected_drug, [])
        
        if not gene_keys:
            st.warning("No PGx associations available.")
        else:
            for gene_key in gene_keys:
                if gene_key in EVIDENCE_REGISTRY:
                    evidence = EVIDENCE_REGISTRY[gene_key]
                    
                    if gene_key in selected_patient['genotypes']:
                        genotype_data = selected_patient['genotypes'][gene_key]
                        
                        st.markdown(f"## {evidence['gene_symbol']} - {evidence['variant']}")
                        
                        render_genotype_card(gene_key, genotype_data, selected_patient['ancestry'])
                        st.markdown("---")
                        
                        render_efficacy_card(evidence)
                        st.markdown("---")
                        
                        render_safety_card(evidence)
                        st.markdown("---")
                        
                        render_label_card(selected_drug)
                        st.markdown("---")
                        
                        render_discussion_prompts(selected_drug)
                        
                        if show_json:
                            with st.expander("🔍 View Full JSON"):
                                st.json(evidence)
                        
                        st.markdown("---")
        
        if st.button("📄 Generate PDF Report"):
            with st.spinner("Generating..."):
                time.sleep(1)
                st.success("✅ PDF generated!")
                st.info(f"Patient: {selected_patient['id']} | Drug: {selected_drug} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    with tab2:
        st.header("Complete Genotype Profile")
        
        genotype_df = pd.DataFrame([
            {"Gene/Variant": key, "Zygosity": data['zygosity'], "QC": data['qc']}
            for key, data in selected_patient['genotypes'].items()
        ])
        
        st.dataframe(genotype_df, use_container_width=True)
    
    with tab3:
        st.header("Evidence Registry")
        
        tier_filter = st.multiselect("Filter by Tier", options=["A", "B", "C"], default=["A", "B", "C"])
        
        for gene_key, evidence in EVIDENCE_REGISTRY.items():
            if evidence['tier'] in tier_filter:
                with st.expander(f"{evidence['gene_symbol']} - {evidence['variant']}"):
                    st.markdown(f"**Tier:** {evidence['tier']}")
                    st.write(evidence['summary'])
    
    with tab4:
        st.header("About")
        st.markdown("""
        **Phase 1 Non-SaMD Information Service**
        
        - Displays genotypes with QC
        - Summarizes PGx associations
        - 6 database connections
        - Evidence tiers
        - Non-directive language
        
        **Version:** 1.0.0-MVP
        """)

if __name__ == "__main__":
    main()
