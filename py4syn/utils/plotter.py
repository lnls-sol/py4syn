"""
Based on the example provided by matplotlib 1.3.1 documentation.

See also: `misc example code: multiprocess.py <http://matplotlib.org/examples/misc/multiprocess.html>`_

Adapted to work without GTK and support multiple subplots and axis overlay.
"""
import multiprocessing
from queue import Empty

from matplotlib.lines import Line2D
import pylab
import collections
import os

class ProcessPlotter(object):
    def __init__(self):
        self.axesCount = 1
        self.validAxesCount = 1
        self.axes = {}

    def __createAxis(self, params):
        NUM_COLORS = 100
        cm = pylab.get_cmap('gist_rainbow')

        idx = self.axesCount

        title = params['title']
        label = params['label']
        xlabel = params['xlabel']
        ylabel = params['ylabel']
        grid = params['grid']
        line_style = params['line_style']
        line_marker = params['line_marker']
        line_color = params['line_color']
        
        parent = params['parent']
        if(parent == None):
            n = len(self.fig.axes)
            for i in range(n):
                self.fig.axes[i].change_geometry(n+1, 1, i+1)

            ax = self.fig.add_subplot(self.validAxesCount,1, self.validAxesCount)
            ax.grid(grid)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            line = Line2D([],[])
            if label != None and label.strip() != "":
                line.set_label(label)
            line.set_linestyle(line_style)
            line.set_marker(line_marker)
            line.set_color(line_color)
            self.validAxesCount += 1
        else:
            ax = self.axes[parent]['axis']
            line = Line2D([],[])
            if label != None and label.strip() != "":
                line.set_label(label)
            line.set_linestyle(line_style)
            line.set_marker(line_marker)
            color = cm(5.*self.axesCount/NUM_COLORS)  # color will now be an RGBA tuple
            line.set_color(color)
        
        ax.add_line(line)
        
        self.axes[idx] = {}
        self.axes[idx]['axis'] = ax
        self.axes[idx]['line'] = line
        self.axes[idx]['x'] = []
        self.axes[idx]['y'] = []
        
        self.axesCount += 1
        
        self.__updateLegend()

    def __updateLegend(self):
        n = len(self.fig.axes) 
        for i in range(n):
            pylab.sca(self.fig.axes[i])
            plotterLegend = pylab.legend(loc='upper left', bbox_to_anchor=(1, 0.5), borderaxespad=1, fancybox=False, shadow=False, prop={'size':8})

    def __updateAxis(self, params):
        ax = params['axis']
        line = params['line']
        x = params['x']
        y = params['y']
        line.set_data(x, y)
        ax.relim()
        ax.autoscale_view()
    
    def __shriknAxisSpacing(self, factor_shrink_axis):
        n = len(self.fig.axes) 
        for i in range(n):
            box = self.fig.axes[i].get_position()
            self.fig.axes[i].set_position([box.x0, box.y0, box.width * factor_shrink_axis, box.height])

    def poll_draw(self):
        def call_back(arg=None):
            try:
                while 1:
                    try:
                        command = self.queue.get_nowait()
                    except Empty:
                        break   

                    cmd = command['cmd']
                    try:
                        idx = command['idx']
                    except:
                        idx = -1

                    if(cmd == "create"):
                        self.__createAxis(command)
                    elif(cmd == "clear"):
                        self.axes[idx]['x'] = []
                        self.axes[idx]['y'] = []
                        self.__updateAxis(self.axes[idx])
                         
                    elif(cmd == "plot"):
                        vx = command['x']
                        vy = command['y']
                        
                        if(isinstance(vx, collections.Iterable)):
                            self.axes[idx]['x'].extend(vx)
                        else:
                            self.axes[idx]['x'].append(vx)

                        if(isinstance(vy, collections.Iterable)):
                            self.axes[idx]['y'].extend(vy)
                        else:
                            self.axes[idx]['y'].append(vy)

                        self.__updateAxis(self.axes[idx])
                    elif(cmd == "updateLabel"):
                        params = self.axes[idx]
                        line = params['line']
                        line.set_label(command['label'])
                        self.__updateLegend()
                    elif(cmd == "updateTitle"):
                        title = command['title']
                        ax = self.axes[idx]['axis']
                        ax.set_title(title)
                    elif(cmd == "shrinkAxisSpacing"):
                        self.__shriknAxisSpacing(command['factor_shrink_axis'])
                    else:
                        pass # not implemented

                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
            except Exception as e:
                pass
            return True
        return call_back  

    def __call__(self, queue, title):
        self.title = title
        self.queue = queue
        self.fig = pylab.figure()
        self.fig.subplots_adjust(hspace=0.4)
        self.fig.canvas.set_window_title(title)
        self.manager = self.fig.canvas.manager
        self.timer = self.fig.canvas.new_timer(interval=5)
        self.timer.add_callback(self.poll_draw(), ())
        self.timer.start()

        try:
            pylab.show()
        except:
            pass

