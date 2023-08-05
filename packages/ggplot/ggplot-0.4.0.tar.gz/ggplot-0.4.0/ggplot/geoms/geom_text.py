import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from .geom import geom

class geom_text(geom):
    VALID_AES = ['label','x','y','alpha','angle','color','family','fontface',
                 'hjust','size','vjust']
    REQUIRED_AES = ['label','x','y']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        # Check for required aesthetics
        missing_aes = []
        for required_aes in self.REQUIRED_AES:
            if required_aes not in layer:
                missing_aes.append(required_aes)

        if len(missing_aes) > 0:
            raise Exception(
                "geom_text requires the following missing aesthetics: %s" %\
                ", ".join(missing_aes))

        x = layer.pop('x')
        y = layer.pop('y')
        label = layer.pop('label')

        # before taking max and min make sure x is not empty
        if len(x) == 0:
            return

        # plt.text does not resize axes, must do manually
        xmax = max(x)
        xmin = min(x)
        ymax = max(y)
        ymin = min(y)

        margin = 0.1
        xmargin = (xmax - xmin) * margin
        ymargin = (ymax - ymin) * margin 
        xmax = xmax + xmargin
        xmin = xmin - xmargin
        ymax = ymax + ymargin
        ymin = ymin - ymargin

        if 'hjust' in layer:
            x = (np.array(x) + int(layer['hjust'])).tolist()
            del layer['hjust']
        else:
            layer['horizontalalignment'] = 'center'

        if 'vjust' in layer:
            y = (np.array(y) + int(layer['vjust'])).tolist()
            del layer['vjust']
        else:
            layer['verticalalignment'] = 'center'

        if 'angle' in layer:
            layer['rotation'] = layer['angle']
            del layer['angle']

        for x_g,y_g,s in zip(x,y,label):
            plt.text(x_g,y_g,s,**layer)

        # resize axes
        plt.axis([xmin, xmax, ymin, ymax])
