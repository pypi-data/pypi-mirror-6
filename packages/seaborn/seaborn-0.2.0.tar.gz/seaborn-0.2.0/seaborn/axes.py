import numpy as np
import matplotlib.pyplot as plt

from .utils import despine, color_palette


class FacetGrid(object):

    def __init__(self, data, row=None, col=None, hue=None, col_wrap=None,
                 sharex=True, sharey=True, size=5, aspect=1, palette="husl"):

        nrow = 1 if row is None else len(data[row].unique())
        ncol = 1 if col is None else len(data[col].unique())

        figsize = (ncol * size * aspect, nrow * size)

        fig, axes = plt.subplots(nrow, ncol, figsize=figsize,
                                 sharex=sharex, sharey=sharey)

        row_names = [] if row is None else sorted(data[row].unique())
        col_names = [] if col is None else sorted(data[col].unique())
        if row_names and col_names:
            for i, row_name in enumerate(row_names):
                for j, col_name in enumerate(col_names):
                    title = "%s = %s | %s = %s" % (row, row_name, col, col_name)
                    axes[i, j].set_title(title)
        elif row_names:
            for i, row_name in enumerate(row_names):
                title =  "%s = %s" % (row, row_name)
                axes[i].set_title(title)
        elif col_names:
            for i, col_name in enumerate(col_names):
                title =  "%s = %s" % (col, col_name)
                axes[i].set_title(title)

        hue_var = hue
        if hue is None:
            hue_masks = [np.repeat(True, len(data))]
            colors = ["#222222"]
        else:
            hue_vals = np.sort(data[hue].unique())
            hue_masks = [data[hue] == val for val in hue_vals]
            colors = color_palette(palette, len(hue_masks))

        self.data = data
        self.fig = fig
        self.axes = axes
        self.nrow = nrow
        self.row_var = row
        self.ncol = ncol
        self.col_var = col
        self.col_wrap = col_wrap
        self.hue_var = hue_var
        self.colors = colors

        despine(self.fig)


    def __enter__(self):

        return self

    def __exit__(self, exc_type, value, traceback):

        pass

    def map(self, func, x_var, y_var=None, **kwargs):

        if self.nrow == 1 or self.col_wrap is not None:
            row_masks = [np.repeat(True, len(self.data))]
        else:
            row_vals = np.sort(self.data[self.row_var].unique())
            row_masks = [self.data[self.row_var] == val for val in row_vals]

        if self.ncol == 1:
            col_masks = [np.repeat(True, len(self.data))]
        else:
            col_vals = np.sort(self.data[self.col_var].unique())
            col_masks = [self.data[self.col_var] == val for val in col_vals]

        if len(self.colors) == 1:
            hue_masks = [np.repeat(True, len(self.data))]
        else:
            hue_vals = np.sort(self.data[self.hue_var].unique())
            hue_masks = [self.data[self.hue_var] == val for val in hue_vals]

        for row_i, row_mask in enumerate(row_masks):
            for col_j, col_mask in enumerate(col_masks): 
                for hue_k, hue_mask in enumerate(hue_masks):

                    data_ijk = self.data[row_mask & col_mask & hue_mask]

                    if self.col_wrap is not None:
                        f_row = col_j // self.ncol
                        f_col = col_j % self.ncol
                    else:
                        f_row, f_col = row_i, col_j
                    kwargs["color"] = self.colors[hue_k]

                    plt.sca(self.axes[f_row, f_col])

                    if y_var is None:
                        func(data_ijk[x_var], **kwargs)
                    else:
                        func(data_ijk[x_var], data_ijk[y_var], **kwargs)
                    plt.xlabel("")
                    plt.ylabel("")

        if y_var is not None:
            for ax in self.axes[:, 0]:
                ax.set_ylabel(y_var)
        for ax in self.axes[-1, :]:
            ax.set_xlabel(x_var)

        self.fig.tight_layout()