class Plotter(object):
    """
    Python class to represent an almost real-time plotter.
    This Plotter spawn another process responsible for the data plot and graph update.
    Priority should be between 0 (default) and 19 (maximum allowed).
    """
    def __init__(self, title, daemon=True, priority=0):#, **kwargs):
        """
        **Constructor**

        Parameters
        ----------
        title : `string`
            Title of the plot
        daemon : `bool`
            This parameters indicates if the spawned process should be daemon or not
            In general if daemon is set to **True** as the script ends it will close the graph, otherwise the script will end only when the graph is closed
        kwargs : dict
            Added to avoid compatibility issues.
        """
        self.plotsCount = 0
        ctx = multiprocessing.get_context('spawn')  # @UndefinedVariable
        self.plot_queue =  ctx.Queue()
        self.plotter = ProcessPlotter()
        self.plot_process = ctx.Process( target = self.plotter,args = (self.plot_queue,title) )
        self.plot_process.daemon = daemon
        self.plot_process.start()

        # Setting a lower priority to the graphic process (it should be between -20 and 19, but we only set it between 0 and 19)
        if (priority >= 0 and priority <= 19):
            os.setpriority(os.PRIO_PROCESS, self.plot_process.pid, priority)

    def isPlotterAlive(self):
        return self.plot_process.is_alive()

    def createAxis(self, title = '', label = '', xlabel = '', ylabel = '', grid=True, line_style='-', line_marker='o', line_color='red', parent=None):
        """
        Creates a subplot in the plotter, also it's possible to create an axis to a parent subplot through the **parent** parameter
        
        Parameters
        ----------        
        title : `string`
            Title of the plot
        label : `string`
            Label for the Axis Legend, if blank or None will not appear in the legend
        xlabel : `string`
            Label for the X axis
        ylabel : `string`
            Label for the Y axis            
        grid : `bool`
            If `True`, will render grid to the graph area.
        lineStyle : `string`
            The line style according to `Matplotlib Line2D style list <http://matplotlib.org/api/lines_api.html#matplotlib.lines.Line2D.set_linestyle>`_            
        lineMarker : `string`
            The line marker according to `Matplotlib Markers list <http://matplotlib.org/api/markers_api.html#module-matplotlib.markers>`_
        lineColor : `string`
            The line color, accepts any matplotlib color
        parent : `int`
            Index of the parent subplot
            
        """        
        params = {}
        params['cmd'] = "create"
        params['title'] = title
        params['label'] = label
        params['xlabel'] = xlabel
        params['ylabel'] = ylabel
        params['grid'] = grid
        params['line_style'] = line_style
        params['line_marker'] = line_marker
        params['line_color'] = line_color
        params['parent'] = parent
        if(parent != None) and (parent > self.plotsCount):
            print("Warning. Parent Axis not found. Axis not created!")
        self.plot_queue.put(params)        
        self.plotsCount += 1

    def getPlotsCount(self):
        return self.getPlotsCount()

    def plot(self, x, y, axis=1):
        """
        Plot data to graph.
        
        Parameters
        ----------
        x : `double`
            X data
        y : `double`
            Y data
        axis : `int`
            The axis index where data should be plot.
                        
        """
        params = {}
        params['cmd'] = "plot"
        params['idx'] = axis
        params['x'] = x
        params['y'] = y        
        self.plot_queue.put(params)       

    def updateLabel(self, axis=1, label=""):
        """
        Update the label in a given axis.
        
        Parameters
        ----------
        axis : `int`
            The axis index to be cleaned.
        label: `string`
            The new label.
        """
        params = {}
        params['cmd'] = "updateLabel"
        params['idx'] = axis
        params['label'] = label
        self.plot_queue.put(params)

    def updateTitle(self, axis=1, title=""):
        """
        Update the label in a given axis.
        
        Parameters
        ----------
        axis : `int`
            The axis index to be cleaned.
        title: `string`
            The new title.
        """
        params = {}
        params['cmd'] = "updateTitle"
        params['idx'] = axis
        params['title'] = title
        self.plot_queue.put(params)
    
    def shrinkAxisSpacing(self, factor_shrink_axis=1):
        params = {}
        params['cmd'] = "shrinkAxisSpacing"
        params['factor_shrink_axis'] = factor_shrink_axis
        self.plot_queue.put(params)
         
    def clear(self, axis=1):
        """
        Clear the graph.
        
        Parameters
        ----------
        axis : `int`
            The axis index to be cleaned.        
        """
        params = {}
        params['cmd'] = "clear"
        params['idx'] = axis
        self.plot_queue.put(params)        

