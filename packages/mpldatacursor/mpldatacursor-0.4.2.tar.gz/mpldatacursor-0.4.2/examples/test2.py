import numpy as np
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

fig, ax = plt.subplots()
ax.plot(range(3)[::-1], 'ro-')
datacursor()
plt.show()
