import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

data = np.arange(100).reshape((10,10))

fig, axes = plt.subplots(ncols=2)
axes[0].pcolor(data)
axes[1].pcolormesh(data)
datacursor(display='single')

fig.suptitle('Click anywhere on the image')

plt.show()
