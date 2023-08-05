import matplotlib.pyplot as plt
import numpy as np
from .geom import geom

class geom_errorbar(geom):
    VALID_AES = ['x', 'y', 'ymin', 'ymax', 'color', 'linestyle', 'alpha',
                 'size', 'width']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        ymin, ymax = None, None
        if 'ymin' in layer:
            ymin = layer.pop('ymin')
        else:
            ymin = np.array(y) - np.std(y)
        if 'ymax' in layer:
            ymax = layer.pop('ymax')
        else:
            ymax = np.array(y) + np.std(y)

        yerr = np.array(ymax) - np.array(ymin)
        y = (np.array(ymax) + np.array(ymin)) / 2.0

        plt.errorbar(x, y=y, yerr=yerr, fmt=None)

