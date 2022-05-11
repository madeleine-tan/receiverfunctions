#!/Users/madeleinetan/opt/anaconda3/bin/python

# Plots RFs by baz; includes baz plot, stack (0-25s), and extended stack (0-70s)
# Required: Obspy
# File type: SAC

import matplotlib.pyplot as plt
from matplotlib import gridspec
from obspy import read, Stream
import numpy as np
import os
import glob

# sta = ['C40A','D41A','E40A','E41A','E42A','E43A','E44A','E45A','F43A','F44A','F45A',
#   'F46A','G43A','G45A','G46A','G47A','H45A','H46A','H47A','H48A','I45A','I46A',
#   'I47A','I48A','I49A','J45A','J46A','J47A','J48A','J49A','K46A','K47A','K48A',
#   'K49A','K50A','L46A','L48A','L49A']

fig_name = 'K47A_M65'

temp_array = []
fff = []
filenames = []
st = Stream()

for f in glob.iglob("/Users/madeleinetan/Research/TA_ARRAYS/recfs/TA.K47A.*.recf.sac"):
    st += read(f)
    filenames = np.append(filenames, f)

for tr in st:
    temp_array = np.append(temp_array,tr.stats.sac.baz)
    #fff = np.append(fff, tr)

idx = np.argsort(temp_array)

st1 = Stream()

for i in filenames[idx]:
    file = i
    xx = '{}'.format(file)
    for ff in glob.iglob(xx):
        st1 += read(ff)


tmin = st1[0].stats.sac.b
npts = st1[0].stats.sac.npts
dt = st1[0].stats.sac.delta
time = np.linspace(0, npts - 1, npts) * dt + tmin

scale_factor = 30

fig = plt.figure()
grid = plt.GridSpec(4, 5, hspace=0.2, wspace=0.2)
ax0 = fig.add_subplot(grid[0:3, 0:3]) #rfs
ax1 = fig.add_subplot(grid[3, 0:3]) #baz plot
ax2 = fig.add_subplot(grid[0:3, 3]) #stack
ax3 = fig.add_subplot(grid[0:4, 4]) #extended stack

zz = 180 - (((len(idx)) / 2) * 10) #autoset offset
#zz = 170 #manually set offset
if zz < 0:
    print("WARNING: OFFSET IS NEGATIVE!")

def _fig0():
    ax0.set_ylim([25, 0])
    ax0.set_xlim([0, 380])
    ax0.set_xticks([])
    ax0.set_ylabel('time lag, s')
    ax0.minorticks_on()
    ax0.grid(which='major', axis='y', linewidth=0.5)
    fig.suptitle('TA.{}'.format(dir))
    ax0.plot(tr.data * scale_factor + offset, time, color='black', linewidth=0.8)
    ax0.fill_betweenx(time, tr.data * scale_factor + offset, offset, where=(tr.data * scale_factor + offset) > offset, color='r', alpha=0.7)
    ax0.fill_betweenx(time, tr.data * scale_factor + offset, offset, where=(tr.data * scale_factor + offset) < offset, color='b', alpha=0.7)

def _fig1():
    ax1.set_xlim(0, 380)
    ax1.set_ylim(0, 360)
    ax1.set_ylabel('back azimuth')
    ax1.set_xticks([])
    ax1.scatter(zz, baz, c='k', s=10)

def _fig2():
    ax2.set_ylim([25, 0])
    ax2.grid(visible=True, which='major', axis='y', linewidth=0.5)
    ax2.set_yticks([])
    ax2.plot(trr.data, time, color='black', linewidth=0.8)
    ax2.fill_betweenx(time, trr.data, x2=0, where=(trr.data) > 0, color='r', alpha=0.7)
    ax2.fill_betweenx(time, trr.data, x2=0, where=(trr.data) < 0, color='b', alpha=0.7)

def _fig3():
    ax3.set_ylim([70, 0])
    ax3.yaxis.tick_right()
    ax3.plot(trr.data, time, color='black', linewidth=0.8)
    ax3.fill_betweenx(time, trr.data, x2=0, where=(trr.data) > 0, color='r', alpha=0.7)
    ax3.fill_betweenx(time, trr.data, x2=0, where=(trr.data) < 0, color='b', alpha=0.7)

for j, tr in enumerate(st1):
    baz = tr.stats.sac.baz
    offset = zz

    _fig0()
    _fig1()

    zz = zz + 10

stack = st1.stack()

for k, trr in enumerate(stack):
    _fig2()
    _fig3()

print("final zz=",zz)
plt.savefig('/Users/madeleinetan/Research/TA_ARRAYS/FIGURES/M65/TA_{}.pdf'.format(fig_name))
plt.show()



