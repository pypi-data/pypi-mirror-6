"""
A demonstration of using an ImageDataCursor to display image array values. This
example also demonstrates using the ``display="single"`` option to display only
one data cursor instead of one-per-axes.
"""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

data = np.arange(20 * 10).reshape((20,10))
data = np.ma.masked_where(np.random.random(data.shape) > 0.8, data)

fig, axes = plt.subplots(ncols=2)
axes[0].imshow(data, interpolation='nearest', origin='lower')
axes[1].imshow(data, interpolation='nearest', origin='upper',
                     extent=[200, 300, 400, 500])
datacursor(display='single')

axes[1].margins(0.1)

fig.suptitle('Click anywhere on the image')

plt.show()
