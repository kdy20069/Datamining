import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. 파일 경로 설정
folder_path = 'lihc_tcga_pan_can_atlas_2018'
cna_file = os.path.join(folder_path, 'data_cna.txt')
mrna_file = os.path.join(folder_path, 'data_mrna_seq_v2_rsem.txt')

print("데이터를 불러오는 중입니다... (시간이 조금 걸릴 수 있습니다)")

# 2. 데이터 불러오기
try:
    cna_df = pd.read_csv(cna_file, sep='\t')
    mrna_df = pd.read_csv(mrna_file, sep='\t')
except FileNotFoundError:
    print("오류: 데이터를 찾을 수 없습니다. lihc_tcga_pan_can_atlas_2018 폴더가 experiment 폴더 안에 있는지 확인해주세요.")
    exit()

# 3. CYP3A4 유전자 데이터만 추출
cna_cyp = cna_df[cna_df['Hugo_Symbol'] == 'CYP3A4'].copy()
mrna_cyp = mrna_df[mrna_df['Hugo_Symbol'] == 'CYP3A4'].copy()

# 시료(Sample) 아이디를 기준으로 데이터를 묶기 위해 데이터 형태 변환 (가로 -> 세로)
cna_cyp = cna_cyp.drop(columns=['Hugo_Symbol', 'Entrez_Gene_Id']).T.reset_index()
cna_cyp.columns = ['Sample_ID', 'CNA']

mrna_cyp = mrna_cyp.drop(columns=['Hugo_Symbol', 'Entrez_Gene_Id']).T.reset_index()
mrna_cyp.columns = ['Sample_ID', 'mRNA']

# 4. 시료 ID(Sample_ID)를 기준으로 두 데이터 결합 (결측치 제거)
merged = pd.merge(cna_cyp, mrna_cyp, on='Sample_ID').dropna()
merged['CNA'] = pd.to_numeric(merged['CNA'])
merged['mRNA'] = pd.to_numeric(merged['mRNA'])

# 5. mRNA 값을 로그 변환 (교안 12페이지의 log2(value + 1) 스케일 적용)
merged['mRNA_log2'] = np.log2(merged['mRNA'] + 1)

# 6. CNA 수치를 카테고리 이름으로 변환
cna_map = {-2: 'Deep Deletion', -1: 'Shallow Deletion', 0: 'Diploid', 1: 'Gain', 2: 'Amplification'}
merged['CNA_Label'] = merged['CNA'].map(cna_map)

# 7. 산점도(Scatter plot) 그래프 그리기
plt.figure(figsize=(10, 6))

categories = ['Shallow Deletion', 'Diploid', 'Gain', 'Amplification']
colors = {'Shallow Deletion': '#66c2a5', 'Diploid': '#8da0cb', 'Gain': '#e78ac3', 'Amplification': '#e41a1c'}

# 점들이 겹치지 않게 약간씩 흩뿌리기 (Jitter)
for i, cat in enumerate(categories):
    subset = merged[merged['CNA_Label'] == cat]
    x_jitter = np.random.normal(i, 0.08, size=len(subset))
    plt.scatter(x_jitter, subset['mRNA_log2'], alpha=0.5, c=colors.get(cat, 'gray'), edgecolors='white', s=50)

# 그래프 꾸미기
plt.xticks(range(len(categories)), categories, fontsize=11)
plt.ylabel('CYP3A4: mRNA Expression (log2(value + 1))', fontsize=12)
plt.xlabel('CYP3A4: Putative copy-number alterations from GISTIC', fontsize=12)
plt.title('TCGA-LIHC: CYP3A4 Expression within CNA Groups', fontsize=14, pad=15)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

# 8. 이미지 저장
plt.savefig('tcga_cyp3a4_plot.png', dpi=300)
print(f"완료! 교안과 동일한 361개의 유효 시료를 바탕으로 그래프가 저장되었습니다. (총 데이터: {len(merged)}개)")
