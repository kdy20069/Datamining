#!/usr/bin/env python3
"""Verify Open Targets disease score components and direct CYP/POR associations."""
import csv,json,os,sys,urllib.request,urllib.error

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));DATA=os.path.join(ROOT,"data")
URL="https://api.platform.opentargets.org/api/v4/graphql";TODAY="2026-11-27"
DISEASES={"MONDO_0002009":"major depressive disorder","MONDO_0005090":"schizophrenia","MONDO_0005618":"anxiety disorder"}
GABA={"GABRA1":"ENSG00000022355","GABRA2":"ENSG00000151834","GABRA3":"ENSG00000011677","GABRA5":"ENSG00000186297","GABRB2":"ENSG00000145864","GABRG2":"ENSG00000113327"}
CYP={"CYP3A4":"ENSG00000160868","CYP2C19":"ENSG00000165841","POR":"ENSG00000127948"}
FIELDS="score datatypeScores { id score } datasourceScores { id score }"

def post(query):
    body=json.dumps({"query":query}).encode()
    req=urllib.request.Request(URL,data=body,headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"Datamining-OT-verification/1.0"})
    with urllib.request.urlopen(req,timeout=15) as r:return json.loads(r.read())
def write(path,rows,fields):
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def safe_json(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def remaining_pages():
    """Fetch only page 1 after the already saved page-0 direct target checks."""
    path=os.path.join(DATA,"psychiatric_cyp_check.csv")
    with open(path,newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
    fields=list(rows[0])
    disease_groups=[("MDD","MONDO_0002009",lambda d: d.get("id")=="MONDO_0002009"),
                    ("schizophrenia","MONDO_0005090",lambda d: d.get("id")=="MONDO_0005090"),
                    ("anxiety","MONDO_0005618",lambda d: d.get("id")=="MONDO_0005618"),
                    ("CTD MeSH D020258","MESH:D020258",lambda d: d.get("id")=="MESH:D020258"),
                    ("neurotoxicity-named disease","EFO_0011057",lambda d: "neurotox" in (d.get("name") or "").lower()),
                    ("seizure-related","MONDO seizure/epilepsy terms",lambda d: any(k in d.get("name","").lower() for k in ("seizure","epilep")))]
    for gene,ens in CYP.items():
        old=[r for r in rows if r.get("gene_symbol")==gene]
        count=int(next(r["target_associated_disease_count"] for r in old if r.get("target_associated_disease_count")))
        query=f'''query {{ target(ensemblId:"{ens}") {{ id approvedSymbol associatedDiseases(page:{{index:1,size:500}}) {{ count rows {{ disease {{ id name }} {FIELDS} }} }} }} }}'''
        try:
            data=post(query);t=data.get("data",{}).get("target") or {};assoc=t.get("associatedDiseases") or {};page=assoc.get("rows",[])
            hit_rows=[]
            for r in page:
                d=r.get("disease") or {};name=(d.get("name") or "").lower();did=d.get("id") or ""
                if any(k in name for k in ("depress","schizophren","anxiety","neurotox","seizure","epilep")) or did=="MESH:D020258":
                    hit_rows.append({"gene_symbol":gene,"ensembl_id":ens,"disease_id":did,"disease_name":d.get("name"),"overall_score":r.get("score"),"datatype_scores":safe_json(r.get("datatypeScores")),"datasource_scores":safe_json(r.get("datasourceScores")),"target_associated_disease_count":count,"query":query,"source_url":URL,"retrieval_date":TODAY,"status":"observed_direct_target_association_page_1"})
            old_ids={r.get("disease_id") for r in old if r.get("disease_id")}
            new_ids={r.get("disease_id") for r in hit_rows}
            rows.extend(r for r in hit_rows if r.get("disease_id") not in old_ids)
            allnames=[(r.get("disease_id","") or "",r.get("disease_name","") or "") for r in old+hit_rows]
            complete=(len(page)<500 and count<=500+len(page))
            for group,group_id,match in disease_groups:
                found=any(match({"id":did,"name":name}) for did,name in allnames)
                if found:continue
                rows.append({"gene_symbol":gene,"ensembl_id":ens,"disease_id":group_id,"disease_name":f"No {group} match in returned associatedDiseases list","overall_score":"","datatype_scores":"","datasource_scores":"","target_associated_disease_count":count,"query":query,"source_url":URL,"retrieval_date":TODAY,"status":"no_match_complete_associatedDiseases_list" if complete else "no_match_in_retrieved_pages_not_zero_proven"})
        except Exception as e:
            rows.append({"gene_symbol":gene,"ensembl_id":ens,"disease_id":"","disease_name":"page 1 query failed","overall_score":"","datatype_scores":"","datasource_scores":"","target_associated_disease_count":count,"query":query,"source_url":URL,"retrieval_date":TODAY,"status":f"failed: {type(e).__name__}: {e}"})
    write(path,rows,fields)

def main():
    if "--remaining" in sys.argv:
        remaining_pages();return
    evidence=[]
    for disease_id,disease_name in DISEASES.items():
        query=f'''query {{ disease(efoId:"{disease_id}") {{ id name associatedTargets(page:{{index:0,size:500}}) {{ count rows {{ target {{ id approvedSymbol }} {FIELDS} }} }} }} }}'''
        try:
            data=post(query);d=data.get("data",{}).get("disease") or {};rows=d.get("associatedTargets",{}).get("rows",[])
            for row in rows:
                t=row.get("target") or {};g=t.get("approvedSymbol")
                if g not in GABA:continue
                evidence.append({"disease":disease_name,"source_db":"Open Targets GraphQL","gene_symbol":g,"gene_id":"","compound_relevance_note":"Association score is not causal proof.","evidence_summary":f"overall association score={row.get('score')}; datatypeScores={safe_json(row.get('datatypeScores'))}; datasourceScores={safe_json(row.get('datasourceScores'))}; disease ID={disease_id}; target ID={t.get('id')}","query":query,"source_url":URL,"retrieval_date":TODAY,"status_or_failure_reason":"observed_with_score_components"})
            missing=set(GABA)-{r["gene_symbol"] for r in evidence if r["disease"]==disease_name}
            for g in sorted(missing):evidence.append({"disease":disease_name,"source_db":"Open Targets GraphQL","gene_symbol":g,"gene_id":"","compound_relevance_note":"Association score is not causal proof.","evidence_summary":f"Not returned among first 500 associated targets; total count={d.get('associatedTargets',{}).get('count')}","query":query,"source_url":URL,"retrieval_date":TODAY,"status_or_failure_reason":"not_in_first_500_not_zero_proven"})
        except Exception as e:
            for g in GABA:evidence.append({"disease":disease_name,"source_db":"Open Targets GraphQL","gene_symbol":g,"gene_id":"","compound_relevance_note":"","evidence_summary":"","query":query,"source_url":URL,"retrieval_date":TODAY,"status_or_failure_reason":f"failed: {type(e).__name__}: {e}"})
    # Retain the existing local GEO audit rows while replacing stale score-only OT rows.
    p=os.path.join(DATA,"psychiatric_disease_evidence.csv")
    with open(p,newline="",encoding="utf-8") as f:old=list(csv.DictReader(f))
    rows=[r for r in old if r.get("source_db")!="Open Targets GraphQL"]+evidence
    fields=list(old[0]) if old else list(evidence[0]);
    for key in evidence[0]:
        if key not in fields:fields.append(key)
    write(p,rows,fields)

    direct=[]
    for gene,ens in CYP.items():
        query=f'''query {{ target(ensemblId:"{ens}") {{ id approvedSymbol associatedDiseases(page:{{index:0,size:500}}) {{ count rows {{ disease {{ id name }} {FIELDS} }} }} }} }}'''
        try:
            data=post(query);t=data.get("data",{}).get("target") or {};assoc=t.get("associatedDiseases") or {};drows=assoc.get("rows",[])
            # Report ranked matches for psychiatric disorders and neurotoxicity/seizure by name/identifier.
            matches=[r for r in drows if any(k in (str((r.get("disease") or {}).get("id",""))+" "+str((r.get("disease") or {}).get("name",""))).lower() for k in ("mdd","depress","schizophren","anxiety","neurotox","seizure","epilep"))]
            for r in matches:
                d=r.get("disease") or {};direct.append({"gene_symbol":gene,"ensembl_id":ens,"disease_id":d.get("id"),"disease_name":d.get("name"),"overall_score":r.get("score"),"datatype_scores":safe_json(r.get("datatypeScores")),"datasource_scores":safe_json(r.get("datasourceScores")),"target_associated_disease_count":assoc.get("count"),"query":query,"source_url":URL,"retrieval_date":TODAY,"status":"observed_direct_target_association"})
            if not matches:
                status="no_match_in_complete_associatedDiseases_list" if assoc.get("count",501)<=len(drows) else "no_match_in_first_500_not_zero_proven"
                direct.append({"gene_symbol":gene,"ensembl_id":ens,"disease_id":"","disease_name":"","overall_score":"","datatype_scores":"","datasource_scores":"","target_associated_disease_count":assoc.get("count"),"query":query,"source_url":URL,"retrieval_date":TODAY,"status":status})
        except Exception as e:direct.append({"gene_symbol":gene,"ensembl_id":ens,"disease_id":"","disease_name":"","overall_score":"","datatype_scores":"","datasource_scores":"","target_associated_disease_count":"","query":query,"source_url":URL,"retrieval_date":TODAY,"status":f"failed: {type(e).__name__}: {e}"})
    write(os.path.join(DATA,"psychiatric_cyp_check.csv"),direct,["gene_symbol","ensembl_id","disease_id","disease_name","overall_score","datatype_scores","datasource_scores","target_associated_disease_count","query","source_url","retrieval_date","status"])

if __name__=="__main__":main()
