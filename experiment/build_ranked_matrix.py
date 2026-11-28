#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a source-derived observed/inferred 2x3 pesticide–benzodiazepine matrix.

Observed = an explicit curated database or bioassay record, or a peer-reviewed
record with a PMID, connecting that compound to that target. Inferred = a
relationship explicitly labeled inferred in evidence_table.csv, or an indirect
STRING network-neighbor extension; neither is counted as observed.
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

PESTICIDES = ["Permethrin", "Prallethrin", "PBO"]
BENZOS = ["Diazepam", "Alprazolam"]
GENE_IDS = {"CYP3A4":"1576","CYP2C19":"1557","POR":"5447","GABRA1":"2554","GABRA2":"2555","GABRA3":"2556","GABRA5":"2558","GABRB2":"2561","GABRG2":"2566"}
SUBUNIT_IDS = {v:k for k,v in GENE_IDS.items() if k.startswith("GAB")}

def read(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def read_local(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(f"[OK] {os.path.relpath(path, ROOT)}: {len(rows)} rows", flush=True)

def load_evidence():
    evidence = read_local(os.path.join(HERE, "evidence_table.csv"))
    expanded = read("expanded_db_evidence.csv")
    aids = read("pubchem_aids.csv")
    ctd = read("ctd_direction_audit.csv")
    obs = {x:{} for x in PESTICIDES+BENZOS}
    inferred = {x:{} for x in PESTICIDES+BENZOS}
    meta = {x:{} for x in PESTICIDES+BENZOS}

    # PMID-backed CTD interaction rows: measured metabolic relationship, not induction/inhibition.
    for r in ctd:
        if r.get("ChemicalName") == "Permethrin" and r.get("GeneSymbol") in GENE_IDS and r.get("PMID"):
            node=r["GeneSymbol"]; obs["Permethrin"].setdefault(node,[]).append(f"CTD PMID {r['PMID']}: {r.get('ActionText','')}")
            meta["Permethrin"].setdefault(node, set()).add("PMID")

    # Unique PubChem assay records for Prallethrin; one record remains per AID.
    for r in aids:
        if r.get("ChemicalName") == "Prallethrin" and r.get("GeneSymbol") in GENE_IDS:
            node=r["GeneSymbol"]; obs["Prallethrin"].setdefault(node,[]).append(f"PubChem AID {r.get('AID')} {r.get('Endpoint')} {r.get('Outcome')} {r.get('Value_uM')} uM")
            meta["Prallethrin"].setdefault(node, set()).add("bioassay")

    # ChEMBL archived activities from expanded_db_evidence.csv.
    for r in expanded:
        if r.get("candidate_compound") == "PBO" and r.get("source_db") == "ChEMBL archived activity observed" and r.get("target_gene") in GENE_IDS and r.get("status_or_failure_reason") == "observed_archived_source":
            node=r["target_gene"]; obs["PBO"].setdefault(node,[]).append(r.get("interaction_direction_note","")); meta["PBO"].setdefault(node,set()).add("bioassay")

    # Benzodiazepine curated KEGG records. The target field lists individual GABA-A
    # subunit GeneIDs; expand only those explicitly present in that source note.
    for r in expanded:
        drug=r.get("candidate_compound")
        if drug not in BENZOS or r.get("source_db") != "KEGG Drug observed" or r.get("status_or_failure_reason") != "observed": continue
        node=r.get("target_gene","")
        if node in GENE_IDS:
            obs[drug].setdefault(node,[]).append(r.get("interaction_direction_note","")); meta[drug].setdefault(node,set()).add("DB_curation")
        note=r.get("interaction_direction_note","")
        if "TARGET field" in note:
            for gene_id,symbol in SUBUNIT_IDS.items():
                if re.search(rf"\b{gene_id}\b",note):
                    obs[drug].setdefault(symbol,[]).append(note); meta[drug].setdefault(symbol,set()).add("DB_curation")

    # The row is explicitly marked inferred and names all three insecticides plus CYP nodes.
    for r in evidence:
        if r.get("link_type") != "inferred": continue
        src=r.get("source_node",""); dst=r.get("target_node","")
        for chem in PESTICIDES + BENZOS:
            if chem.lower() in src.lower():
                for node in GENE_IDS:
                    if re.search(rf"\b{node}\b",dst):
                        inferred[chem].setdefault(node,[]).append(f"{r.get('source_db')} {r.get('record_id')}: {r.get('value_unit_or_status')}")
    # STRING supplies a CYP3A4–POR functional neighbor edge; this supports a network
    # extension hypothesis only and is not direct chemical–POR evidence.
    has_string_por=any(r.get("source_db","").startswith("STRING") and "CYP3A4-POR" in r.get("record_id","") for r in evidence)
    if has_string_por:
        for chem in PESTICIDES + BENZOS:
            if "CYP3A4" in obs[chem] or "CYP3A4" in inferred[chem]:
                inferred[chem].setdefault("POR",[]).append("STRING CYP3A4-POR functional association; network-neighbor extension only")

    # Observed classifications take precedence when the same node also appears in an inference.
    return obs, inferred, meta, evidence, expanded, aids, ctd

def main():
    obs, inf, meta, evidence, expanded, aids, ctd = load_evidence()
    pairs=[]
    for pesticide in PESTICIDES:
        for benzo in BENZOS:
            shared_obs=sorted(set(obs[pesticide]) & set(obs[benzo]))
            left_all=set(obs[pesticide]) | set(inf[pesticide]); right_all=set(obs[benzo]) | set(inf[benzo])
            shared_inf=sorted((left_all & right_all) - set(shared_obs))
            pmid_nodes=sorted(n for n in shared_obs if "PMID" in meta[pesticide].get(n,set()))
            assay_nodes=sorted(n for n in shared_obs if "bioassay" in meta[pesticide].get(n,set()))
            details=[]
            for n in shared_obs:
                details.append(n)
            summary=f"Observed shared: {', '.join(shared_obs) if shared_obs else 'none'}; inferred shared: {', '.join(shared_inf) if shared_inf else 'none'}."
            if pesticide=="Permethrin" and benzo=="Diazepam":
                summary += " CTD PMID 24548679 reports CYP3A4 and CYP2C19 increase permethrin metabolism; KEGG Diazepam METABOLISM lists both enzymes."
            elif pesticide=="Prallethrin" and benzo=="Diazepam":
                summary += " PubChem AIDs identify CYP3A4/CYP2C19 assay activity; assay species is recorded as Unknown in the source table."
            elif pesticide=="PBO":
                summary += " PBO CYP3A4 observations include 501.2 nM Potency (one Active, one Not Active) and two 3000 nM IC50 records; do not collapse mixed calls into a single active claim."
            if "POR" in shared_inf:
                summary += " POR is an indirect STRING network-neighbor inference, not a direct compound–POR observation."
            pairs.append({"pesticide":pesticide,"benzodiazepine":benzo,"shared_nodes":";".join(sorted(set(shared_obs)|set(shared_inf))),
                "observed_shared_nodes":";".join(shared_obs),"observed_shared_count":len(shared_obs),
                "inferred_shared_nodes":";".join(shared_inf),"inferred_shared_count":len(shared_inf),
                "pmid_supported_shared_nodes":";".join(pmid_nodes),"bioassay_supported_shared_nodes":";".join(assay_nodes),
                "core_mechanism_summary":summary,"rank":"","observed_rank":"","tie_break_order":"PMID priority → Bioassay order (then alphabetical for display)","rank_basis":""})

    # Lexicographic tie-break: more observed shared nodes, then more PMID-backed
    # shared nodes, then more distinct observed shared nodes with bioassay support.
    # Inferred counts never outrank observed evidence.
    ranked=sorted(pairs,key=lambda r:(-r["observed_shared_count"],-len([x for x in r["pmid_supported_shared_nodes"].split(";") if x]),-len([x for x in r["bioassay_supported_shared_nodes"].split(";") if x]),r["pesticide"],r["benzodiazepine"]))
    rank=0; prior=None
    for i,r in enumerate(ranked,1):
        key=(r["observed_shared_count"],len([x for x in r["pmid_supported_shared_nodes"].split(";") if x]),len([x for x in r["bioassay_supported_shared_nodes"].split(";") if x]))
        if key!=prior: rank=i; prior=key
        r["rank"]=rank
        r["rank_basis"]=f"observed_shared_count desc; PMID-supported shared nodes desc; bioassay-supported shared nodes desc; tie group rank={rank}"
    # User-facing observed rank is based on observed count only; evidence-source
    # tie-breaks remain represented by `rank` and the explicit order column.
    counts=sorted({r["observed_shared_count"] for r in ranked},reverse=True)
    for r in ranked:
        count=r["observed_shared_count"];competition_rank=1+sum(1 for x in ranked if x["observed_shared_count"]>count)
        tied=sum(1 for x in ranked if x["observed_shared_count"]==count)-1
        r["observed_rank"]=f"{competition_rank} (tie)" if tied else str(competition_rank)
    out=os.path.join(HERE,"pair_matrix_2x3.csv")
    fields=["rank","observed_rank","tie_break_order","pesticide","benzodiazepine","shared_nodes","observed_shared_nodes","observed_shared_count","inferred_shared_nodes","inferred_shared_count","pmid_supported_shared_nodes","bioassay_supported_shared_nodes","core_mechanism_summary","rank_basis"]
    write(out,ranked,fields)

    # Exact GeneSymbol intersections and observed Open Targets score rows from input CSVs.
    ctd_genes=read("ctd_neurotoxicity_gene_audit.csv")
    candidate=set(GENE_IDS)
    live_ctd=read("ctd_neurotoxicity_live.csv") if os.path.exists(os.path.join(DATA,"ctd_neurotoxicity_live.csv")) else []
    live_genes=[r for r in live_ctd if r.get("record_type")=="disease_gene" and r.get("status")=="observed"]
    ctd_symbols={r.get("gene_symbol","") for r in live_genes} if live_genes else {r.get("GeneSymbol","") for r in ctd_genes}
    exact=sorted(candidate & ctd_symbols)
    psych=read("psychiatric_disease_evidence.csv")
    ot=[r for r in psych if r.get("source_db")=="Open Targets GraphQL" and r.get("gene_symbol") and r.get("status_or_failure_reason") in {"observed_in_first_500_associated_targets","observed_with_score_components"}]
    ctd_source="data/ctd_neurotoxicity_live.csv" if live_genes else "data/ctd_neurotoxicity_genes.csv"
    ctd_retrieval="2026-11-27" if live_genes else "Local extract (original query date unrecorded)"
    ctd_query="Exact symbol intersection from live CTD MESH:D020258 disease-gene response and fixed 9 candidate target list" if live_genes else "Exact symbol intersection of local CTD extract and fixed 9 candidate target list; live CTD retrieval failed"
    ctd_note="Live CTD disease-gene records retrieved and intersected by exact symbol." if live_genes else "CTD live query failed; 0 means exact symbol overlap in the local extract only. Original query date unrecorded."
    outrows=[{"summary":"CTD neurotoxicity GeneSymbol ∩ 9 candidate target symbols","n_genes":len(exact),"genes":";".join(exact),"source_count":len(live_genes) if live_genes else len(ctd_genes),"query":ctd_query,"source_url":ctd_source,"retrieval_date":ctd_retrieval,"note":ctd_note},
        {"summary":"Open Targets candidate-target psychiatric associations","n_genes":len(ot),"genes":";".join(sorted(set(r["gene_symbol"] for r in ot))),"source_count":len(ot),"query":"Count rows with status=observed_in_first_500_associated_targets in psychiatric_disease_evidence.csv","source_url":"data/psychiatric_disease_evidence.csv","retrieval_date":"2026-11-27","note":"Rows are disease-gene pairs; scores are in source CSV. Does not assert absent genes have zero score."}]
    write(os.path.join(HERE,"gene_overlap_summary.csv"),outrows,["summary","n_genes","genes","source_count","query","source_url","retrieval_date","note"])
    print("Observed definition: curated database/bioassay record or peer-reviewed PMID record.",flush=True)
    print("Rank 1 pair(s): "+"; ".join(f"{r['pesticide']} × {r['benzodiazepine']}" for r in ranked if r["rank"]==1),flush=True)

if __name__=="__main__": main()
