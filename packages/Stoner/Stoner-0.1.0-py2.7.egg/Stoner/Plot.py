"""         Stoner.Plot 
            ============

Provides the a class to facilitate easier plotting of Stoner Data:

Classes:
    PlotFile - A class that uses matplotlib to plot data
"""
from .Core import DataFile
import numpy
import matplotlib
import os
import platform
if os.name=="posix" and platform.system()=="Darwin":
    matplotlib.use('MacOSX')
from matplotlib import pyplot as pyplot
from scipy.interpolate import griddata
from copy import copy
import re

class PlotFile(DataFile):
    """Extends DataFile with plotting functions

    Args:
        args(tuple): Arguements to pass to :py:meth:`Stoner.Core.DataFile.__init__`
        kargs (dict):  keyword arguments to pass to \b DataFile.__init__

    Methods:
        plot_xy: Basic 2D plotting function
        plot_xyz: 3D plotting function
        griddata: Method to transform xyz data to a matrix
        contour_xyz: Plots x,y,z points as a contour plot
        plot_matrix: Plots a matrix as a 2D colour image plot
        draw: Pass throuygh to matplotlib draw
        show: Pass through to matploitlib show
        figure: Pass through to maplotlib figure.
        
    Attributes:
        fig (matplotlib.figure): The current figure object being worked with
    
    """

    __figure=None

    def __init__(self, *args, **kargs): #Do the import of pyplot here to speed module load
        """Constructor of \b PlotFile class. Imports pyplot and then calls the parent constructor

        """
        global pyplot
        super(PlotFile, self).__init__(*args, **kargs)

    def __dir__(self):
        """Handles the local attributes as well as the inherited ones"""
        attr=self.__dict__.keys()
        attr2=[a for a in super(PlotFile, self).__dir__() if a not in attr]
        attr.extend(attr2)
        attr.extend(["fig", "axes"])
        attr.extend(('xlabel','ylabel','title','subtitle','xlim','ylim'))
        return attr

    def __getattr__(self, name):
        """Attribute accessor

        Args:
            name (string):  Name of attribute the following attributes are supported:
                * fig - the current pyplot figure reference
                * axes - the pyplot axes object for the current plot
                * xlim - the X axis limits
                * ylim - the Y axis limits

                All other attrbiutes are passed over to the parent class
                """
        if name=="fig":
            return self.__figure
        elif name=="axes":
            if isinstance(self.__figure, matplotlib.figure.Figure):
                return self.__figure.axes
            else:
                return None
        elif name in ('xlim','ylim'):
            return pyplot.__dict__[name]()
        else:
            return super(PlotFile, self).__getattr__(name)

    def __setattr__(self, name, value):
        """Sets the specified attribute

        Args:
            name (string): The name of the attribute to set. The cuirrent attributes are supported:
                * fig - set the pyplot figure isntance to use
                * xlabel - set the X axis label text
                * ylabel - set the Y axis label text
                * title - set the plot title
                * subtitle - set the plot subtitle
                * xlim - set the x-axis limits
                * ylim - set the y-axis limits
            
            Only "fig" is supported in this class - everything else drops through to the parent class
            value (any): The value of the attribute to set.
    """
        if name=="fig":
            self.__figure=value
            pyplot.figure(value.number)
        elif name in ('xlabel','ylabel','title','subtitle','xlim','ylim'):
            if isinstance(value,tuple):
                pyplot.__dict__[name](*value)
            elif isinstance(value,dict):
                pyplot.__dict__[name](**value)
            else:
                pyplot.__dict__[name](value)
        else:
            super(PlotFile, self).__setattr__(name, value)

    def _plot(self,ix,iy,fmt,plotter,figure,**kwords):
        """Private method for plotting a single plot to a figure.
        
        Args:
            ix (int): COlumn index of x data
            iy (int): Column index of y data
            fmt (str): Format of this plot
            plotter (callable): Routine used to plot this data
            figure (matplotlib.figure): Figure to plot data
            **kwords (dict): Other keyword arguments to pass through

        """
        if "label" not in kwords:
            kwords["label"]=self.column_headers[iy]
        x=self.column(ix)
        y=self.column(iy)
        if plotter in (pyplot.plot,pyplot.semilogx,pyplot.semilogy,pyplot.loglog): #plots with positional fmt
            if fmt is None:
                plotter(x,y, figure=figure, **kwords)
            else:
                plotter(x,y, fmt, figure=figure, **kwords)
        else:
            if fmt is None:
                fmt="-"
            plotter(x,y, fmt=fmt,figure=figure, **kwords)



    def plot_xy(self,column_x, column_y, fmt=None,show_plot=True,  title='', save_filename='', figure=None, plotter=None,  **kwords):
        """Makes a simple X-Y plot of the specified data.

            Args:
                column_x (index): Which column has the X-Data
                column_y (index): Which column(s) has(have) the y-data to plot
            
            Keyword Arguments:            
                fmt (strong or sequence of strings): Specifies the format for the plot - see matplotlib documentation for details
                show_plot (bool): True Turns on interactive plot control
                title (string): Optional parameter that specfies the plot title - otherwise the current DataFile filename is used
                save_filename (string): Filename used to save the plot
                figure (matplotlib figure): Controls what matplotlib figure to use. Can be an integer, or a matplotlib.figure or False. If False then a new figure is always used, otherwise it will default to using the last figure used by this DataFile object.
                plotter (callable): Optional arguement that passes a plotting function into the routine. Sensible choices might be pyplot.plot (default), py.semilogy, pyplot.semilogx
                kwords (dict): A dictionary of other keyword arguments to pass into the plot function.
    
            Returns:
                A matplotlib.figure isntance

        """
        column_x=self.find_col(column_x)
        column_y=self.find_col(column_y)
        if "xerr" in kwords or "yerr" in kwords and plotter is None: # USe and errorbar blotter by default for errors
            plotter=pyplot.errorbar
        for err in ["xerr", "yerr"]:  # Check for x and y error keywords
            if err in kwords:
                if isinstance(kwords[err],(int,str,unicode,re._pattern_type)):
                    kwords[err]=self.column(kwords[err])
                elif isinstance(kwords[err], list) and isinstance(column_y,list) and len(kwords[err])==len(column_y):
                # Ok, so it's a list, so redo the check for each  item.
                    for i in range(len(kwords[err])):
                        if isinstance(kwords[err],(int,str,unicode,re._pattern_type)):
                            kwords[err][i]=self.column(kwords[err])
        
        # Now try to process the figure parameter
        if isinstance(figure, int):
            figure=pyplot.figure(figure)
        elif isinstance(figure, bool) and not figure:
            figure=pyplot.figure()
        elif isinstance(figure, matplotlib.figure.Figure):
            figure=pyplot.figure(figure.number)
        elif isinstance(self.__figure,  matplotlib.figure.Figure):
            figure=self.__figure
        else:
            figure=pyplot.figure()
        
        pyplot.figure(figure.number)
        
        if show_plot == True:
            pyplot.ion()
        if plotter is None: #Nothing has defined the plotter to use yet
            plotter=pyplot.plot  
        if not isinstance(column_y, list):
            ylabel=self.column_headers[column_y]
            column_y=[column_y]
        else:
            ylabel=",".join([self.column_headers[ix] for ix in column_y])
        temp_kwords=kwords
        for ix in range(len(column_y)):
            if isinstance(fmt,list): # Fix up the format
                fmt_t=fmt[ix]
            else:
                fmt_t=fmt
            if "label" in kwords and isinstance(kwords["label"],list): # Fix label keywords
                temp_kwords["label"]=kwords["label"][ix]
            # Call plot
            self._plot(column_x,column_y[ix],fmt_t,plotter,figure,**temp_kwords)


        pyplot.xlabel(str(self.column_headers[column_x]))
        pyplot.ylabel(str(ylabel))
        if title=='':
            title=self.filename
        pyplot.title(title)
        pyplot.grid(True)
        if save_filename != '':
            pyplot.savefig(str(save_filename))
        pyplot.draw()
        self.__figure=figure
        return self.__figure

    def plot_xyz(self, xcol, ycol, zcol, shape=None, xlim=None, ylim=None,cmap=pyplot.cm.jet,show_plot=True,  title='', figure=None, plotter=None,  **kwords):
        """Plots a surface plot based on rows of X,Y,Z data using matplotlib.pcolor()
        
            Args:
                xcol (index): Xcolumn index or label
                ycol (index): Y column index or label
                zcol (index): Z column index or label
            
            Keyword Arguments:            
                shape (tuple): Defines the shape of the surface (i.e. the number of X and Y value. If not procided or None, then the routine will attempt to calculate these from the data provided
                xlim (tuple): Defines the x-axis limits and grid of the data to be plotted
                ylim (tuple) Defines the Y-axis limits and grid of the data data to be plotted
                cmap (matplotlib colour map): Surface colour map - defaults to the jet colour map
                show_plot (bool): True Turns on interactive plot control
                title (string): Optional parameter that specfies the plot title - otherwise the current DataFile filename is used
                save_filename (string): Filename used to save the plot
                figure (matplotlib figure): Controls what matplotlib figure to use. Can be an integer, or a matplotlib.figure or False. If False then a new figure is always used, otherwise it will default to using the last figure used by this DataFile object.
                plotter (callable): Optional arguement that passes a plotting function into the routine. Sensible choices might be pyplot.plot (default), py.semilogy, pyplot.semilogx
                kwords (dict): A dictionary of other keyword arguments to pass into the plot function.

            Returns:
                A matplotlib.figure isntance
        """
        xdata,ydata,zdata=self.griddata(xcol,ycol,zcol,shape=shape,xlim=xlim,ylim=ylim)
        if isinstance(figure, int):
            figure=pyplot.figure(figure)
        elif isinstance(figure, bool) and not figure:
            figure=pyplot.figure()
        elif isinstance(figure, matplotlib.figure.Figure):
            figure=pyplot.figure(figure.number)
        elif isinstance(self.__figure,  matplotlib.figure.Figure):
            figure=self.__figure
        else:
            figure=pyplot.figure()
        self.__figure=figure
        if show_plot == True:
            pyplot.ion()
        if plotter is None:
            plotter=self.__SurfPlotter
        plotter(xdata, ydata, zdata, cmap=cmap, **kwords)
        pyplot.xlabel(str(self.column_headers[self.find_col(xcol)]))
        pyplot.ylabel(str(self.column_headers[self.find_col(ycol)]))
        if plotter==self.__SurfPlotter:
            self.axes[0].set_zlabel(str(self.column_headers[self.find_col(zcol)]))
        if title=='':
            title=self.filename
        pyplot.title(title)
        pyplot.draw()

        return self.__figure

    def griddata(self,xc,yc=None,zc=None,shape=None,xlim=None,ylim=None,method="linear"):
        """Function to convert xyz data onto a regular grid

            Args:
                xc (index): Column to be used for the X-Data
                yc (index): column to be used for Y-Data - default value is column to the right of the x-data column
                zc (index): column to be used for the Z-data - default value is the column to the right of the y-data column
            
            Keyword Arguments:        
                shaoe (two-tuple): Number of points along x and y in the grid - defaults to a square of sidelength = square root of the length of the data.
                xlim (tuple): The xlimits
                ylim (tuple) The ylimits
                method (string): Type of interploation to use, default is linear
            
            ReturnsL
                X,Y,Z three two dimensional arrays of the co-ordinates of the interpolated data
        """

        xc=self.find_col(xc)
        if yc is None:
            yc=xc+1
        else:
            yc=self.find_col(yc)
        if zc is None:
            zc=yc+1
        else:
            zc=self.find_col(zc)
        if shape is None or not(isinstance(shape,tuple) and len(shape)==2):
            shape=(numpy.floor(numpy.sqrt(len(self))),numpy.floor(numpy.sqrt(len(self))))
        if xlim is None:
            xlim=(numpy.min(self.column(xc)),numpy.max(self.column(xc)))
        if isinstance(xlim,tuple) and len(xlim)==2:
            xlim=(xlim[0],xlim[1],(xlim[1]-xlim[0])/shape[0])
        elif isinstance(xlim,tuple) and len(xlim)==3:
            xlim[2]=len(range(*xlim))
        else:
            raise RuntimeError("X limit specification not good.")
        if ylim is None:
            ylim=(numpy.min(self.column(yc)),numpy.max(self.column(yc)))
        if isinstance(ylim,tuple) and len(ylim)==2:
            ylim=(ylim[0],ylim[1],(ylim[1]-ylim[0])/shape[1])
        elif isinstance(ylim,tuple) and len(ylim)==3:
            ylim[2]=len(range(*ylim))
        else:
            raise RuntimeError("Y limit specification not good.")

        np=numpy.mgrid[slice(*xlim),slice(*ylim)].T

        points=numpy.array([self.column(xc),self.column(yc)]).T
        Z=griddata(points,self.column(zc),np,method=method)

        return np[:,:,0],np[:,:,1],Z

    def contour_xyz(self,xc,yc,zc,shape=None,xlim=None, ylim=None, plotter=None,**kargs):
        """Grid up the three columns of data and plot

        Args:
            xc (index): Column to be used for the X-Data
            yc (index): column to be used for Y-Data - default value is column to the right of the x-data column
            zc (index): column to be used for the Z-data - default value is the column to the right of the y-data column
        
        Keyword Arguments:        
            shaoe (two-tuple): Number of points along x and y in the grid - defaults to a square of sidelength = square root of the length of the data.
            xlim (tuple): The xlimits
            ylim (tuple) The ylimits

        Returns:
            A matplotlib figure
         """

        X,Y,Z=self.griddata(xc,yc,zc,shape,xlim,ylim)
        if plotter is None:
            plotter=pyplot.contour

        fig=plotter(X,Y,Z,**kargs)
        pyplot.xlabel(self.column_headers[self.find_col(xc)])
        pyplot.ylabel(self.column_headers[self.find_col(yc)])
        pyplot.title(self.filename + " "+ self.column_headers[zc])

        return fig




    def plot_matrix(self, xvals=None, yvals=None, rectang=None, cmap=pyplot.cm.jet,show_plot=True,  title='',xlabel=None, ylabel=None, zlabel=None,  figure=None, plotter=None,  **kwords):
        """Plots a surface plot by assuming that the current dataset represents a regular matrix of points.

            Args:
                xvals (index, list or numpy.array): Either a column index or name or a list or numpytarray of column values. The default (None) uses the first column of data
                yvals (int or list): Either a row index or a list or numpy array of row values. The default (None) uses the column_headings interpreted as floats
                rectang (tuple):  a tuple of either 2 or 4 elements representing either the origin (row,column) or size (origin, number of rows, number of columns) of data to be used for the z0data matrix
            
            Keyword Arguments:
                cmap (matplotlib colour map): Surface colour map - defaults to the jet colour map
                show_plot (bool): True Turns on interactive plot control
                title (string): Optional parameter that specfies the plot title - otherwise the current DataFile filename is used
                xlabel (string) X axes label. Deafult is None - guess from xvals or metadata
                ylabel (string): Y axes label, Default is None - guess from metadata
                zlabel (string): Z axis label, Default is None - guess from metadata
                figure (matplotlib figure): Controls what matplotlib figure to use. Can be an integer, or a matplotlib.figure or False. If False then a new figure is always used, otherwise it will default to using the last figure used by this DataFile object.
                plotter (callable): Optional arguement that passes a plotting function into the routine. Sensible choices might be pyplot.plot (default), py.semilogy, pyplot.semilogx
                kwords (dict): A dictionary of other keyword arguments to pass into the plot function.
            
            Returns:
                The matplotib figure with the data plotted"""
        # Sortout yvals values
        if isinstance(yvals, int): #  Int means we're sepcifying a data row
            if rectang is None: # we need to intitialise the rectang
                rectang=(yvals+1, 0) # We'll sort the column origin later
            elif isinstance(rectang, tuple) and rectang[1]<=yvals: # We have a rectang, but we need to adjust the row origin
                rectang[0]=yvals+1
            yvals=self[yvals] # change the yvals into a numpy array
        elif isinstance(yvals, list) or isinstance(yvals, tuple): # We're given the yvals as a list already
            yvals=numpy.array(yvals)
        elif yvals is None: # No yvals, so we'l try column headings
            if isinstance(xvals, int) or isinstance(xvals, str): # Do we have an xcolumn header to take away ?
                xvals=self.find_col(xvals)
                headers=self.column_headers[xvals+1:]
            elif xvals is None: # No xvals so we're going to be using the first column
                xvals=0
                headers=self.column_headers[1:]
            else:
                headers=self.column_headers
            yvals=numpy.array([float(x) for x in headers]) #Ok try to construct yvals aray
        else:
            raise RuntimeError("uvals must be either an integer, list, tuple, numpy array or None")
        #Sort out xvls values
        if isinstance(xvals, int) or isinstance(xvals, str): # String or int means using a column index
            if xlabel is None:
                xlabel=self.column_headers[self.find_col(xvals)]
            if rectang is None: # Do we need to init the rectan ?
                rectang=(0, xvals+1)
            elif isinstance(rectang, tuple): # Do we need to adjust the rectan column origin ?
                rectang[1]=xvals+1
            xvals=self.column(xvals)
        elif isinstance(xvals, list) or isinstance(xvals, tuple): # Xvals as a data item
            xvals=numpy.array(xvals)
        elif isinstance(xvals, numpy.ndarray):
            pass
        elif xvals is None: # xvals from column 0
            xvals=self.column(0)
            if rectang is None: # and fix up rectang
                rectang=(0, 1)
        else:
            raise RuntimeError("xvals must be a string, integer, list, tuple or numpy array or None")

        if isinstance(rectang, tuple) and len(rectang)==2: # Sort the rectang value
            rectang=(rectang[0], rectang[1], numpy.shape(self.data)[0]-rectang[0], numpy.shape(self.data)[1]-rectang[1])
        elif rectang is None:
            rectang=(0, 0, numpy.shape(self.data)[0], numpy.shape(self.data)[1])
        elif isinstance(rectang, tuple) and len(rectang)==4: # Ok, just make sure we have enough data points left.
            rectang=(rectang[0], rectang[1], min(rectang[2], numpy.shape(self.data)[0]-rectang[0]), min(rectang[3], numpy.shape(self.data)[1]-rectang[1]))
        else:
            raise RuntimeError("rectang should either be a 2 or 4 tuple or None")

        #Now we can create X,Y and Z 2D arrays
        print rectang
        zdata=self.data[rectang[0]:rectang[0]+rectang[2], rectang[1]:rectang[1]+rectang[3]]
        xvals=xvals[0:rectang[2]]
        yvals=yvals[0:rectang[3]]
        xdata, ydata=numpy.meshgrid(xvals, yvals)

        #This is the same as for the plot_xyz routine'
        if isinstance(figure, int):
            figure=pyplot.figure(figure)
        elif isinstance(figure, bool) and not figure:
            figure=pyplot.figure()
        elif isinstance(figure, matplotlib.figure.Figure):
            figure=pyplot.figure(figure.number)
        elif isinstance(self.__figure,  matplotlib.figure.Figure):
            figure=self.__figure
        else:
            figure=pyplot.figure()
        self.__figure=figure
        if show_plot == True:
            pyplot.ion()
        if plotter is None:
            plotter=self.__SurfPlotter
        plotter(xdata, ydata, zdata, cmap=cmap, **kwords)
        labels={"xlabel":(xlabel, "X Data"), "ylabel":(ylabel, "Y Data"), "zlabel":(zlabel, "Z Data")}
        for label in labels:
            (v, default)=labels[label]
            if v is None:
                if label in self.metadata:
                    labels[label]=self[label]
                else:
                    labels[label]=default
            else:
                labels[label]=v

        pyplot.xlabel(str(labels["xlabel"]))
        pyplot.ylabel(str(labels["ylabel"]))
        if plotter==self.__SurfPlotter:
            self.axes[0].set_zlabel(str(labels["zlabel"]))
        if title=='':
            title=self.filename
        pyplot.title(title)
        pyplot.draw()

        return self.__figure


    def __SurfPlotter(self, X, Y, Z, **kargs):
        """Utility private function to plot a 3D color mapped surface
        
        Args:
            X data
            Y Y data
            Z data
            kargs (dict): Other keywords to pass through

        ReturnsL
            A matplotib Figure

        This function attempts to work the same as the 2D surface plotter pcolor, but draws a 3D axes set"""
        ax = self.fig.gca(projection='3d')
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, **kargs)
        self.fig.colorbar(surf, shrink=0.5, aspect=5)
        return surf

    def draw(self):
        """Pass through to pyplot to force figure redraw"""
        pyplot.figure(self.__figure.number)
        pyplot.draw()

    def show(self):
        """Pass through for pyplot Figure.show()"""
        self.fig.show()

    def figure(self, figure):
        """Set the figure used by :py:class:`Stoner.Plot.PlotFile`
        
        Args:
            figure A matplotlib figure or figure number
            
        Returns:
            The current \b Stoner.PlotFile instance"""
        if isinstance(figure, int):
            figure=pyplot.figure(figure)
        elif isinstance(figure, matplotlib.figure.Figure):
            pyplot.figure(figure.number)
        self.__figure=figure
        return self


