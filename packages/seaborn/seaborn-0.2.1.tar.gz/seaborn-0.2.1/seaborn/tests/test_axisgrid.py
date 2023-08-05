import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import nose.tools as nt
import numpy.testing as npt

from .. import axisgrid as ag

rs = np.random.RandomState(0)


class TestFacetGrid(object):

    df = pd.DataFrame(dict(x=rs.normal(size=60),
                           y=rs.gamma(4, size=60),
                           a=np.repeat(list("abc"), 20),
                           b=np.tile(list("mn"), 30),
                           c=rs.choice(list("tuv"), 60),
                           d=np.tile(list("abcdefghij"), 6)))

    def test_selfdata(self):
        """Test that the dataframe is an attribute."""
        g = ag.FacetGrid(self.df)
        nt.assert_is(g.data, self.df)
        plt.close("all")

    def test_selffig(self):
        """Test a figure gets created and set as an attribute."""
        g = ag.FacetGrid(self.df)
        nt.assert_is_instance(g.fig, plt.Figure)
        plt.close("all")

    def test_selfaxes(self):
        """Test that there is a grid of subplot axes."""
        g = ag.FacetGrid(self.df, row="a", col="b", hue="c")
        for ax in g.axes.flat:
            nt.assert_is_instance(ax, plt.Axes)

        plt.close("all")

    def testaxes_array_size(self):
        """Test that axes grids are created with the right shape."""
        g1 = ag.FacetGrid(self.df)
        nt.assert_equal(g1.axes.shape, (1, 1))

        g2 = ag.FacetGrid(self.df, row="a")
        nt.assert_equal(g2.axes.shape, (3, 1))

        g3 = ag.FacetGrid(self.df, col="b")
        nt.assert_equal(g3.axes.shape, (1, 2))

        g4 = ag.FacetGrid(self.df, hue="c")
        nt.assert_equal(g4.axes.shape, (1, 1))

        g5 = ag.FacetGrid(self.df, row="a", col="b", hue="c")
        nt.assert_equal(g5.axes.shape, (3, 2))

        for ax in g5.axes.flat:
            nt.assert_is_instance(ax, plt.Axes)

        plt.close("all")

    def test_col_wrap(self):
        """Test that we can wrap the column facet."""
        g = ag.FacetGrid(self.df, col="d")
        nt.assert_equal(g.axes.shape, (1, 10))

        g_wrap = ag.FacetGrid(self.df, col="d", col_wrap=5)
        nt.assert_equal(g_wrap.axes.shape, (2, 5))

    def test_figure_size(self):
        """Test that the created figure size is responsive to parameters."""
        g = ag.FacetGrid(self.df, row="a", col="b")
        npt.assert_array_equal(g.fig.get_size_inches(), (6, 9))

        g = ag.FacetGrid(self.df, row="a", col="b", size=6)
        npt.assert_array_equal(g.fig.get_size_inches(), (12, 18))

        g = ag.FacetGrid(self.df, col="c", size=4, aspect=.5)
        npt.assert_array_equal(g.fig.get_size_inches(), (6, 4))

        plt.close("all")

    def testfigure_size_with_legend(self):
        """Test that adding a legend makes the figure wider when it should."""
        g1 = ag.FacetGrid(self.df, col="a", hue="c", size=4, aspect=.5)
        npt.assert_array_equal(g1.fig.get_size_inches(), (6, 4))
        g1.set_legend()
        nt.assert_greater(g1.fig.get_size_inches()[0], 6)

        g2 = ag.FacetGrid(self.df, col="a", hue="c", size=4, aspect=.5,
                          legend_out=False)
        npt.assert_array_equal(g2.fig.get_size_inches(), (6, 4))
        g2.set_legend()
        npt.assert_array_equal(g2.fig.get_size_inches(), (6, 4))

        plt.close("all")

    def testdata_generator(self):
        """Test the generator that returns data for each facet."""
        g = ag.FacetGrid(self.df, row="a")
        d = list(g.facet_data())
        nt.assert_equal(len(d), 3)

        tup, data = d[0]
        nt.assert_equal(tup, (0, 0, 0))
        nt.assert_true((data["a"] == "a").all())

        tup, data = d[1]
        nt.assert_equal(tup, (1, 0, 0))
        nt.assert_true((data["a"] == "b").all())

        g = ag.FacetGrid(self.df, row="a", col="b")
        d = list(g.facet_data())
        nt.assert_equal(len(d), 6)

        tup, data = d[0]
        nt.assert_equal(tup, (0, 0, 0))
        nt.assert_true((data["a"] == "a").all())
        nt.assert_true((data["b"] == "m").all())

        tup, data = d[1]
        nt.assert_equal(tup, (0, 1, 0))
        nt.assert_true((data["a"] == "a").all())
        nt.assert_true((data["b"] == "n").all())

        tup, data = d[2]
        nt.assert_equal(tup, (1, 0, 0))
        nt.assert_true((data["a"] == "b").all())
        nt.assert_true((data["b"] == "m").all())

        g = ag.FacetGrid(self.df, hue="c") 
        d = list(g.facet_data())
        nt.assert_equal(len(d), 3)
        tup, data = d[1]
        nt.assert_equal(tup, (0, 0, 1))
        nt.assert_true((data["c"] == "u").all())

        plt.close("all")

    def test_set(self):
        """Test the method allowing us to set attributes across facets."""
        g = ag.FacetGrid(self.df, row="a", col="b")
        xlim = (-2, 5)
        ylim = (3, 6)
        xticks = [-2, 0, 3, 5]
        yticks = [3, 4.5, 6]
        g.set(xlim=xlim, ylim=ylim, xticks=xticks, yticks=yticks)
        for ax in g.axes.flat:
            npt.assert_array_equal(ax.get_xlim(), xlim) 
            npt.assert_array_equal(ax.get_ylim(), ylim) 
            npt.assert_array_equal(ax.get_xticks(), xticks) 
            npt.assert_array_equal(ax.get_yticks(), yticks) 

        plt.close("all")

    def test_set_titles(self):
        """Test that we can provide titles for the plots."""
        g = ag.FacetGrid(self.df, row="a", col="b")
        g.map(plt.plot, "x", "y")

        # Test the default titles
        nt.assert_equal(g.axes[0, 0].get_title(), "a = a | b = m")
        nt.assert_equal(g.axes[0, 1].get_title(), "a = a | b = n")
        nt.assert_equal(g.axes[1, 0].get_title(), "a = b | b = m")

        # Test a provided title
        g.set_titles("{row_var} == {row_name} \/ {col_var} == {col_name}")
        nt.assert_equal(g.axes[0, 0].get_title(), "a == a \/ b == m")
        nt.assert_equal(g.axes[0, 1].get_title(), "a == a \/ b == n")
        nt.assert_equal(g.axes[1, 0].get_title(), "a == b \/ b == m")

        # Test a single row
        g = ag.FacetGrid(self.df,  col="b")
        g.map(plt.plot, "x", "y")

        # Test the default titles
        nt.assert_equal(g.axes[0, 0].get_title(), "b = m")
        nt.assert_equal(g.axes[0, 1].get_title(), "b = n")

        plt.close("all")

    def test_set_titles_margin_titles(self):
        """Test that we can provide titles on the plot margins."""
        g = ag.FacetGrid(self.df, row="a", col="b", margin_titles=True)
        g.map(plt.plot, "x", "y")

        # Test the default titles
        nt.assert_equal(g.axes[0, 0].get_title(), "b = m")
        nt.assert_equal(g.axes[0, 1].get_title(), "b = n")
        nt.assert_equal(g.axes[1, 0].get_title(), "")

        # Test a provided title
        g.set_titles(col_template="{col_var} == {col_name}")
        nt.assert_equal(g.axes[0, 0].get_title(), "b == m")
        nt.assert_equal(g.axes[0, 1].get_title(), "b == n")
        nt.assert_equal(g.axes[1, 0].get_title(), "")

        plt.close("all")

    @classmethod
    def teardown_class(cls):
        """Ensure that all figures are closed on exit."""
        plt.close("all")
