import pandas as pd

# 1. UP 유전자 목록 저장
up_genes = ['HMGCR', 'HMGCS1', 'FDFT1', 'ACAT2', 'TMEM97', 'CBLB', 'ELOVL6', 'WDTC1', 'PIK3C2B']
with open('haloperidol_up_genes.txt', 'w') as f:
    f.write('\n'.join(up_genes))

# 2. Enrichr 분석 결과 (Reactome Pathways 2024 등) 저장
enrichr_data = [
    ['Reactome 2024', 'Cholesterol Biosynthesis', '4/9', '7.9e-9', 'R-HSA-191273', 'https://reactome.org/content/detail/R-HSA-191273', '2026-11-23'],
    ['Reactome 2024', 'Activation of Gene Expression by SREBP', '4/9', '2.6e-8', 'R-HSA-2426168', 'https://reactome.org/content/detail/R-HSA-2426168', '2026-11-23'],
    ['WikiPathways 2024', 'Mevalonate Arm of Cholesterol Biosynthesis', '4/9', '5.1e-10', 'WP4190', 'https://www.wikipathways.org/pathways/WP4190.html', '2026-11-23'],
    ['GO BP 2025', 'Cholesterol Biosynthetic Process', '3/9', '4.5e-6', 'GO:0006695', 'https://amigo.geneontology.org/amigo/term/GO:0006695', '2026-11-23']
]
enrichr_df = pd.DataFrame(enrichr_data, columns=['Library', 'Top_Term', 'Hits', 'Adj_p_value', 'Stable_Term_ID', 'Term_Record_URL', 'Term_ID_Checked_On'])
enrichr_df.to_csv('enrichr_top_pathways.csv', index=False)

# 3. 프로젝트 제출용 증거 기록 및 한계점(Inference Limits) 파일 생성
evidence_text = """[LINCS Evidence Row]
- Search Term: haloperidol
- Signature ID: LINCSCP_22231
- Context: HepG2 (Liver cancer cells), 10uM, 6h
- Result: 9 genes UP, 5 genes DOWN (filtered by p < 0.01)
- Pathway Analysis (Enrichr): Cholesterol Biosynthesis (Reactome 2024, Adj p = 7.9e-9)
- Pathway term identifiers checked 2026-11-23: Reactome R-HSA-191273 / R-HSA-2426168, WikiPathways WP4190, GO:0006695.
- Provenance limitation: Enrichr request payload, source gene-set library response, and original run date were not archived; the p-values are retained from the existing local record and were not independently rerun.

[Inference Limits (데이터의 한계점)]
1. 간세포(Liver cells)에서의 콜레스테롤 합성 증가 결과이므로, 뇌 신경독성(neurotoxicity)이나 뇌에 미치는 영향을 직접적으로 증명할 수 없습니다.
2. 단일 약물(Single-drug) 시그니처이므로, 혼합 독성(mixture synergy)을 이 데이터만으로 주장할 수 없습니다.
"""
with open('lincs_evidence_row.txt', 'w') as f:
    f.write(evidence_text)

print("LINCS 증거 자료(유전자 목록, Enrichr 결과, 한계점 기록)가 성공적으로 저장되었습니다!")
