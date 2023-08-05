import matplotlib.pyplot as plt
from copy import deepcopy
from .geom import geom

class geom_errorbar(geom):
    VALID_AES = ['x', 'ymin', 'ymax', 'color', 'linestyle', 'alpha', 'size',
                 'width']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        ymin, ymax = None, None
        if 'ymin' in layer:
            ymin = layer.pop('ymin')
        else:
            ymin = 0
        if 'ymax' in layer:
            ymax = layer.pop('ymax')
        else:
            ymax = 0

        plt.errorbar(x=x, ymin=ymin, ymax=ymax, **layer)

