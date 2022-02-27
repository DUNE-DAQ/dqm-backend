from django.db import models

import plotly.express as px
import pandas as pd

# Create your models here.

class Plot(models.Model):
    name = models.CharField(max_length=30)


class Scatter(Plot):
    def plot():
        if dic is None:
            print('NONE')
            return px.scatter()
        print('Calling plot_scatter')
        ndf = pd.DataFrame(dic['data'])
        fig = px.scatter(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0],
                        labels={'x': 'Channel number', 'y': 'RMS'})

        fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'RMS',
                        'title': 'Induction plane',
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)'})

        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=1, gridcolor='black')
        return fig
        
class Heatmap(Plot):

    def plot():
        if dic is None:
            print('NONE')
            return px.scatter()
        print('Calling plot_heatmap')
        ndf = pd.DataFrame(dic['data'])
        # aspect=100 makes it a square, the default option 'equal' uses as much spacing as elements
        # has each axis (i.e. a 200x100 array is plotted as a 200x100 rectangle in arbritrary units)
        fig = px.imshow(ndf, aspect=100, origin='lower', labels={'x': 'Channel number', 'y': 'Time tick', 'color': 'ADC'})
        fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'Time ticks',
                        'title': 'Induction plane',
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)'})
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)
        return fig

class TimePlot():
    def plot():
        pass
    
    
