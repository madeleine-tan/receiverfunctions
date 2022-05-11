#!/Users/madeleinetan/opt/anaconda3/bin/python

import matplotlib.pyplot as plt
from matplotlib import gridspec
from obspy import read, Stream
import numpy as np
import os
import glob
import time
import math
import numpy as np
import matplotlib as mpl
mpl.use('macosx')

station = 'K47A'

# Rounds up or down
def roundup(x, n=10):
    res = math.ceil(x/n)*n
    if (x%n < n/2)and (x%n>0):
        res-=n
    return res

# Display commands on figure
def tellme(s):
    print(s)
    plt.title(s,fontsize=16)
    plt.draw()

def _fig0():
    ax0.set_ylim([25, 0])
    ax0.set_xlim([0, 380])
    ax0.set_xticks([])
    ax0.set_ylabel('time lag, s')
    ax0.minorticks_on()
    ax0.grid(which='major', axis='y', linewidth=0.5)
    fig.suptitle('TA.{}'.format(station))
    ax0.plot(tr.data * scale_factor + offset, time, color='black', linewidth=0.8)
    ax0.fill_betweenx(time, tr.data * scale_factor + offset, offset, where=(tr.data * scale_factor + offset) > offset, color='r', alpha=0.7)
    ax0.fill_betweenx(time, tr.data * scale_factor + offset, offset, where=(tr.data * scale_factor + offset) < offset, color='b', alpha=0.7)

# Begin reading in files and sorting by baz
temp_array = []
fff = []
filenames = []
st = Stream()

for f in glob.iglob("/Users/madeleinetan/Research/TA_ARRAYS/recfs/TA.K47A.*.recf.sac"):
    st += read(f)
    filenames = np.append(filenames, f)

for tr in st:
    temp_array = np.append(temp_array,tr.stats.sac.baz)

idx = np.argsort(temp_array)

st1 = Stream()

for i in filenames[idx]:
    file = i
    xx = '{}'.format(file)
    for ff in glob.iglob(xx):
        st1 += read(ff)

# Figure plotting parameters
tmin = st1[0].stats.sac.b
npts = st1[0].stats.sac.npts
dt = st1[0].stats.sac.delta
time = np.linspace(0, npts - 1, npts) * dt + tmin
scale_factor = 30

fig = plt.figure()
grid = plt.GridSpec(3, 3)
ax0 = fig.add_subplot(grid[0:3, 0:3])  # rfs
zz = 180 - (((len(idx)) / 2) * 10)  # autoset offset
    # zz = 170 #manually set offset
if zz < 0:
    print("WARNING: OFFSET IS NEGATIVE!")

tellme('Plotting receiver functions...')

offsets = []
yys = np.arange(0,25,1)

# Plot traces; if offset == baz in bad event file, trace is skipped
for j, tr in enumerate(st1):
    baz = tr.stats.sac.baz
    offset = zz
    offsets = str(zz)
    with open('{}.txt'.format(station)) as file:
        if offsets in file.read():
            print("1 bad trace skipped")
            pass
        else:
            _fig0()
    zz = zz + 10

# Select bad events
done = False
while not done:
    pts = []
    while len(pts) < 3:
        tellme('Select 3 bad traces')
        pts = np.asarray(plt.ginput(3,timeout=-1))
        if len(pts) < 3:
            tellme('Restarting QC...')

    pts = np.around(np.array(pts))
    ph = plt.scatter(pts[:,0],pts[:,1],c='g',marker='.')

    tellme('Ready to save? Key input for yes, mouse click for no')

    done = plt.waitforbuttonpress()

    ptss = []
    ptsss = []
    ptss = np.append(ptss,pts[:,0])

# Save bad events
    if done:
        tellme('Initiating saving...')
        ptsss = [roundup(n) for n in ptss]
        a_file = open('{}.txt'.format(station), "a")
        np.savetxt(a_file, ptsss, fmt='%.3f', newline=os.linesep)
        a_file.close()
        print(ptsss)
