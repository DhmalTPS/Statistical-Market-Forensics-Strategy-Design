from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path(r".\output")
REGIME_FILE = OUTPUT_DIR / "13_regime_cum_table.csv"
TRANS_FILE = OUTPUT_DIR / "14_transition_matrix.csv"

reg_df = pd.read_csv(REGIME_FILE)
df = reg_df[["day","Final"]].copy()
df = df.sort_values("day").reset_index(drop=True)

print("\nInput columns:\n",reg_df.columns.tolist())
print("\nInput shape:\n",reg_df.shape)
print("\nRegime sequence:\n",df.to_string(index=False))

reg = ["MEAN_REVERTING","RANDOM_WALK_LIKE","MOMENTUM","MIXED_INCONCLUSIVE"]
trans_df = pd.DataFrame(0,index=reg,columns=reg,dtype=int)

for i in range(len(df) - 1):
    curr_reg = df.loc[i,"Final"]
    next_reg = df.loc[i+1,"Final"]
    if curr_reg in reg and next_reg in reg: trans_df.loc[curr_reg, next_reg] += 1

trans_mat = trans_df.div(trans_df.sum(axis=1).replace(0, pd.NA),axis=0)
trans_mat.to_csv(TRANS_FILE)

print("\nTransition Counts:\n",trans_df)
print("\nEmpirical Transition Matrix:\n",trans_mat)
print("\nRow sums:\n",trans_mat.sum(axis=1))