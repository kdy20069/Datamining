import pandas as pd
import matplotlib.pyplot as plt

# 1. 데이터 읽기 및 정렬 (교안과 동일하게 위아래 순서 맞춤)
df = pd.read_csv('haloperidol_signature.csv')
df = df.sort_values(by='Differential_Expression', ascending=True)

# 2. 색상 설정 (발현 증가 UP은 보라색, 발현 감소 DOWN은 붉은색)
colors = ['#CC4F59' if val < 0 else '#5C4DB2' for val in df['Differential_Expression']]

# 3. 그래프 그리기 (가로 막대 그래프)
plt.figure(figsize=(10, 7))
bars = plt.barh(df['Gene_Symbol'], df['Differential_Expression'], color=colors, height=0.6)

# 4. 막대 끝에 수치 적어주기
for bar, val in zip(bars, df['Differential_Expression']):
    if val > 0:
        plt.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"+{val:.2f}", va='center', fontsize=10)
    else:
        plt.text(val - 0.1, bar.get_y() + bar.get_height()/2, f"{val:.2f}", va='center', ha='right', fontsize=10)

# 5. 기준선(0) 및 텍스트 꾸미기
plt.axvline(0, color='black', linewidth=1)
plt.text(3, 8.5, 'UP (9 genes)', color='#5C4DB2', fontsize=12, fontweight='bold')
plt.text(2.5, 1.5, 'DOWN (5 genes)', color='#CC4F59', fontsize=12, fontweight='bold')

plt.xlabel('Differential expression (iLINCS value; > 0 = up, < 0 = down)', fontsize=11)
plt.title('Haloperidol in liver cells: changed genes (LINCSCP_22231)', fontsize=14, pad=15)
plt.xlim(-3, 5.5)
plt.tight_layout()

# 6. 이미지 저장
plt.savefig('haloperidol_lincs_plot.png', dpi=300)
print("LINCS Haloperidol signature plot successfully saved as 'haloperidol_lincs_plot.png'!")
