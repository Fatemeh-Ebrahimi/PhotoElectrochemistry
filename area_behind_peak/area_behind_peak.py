# This program is used on the separate cycles in a CV measurement and calculation area behind the reduction peak
import numpy as np
import pandas as pd
from scipy.integrate import simpson
from scipy import integrate
import matplotlib.pylab as plt
from matplotlib.ticker import EngFormatter
import os
import glob

def closest(list, k):
    lst = np.asanyarray(list)
    idx = (np.abs(lst - k)).argmin()
    return idx

def integral(x,y,i,f):
    xdata = np.asanyarray(x); ydata = np.asanyarray(y)
    xi = xdata[i:f]; yi = ydata[i:f]
    #print(len(xdata),len(ydata))
    integ = np.trapz(yi,x = xi ,axis=-1)
    #integ = integrate.simps(yi,x = xi, dx = 1,axis=0)
    return integ


formatter0 = EngFormatter(unit='A')
filePath = input('Input file directory:\n')
dirs=os.path.join(filePath,'*.csv')
filelist=glob.glob(dirs)

header = ['cycle','area']
area_list =[]
cycle_list=[]

for filename in filelist:
    df = pd.read_csv(filename, sep=',')
    print(filename)
    pot_max = np.argmax(df['Potetial (V vs.RHE)'])
    ind_min= closest(df['Potetial (V vs.RHE)'][pot_max:],1.4)+ pot_max
    ind_max= closest(df['Potetial (V vs.RHE)'][pot_max:],0.8)+ pot_max
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

    #print(df['Potetial (V vs.RHE)'][ind_min])
    #print(df['Potetial (V vs.RHE)'][ind_max])
    #print (df['Time'][ind_min],df['Time'][ind_max])
    #print (ind_min,ind_max)
    #plt.plot(df['Time'],df['Potetial (V vs.RHE)'])
#Plotting shofted data baced on calculations:
    #plt.plot(df['Time'],df_shifted['Current'],)
    #plt.vlines(df['Time'][ind_min],df_shifted['Current'].min(),df_shifted['Current'][ind_min],ls=":",colors='k')
    #plt.vlines(df['Time'][ind_max],df_shifted['Current'].min(),df_shifted['Current'][ind_max],ls=":",colors='k')
   # plt.hlines(0,df['Time'].min(),df['Time'].max(), ls="--",lw=0.5, colors="red")
    #plt.plot(x_values, y_values-y1)
# Plotting real data
    plt.plot(df['Time'], df['Current'], )
    plt.vlines(df['Time'][ind_min], df['Current'].min(), df['Current'][ind_min], ls=":", colors='k')
    plt.vlines(df['Time'][ind_max],df['Current'].min(), df['Current'][ind_max], ls=":", colors='k')
    #plt.hlines(0, df['Time'].min(), df['Time'].max(), ls="--", lw=0.5, colors="red")
    plt.plot(x_values, y_values )
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter0)
    figname=f'{filename}.png'
    outname = os.path.join(filePath,figname)
    plt.savefig(outname, dpi=300)
    behind_peK = integral(df['Time'],df_shifted['Current'],ind_min,ind_max)
    cycle_list.append(df['Cycle'][3])
    plt.clf()
    #plt.show()
    net_area =behind_peK-area_triangle
    #print(net_area)
    area_list.append(np.abs(net_area))
df_area=pd.DataFrame({'Cycle': cycle_list,'area':area_list})   
outname=os.path.join(filePath,'area_behind_peak.csv')
print(outname)
sorted_df =df_area.sort_values(by='Cycle',ascending=True)
sorted_df.to_csv(outname)
sorted_df.head(5)
#print(df_area.head)
#print(sorted_df.head)
#print(area_list)
#print(cycle_list)