def main2():
    import datetime
    import time
    import random
    
    n = 100

    pl = Plotter('Plot Sample e I0', daemon=True)
    
    pl1 = Plotter('Plot Norm', daemon=True)
        
    pl.createAxis(title="Energy Scan", xlabel="Energy", ylabel="I0", grid=True, line_style="--", line_marker="x", line_color="blue", label="I0")
    pl.createAxis(title="", xlabel="Energy", ylabel="Sample", grid=True, line_style=":", line_marker="o", line_color="black", label="Sample")
    pl1.createAxis(title="", xlabel="Foo", ylabel="Bar", grid=True, label="No Label")  
    pl1.createAxis(title="", xlabel="Energy", ylabel="Norm", grid=True, label="1")       
        
    prnt = 2
    idx = 2
    for i in range(0, 10):
        if(i >= 1):
            idx += 1
            #if(idx == 2):
            #    idx = 3
            pl1.createAxis(title="", parent=prnt, label=str(i+1))

        pl.clear(1)
        pl.clear(2)
        
        if(i == 9):
            pl1.createAxis(title="", parent=1, label="Foo Bar 9")
            pl1.plot(random.random()*1000, random.random()*1000, axis=12)
        
        s = datetime.datetime.now()        
        for ii in range(n):
            i0 = random.random()*100
            sample = random.random()*127
            norm = (sample/i0)/10
            pl.plot(ii, i0, axis=1)
            pl.plot(ii, sample, axis=2)
            pl1.plot(ii, norm, axis=idx)
            time.sleep(0.01)
        e = datetime.datetime.now()              
        print("Total Time: ",e-s)
        print("Time per Point: ", (e-s)/n)
    
    print("Press any key to continue...")
    input()

def main():
    import datetime
    import time
    import random
    
    n = 100

    pl = Plotter('Plot Sample e I0', daemon=True)
    
    pl.createAxis(title="Title 1", label="Label 1", xlabel="X", ylabel="Y")
    pl.createAxis(title="Title 2", label="Label 2", xlabel="X", ylabel="Y", parent = 1)
    pl.createAxis(title="Title 3", label="Label 3", xlabel="X", ylabel="Y")
        
    print("Press any key to continue...")
    input()    
    
if __name__ == '__main__':
    main() 
