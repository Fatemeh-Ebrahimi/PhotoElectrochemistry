#%%This program seperate cycles in a CV measurement and the visualize them in Shiny
#importing libreries
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from matplotlib.ticker import EngFormatter
#loading data
df = pd.read_csv('30cycle.csv',sep=',',header=12)
#%%
df.head()
# %%renaming and adding cycle column
df.rename(columns={"Current/A": "Current"},inplace=True)
df.rename(columns={"Time/s": "Time"},inplace=True)
df.rename(columns={"Potential/V": "Potential"},inplace=True)
df['cycle']=1
# %%
#Converting potential
ref_potential= 0.53
df['Potetial (V vs.RHE)']= df['Potential']+ref_potential
# %%
df.head(5)
# %%
#%%

#peaks function
def find_peak_indexes(df: pd.DataFrame, column_name: str):
    target_array = (np.array(-df[column_name]) )
    # Find peaks
    peaks, _ = find_peaks(target_array)
    return peaks
#%%
# finding peaks
column_name = 'Potential'
Min_indexes = find_peak_indexes(df, column_name)

for peak in Min_indexes:
    print(f"Minimum Found: {df[column_name][peak]} (V) at index {peak}")  
# %%
cycle_dataframes = []
start_index = 0
for peak in ((Min_indexes)):
    cycle_df = df[start_index:peak+1]
    cycle_dataframes.append(cycle_df)
    start_index = peak
cycle_last = df[peak:] 
cycle_dataframes.append(cycle_last)    
print(f"Split the dataframe into {len(cycle_dataframes)} cycles")
# %%
#print(len(cycle_dataframes[2]))
#%%
formatter0 = EngFormatter(unit='A')
for i in range(len(cycle_dataframes)):
    cycle_dataframes[i]['Cycle']=(i+1)
    cycle_dataframes[i].to_csv(f'Cycle{i+1}.csv')
    plt.plot(cycle_dataframes[i]['Potential'],cycle_dataframes[i]['Current'], label=f'Cycle{i+1}')
    plt.ylabel('Current(A)')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter0)
    plt.xlabel('Potetial (V vs.RHE)')
    plt.legend()
    #plt.savefig(f'Cycle{i+1}.png',dpi=300)
plt.show() 
# %%
