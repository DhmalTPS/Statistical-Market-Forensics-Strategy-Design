# ls; ls notebooks; ls results; ls output; ls output/03_day_returns; ls output/04_day_acf; ls output/05_intraday_season

from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None

DATA_DIR = Path('EBX_Dataset')
OUTPUT_DIR = Path('output')
RESULTS_DIR = Path('results')
POOL_RET_DIR = OUTPUT_DIR / "03_pooled_returns.csv"
POOL_STAT_DIR = OUTPUT_DIR / "03_pooled_statistics.csv"
RETURN_DIR = OUTPUT_DIR / "03_day_returns"

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']

pool_df = pd.read_csv(POOL_RET_DIR,usecols=['day','Time','Price']+lvar)
stats_df = pd.read_csv(POOL_STAT_DIR)
stats_df = stats_df[stats_df['variable'].isin(lvar)].copy()

for v in lvar:
    s = pool_df[v].dropna()
    stats_df.loc[stats_df['variable']==v,'q00.1']=s.quantile(0.001)
    stats_df.loc[stats_df['variable']==v,'q99.9']=s.quantile(0.999)
stats_df.to_csv(OUTPUT_DIR/f'06_distribution_stats.csv',index=False)

# NORMALITY TESTS
TEST_ALPHA = 0.05
TEST_DAYS = comp_keys #[1,10,19,28,37,46,55,64,82]

def normality_test(ser,scp,day,hor,alp):
    s = ser.dropna()
    jab = stats.jarque_bera(s)
    dag = stats.normaltest(s)
    res = []
    res.append({
        'scope':scp,
        'day':day,
        'horizon':hor,
        'test':'Jarque_Bera',
        'no.':len(s),
        'statistic':jab.statistic,
        'p_value':jab.pvalue,
        'alpha':alp,
        'reject_normality':jab.pvalue<alp
    })
    res.append({
        'scope':scp,
        'day':day,
        'horizon':hor,
        'test':'D\'Agostino_K2',
        'no.':len(s),
        'statistic':dag.statistic,
        'p_value':dag.pvalue,
        'alpha':alp,
        'reject_normality':dag.pvalue<alp
    })
    return res

norm_test=[]
for v in lvar: norm_test+=normality_test(pool_df[v].dropna(),'pooled','ALL',v[8:],TEST_ALPHA)
for d in TEST_DAYS:
    df = pd.read_csv(RETURN_DIR/f'day{d}_returns.csv',usecols=lvar)
    for v in lvar: norm_test+=normality_test(df[v].dropna(),'day',str(d),v[8:],TEST_ALPHA)
norm_df = pd.DataFrame(norm_test)
norm_df.to_csv(OUTPUT_DIR/'06_normality_test.csv',index=False)
print(norm_df)

def normal_histogram(col,hor):
    s = pool_df[col].dropna()
    myu = s.mean()
    sig = s.std()
    x = np.linspace(s.quantile(0.001),s.quantile(0.999),1000)
    pdf = stats.norm.pdf(x,loc=myu,scale=sig)
    plt.hist(s,bins=200,density=True,alpha=0.6,label='Emperical Returns')
    plt.plot(x,pdf,linewidth=2,label='Fitted Gussian')
    plt.xlabel(f'{hor} log return')
    plt.ylabel('Probability Density')
    plt.title(f'EBX Pooled {hor} Returns vs Gaussian')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR/f'06_norm_hist_{col}.png',dpi=150)
    plt.show()

def normal_qqplot(col,hor):
    s = pool_df[col].dropna()
    stats.probplot(s,dist='norm',plot=plt)
    plt.title(f'Normal QQ Plot (EBX {hor} Returns)')
    plt.xlabel('Theoretical Normal Quantiles')
    plt.ylabel('Observed Return Quantiles')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR/f'06_norm_qq_{col}.png',dpi=150)
    plt.show()

for v in lvar: normal_histogram(v,v[-2::1])
for v in lvar: normal_qqplot(v,v[-2::1])    



