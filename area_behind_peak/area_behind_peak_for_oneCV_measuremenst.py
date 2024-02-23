# calculation area behind reduction peak in a cycle voltammogram 
# This code asks for an SCV file input file, which acquired from the Zahner potentiostat setup.

import numpy as np
import pandas as pd
from scipy.integrate import simpson
from scipy import integrate
import matplotlib.pylab as plt
from matplotlib.ticker import EngFormatter
import os
import glob

REF_POTENTIAL = 0.53  # Reference potential vs. Hydrogen reference electrode

def load_data(filename, header_rows=12, sep=','):
    """Load CSV data, skipping the initial header rows."""
    try:
        df = pd.read_csv(filename, sep=sep, header=header_rows)
        return df
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None


def rename_columns(df: pd.DataFrame):
    """Rename columns for consistency and readability."""
    df.rename(columns={"Current/A": "Current", "Time/s": "Time", "Potential/V": "Potential"}, inplace=True)

def convert_potential_to_RHE(df: pd.DataFrame, ref_pot: float):
    """Convert and add a column for potential vs. RHE."""
    df['Potential (V vs. RHE)'] = df['Potential'] + ref_pot



def closest(list, k):
    lst = np.asanyarray(list)
    idx = (np.abs(lst - k)).argmin()
    return idx

def integral(x,y,i,f):
    '''   this fuction integrate the are y(X) from x=i to x=f

    '''
    xdata = np.asanyarray(x); ydata = np.asanyarray(y)
    xi = xdata[i:f]; yi = ydata[i:f]
    integ = np.trapz(yi,x = xi ,axis=-1)
    return integ


formatter0 = EngFormatter(unit='A')
filePath = input('Input file directory:\n')
dirs=os.path.join(filePath,'*.csv')
filelist=glob.glob(dirs)

header = ['file','area']
area_list =[]
cycle_list=[]

for filename in filelist:
    df = pd.read_csv(filename,header=12, sep=',')
    rename_columns(df)
    convert_potential_to_RHE(df, REF_POTENTIAL)
    #df = pd.read_csv(filename, sep=',', error_bad_lines=False, warn_bad_lines=True)
    pot_max = np.argmax(df['Potential (V vs. RHE)'])
    ind_min= closest(df['Potential (V vs. RHE)'][pot_max:],1.25)+ pot_max
    ind_max= closest(df['Potential (V vs. RHE)'][pot_max:],0.45)+ pot_max
    y1= df['Current'][ind_min]
    y2 = df['Current'][ind_max]
    x_values = [df['Time'][ind_min], df['Time'][ind_max]]
    y_values = [y1, y2]
    df_shifted=df.copy()
    df_shifted['Current']-=np.maximum(y1,y2)
    length= df_shifted['Time'][ind_max]-df_shifted['Time'][ind_min]
    y1_shifted = df_shifted['Current'][ind_min]
    y2_shifted = df_shifted['Current'][ind_max]

    area_triangle=np.minimum(y1_shifted,y2_shifted)/2*length
    print(y1_shifted,y2_shifted,area_triangle)
    plt.plot(df['Time'], df['Current'], )
    plt.vlines(df['Time'][ind_min], df['Current'].min(), df['Current'][ind_min], ls=":", colors='k')
    plt.vlines(df['Time'][ind_max],df['Current'].min(), df['Current'][ind_max], ls=":", colors='k')
    plt.plot(x_values, y_values )
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter0)
    figname=f'{filename}.png'
    outname = os.path.join(filePath,figname)
    plt.savefig(outname, dpi=300)
    behind_peK = integral(df['Time'],df_shifted['Current'],ind_min,ind_max)
    cycle_list.append(filename)
    plt.clf()
    net_area =behind_peK-area_triangle
    area_list.append(np.abs(net_area))
df_area=pd.DataFrame({'Cycle': cycle_list,'area':area_list})   
outname=os.path.join(filePath,'area_behind_peak.csv')
print(outname)
sorted_df =df_area.sort_values(by='Cycle',ascending=True)
sorted_df.to_csv(outname)
sorted_df.head(5)
