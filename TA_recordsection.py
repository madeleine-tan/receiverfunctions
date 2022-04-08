import matplotlib.pyplot as plt
from matplotlib import gridspec
from obspy import read, Stream
import numpy as np

#TODO: extend stack to ~70s

#sta = ['C40A','D41A','E40A']

       # 'E41A','E42A','E43A','E44A','E45A','F43A','F44A','F45A',
       #   'F46A','G43A','G45A','G46A','G47A','H45A','H46A','H47A','H48A','I45A','I46A',
       #   'I47A','I48A','I49A','J45A','J46A','J47A','J48A','J49A','K46A','K47A','K48A',
       #   'K49A','K50A','L46A','L48A','L49A']

#dirs = ([ name for name in os.listdir('.') if os.path.isdir(os.path.join('.', name)) ])

dir = 'all'

rf = read("./TA.I47A.*.recf.sac")

def read_process_data(rfpath):
    stadata = trrr.stats
    idx = np.argsort(stadata.baz)
    stadata.stla = stadata.stla[idx]
    stadata.stlo = stadata.stlo[idx]
    return stadata

for trrr in rf:
    print(trrr.stats)

n  = len(rf)
print('n=', n)

tmin = rf[0].stats.sac.b
npts = rf[0].stats.sac.npts
dt   = rf[0].stats.sac.delta
time = np.linspace(0, npts-1, npts) * dt + tmin

scale_factor = 30

fig  = plt.figure()
grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.2)
ax0  = fig.add_subplot(grid[0:3, 0:3])
ax2  = fig.add_subplot(grid[0:3, 3])
ax1  = fig.add_subplot(grid[3,0:3])

for j, tr in enumerate(rf):

    baz = tr.stats.sac.baz
    bb  = tr.stats.sac.baz
    offset = baz

    ax0.grid(which='major', axis='y', linewidth=0.5)
    ax0.plot(tr.data*scale_factor+offset, time, color='black', linewidth=0.8)
    ax0.set_ylim([25, 0])
    ax0.set_xlim([0, 380])
    ax0.set_xticks([])
    ax0.set_ylabel('time lag, s')
    ax0.minorticks_on()
    ax0.fill_betweenx(time, tr.data * scale_factor + offset, baz, where=(tr.data * scale_factor + offset) > baz, color='r')
    ax0.fill_betweenx(time, tr.data * scale_factor + offset, baz, where=(tr.data * scale_factor + offset) < baz, color='b')

    fig.suptitle('TA.{}'.format(dir))

    ax1.set_xlim(0, 380)
    ax1.set_ylim(0, 360)
    ax1.scatter(bb, bb, c='k',s=10)
    ax1.set_ylabel('back azimuth')
    ax1.set_xticks([])

stack = rf.stack()

for k, trr in enumerate(stack):
    ax2.plot(trr.data, time, color='black', linewidth=0.8)
    ax2.set_ylim([25,0])
    ax2.set_yticks([])
    ax2.fill_betweenx(time, trr.data, x2=0, where=(trr.data) > 0, color='r')
    ax2.fill_betweenx(time, trr.data, x2=0, where=(trr.data) < 0, color='b')


#plt.savefig('{}_ver2.pdf'.format(dir))
plt.show()



