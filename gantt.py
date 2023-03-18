"""
Gantt.py is a simple class to render Gantt charts, as commonly used in
"""

import json
from operator import sub

import numpy as np
import matplotlib.pyplot as plt
import random
import matplotlib.patches as mpatches

class Package():
    """Encapsulation of a work package

    A work package is instantiated from a dictionary. It **has to have**
    a label, astart and an end. Optionally it may contain milestones
    and a color

    :arg str pkg: dictionary w/ package data name
    """
    def __init__(self, pkg):

        self.start = pkg['start']
        self.end = pkg['end']
        self.machine = pkg['machine']
        self.job = pkg['job']

        if self.start < 0 or self.end < 0:
            raise ValueError("Package cannot begin at t < 0")
        if self.start > self.end:
            raise ValueError("Cannot end before started")

class Gantt():
    """Gantt
    Class to render a simple Gantt chart, with optional milestones
    """
    def __init__(self, dataFile):
        """ Instantiation

        Create a new Gantt using the data in the file provided
        or the sample data that came along with the script

        :arg str dataFile: file holding Gantt data
        """
        self.dataFile = dataFile

        # some lists needed
        self.packages = []
        self.labels = []

        self._loadData()
        self._procData()

    def _loadData(self):
        """ Load data from a JSON file that has to have the keys:
            packages & title. Packages is an array of objects with
            a label, start and end property and optional milesstones
            and color specs.
        """

        # load data
        with open(self.dataFile) as fh:
            data = json.load(fh)

        for pkg in data['packages']:
            self.packages.append(Package(pkg))

        self.machine = [pkg['machine'] for pkg in data['packages']]
        self.job = [pkg['job'] for pkg in data['packages']]
        try:
            self.title = data['title']
        except KeyError:
            self.title = 'Gantt for JSP'
        try:
            self.xticks = data['xticks']
        except KeyError:
            self.xticks = ""
        try:
            self.machines = data['machines']
        except KeyError:
            self.machines = 100
        for i in range(0,self.machines):
            self.labels.append("machine-"+str(i+1))
        try:
            self.jobs = data['jobs']
        except KeyError:
            self.jobs = 100

    def _procData(self):
        """ Process data to have all values needed for plotting
        """
        # parameters for bars
        self.nPackages = len(self.packages)
        self.start = [None] * self.nPackages
        self.end = [None] * self.nPackages

        maxx = -1
        for i in range(0,len(self.packages)):
            pkg = self.packages[i]
            idx = i
            self.start[idx] = pkg.start
            self.end[idx] = pkg.end
            maxx = max(maxx, self.end[idx])
        if maxx%2==1:
            maxx += 1
        self.xlabel = np.arange(0,2,maxx)

        self.durations = map(sub, self.end, self.start)
        self.yPos = np.arange(self.machines, 0, -1)

    def format(self):
        """ Format various aspect of the plot, such as labels,ticks, BBox
        :todo: Refactor to use a settings object
        """
        # format axis
        plt.tick_params(
            axis='both',    # format x and y
            which='both',   # major and minor ticks affected
            bottom='on',    # bottom edge ticks are on
            top='off',      # top, left and right edge ticks are off
            left='off',
            right='off')

        # tighten axis but give a little room from bar height
        plt.xlim(0, max(self.end))
        plt.ylim(0.5, self.machines + .5)

        # add title and package names
        plt.yticks(self.yPos, self.labels)
        plt.title(self.title)

        if self.xlabel:
            plt.xlabel(self.xlabel)

        if self.xticks:
            plt.xticks(self.xticks, map(str, self.xticks))

    def randomColor(self):
        colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        while True:
            color = ""
            for i in range(6):
                color += colorArr[random.randint(0,14)]
            colorint = int(color, 16)
            if colorint > 8388607.5:
                break
        return "#"+color

    def render(self):
        """ Prepare data for plotting
        """

        # init figure
        self.fig, self.ax = plt.subplots()
        self.ax.yaxis.grid(False)
        self.ax.xaxis.grid(True)

        # assemble colors
        jobcolors = []

        for i in range(0, self.jobs):
            jobcolors.append(self.randomColor())

        colors = []
        for i in range(0, self.nPackages):
            colors.append(jobcolors[self.packages[i].job-1])

        for i in range(0, self.nPackages):
            rect=mpatches.Rectangle((self.start[i],self.machines-self.machine[i]+1-0.25),self.end[i]-self.start[i],0.5,facecolor=colors[i])
            plt.gca().add_patch(rect)

        plt.rc('font',family='serif', size=15)
        for i in range(0, len(self.start)):
            plt.text((self.end[i]+self.start[i])/2, self.machines-self.machine[i]+0.95, str(self.job[i]))

        # format plot
        self.format()

    @staticmethod
    def show():
        """ Show the plot
        """
        plt.show()

    @staticmethod
    def save(saveFile='img/GANTT.png'):
        """ Save the plot to a file. It defaults to `img/GANTT.png`.

        :arg str saveFile: file to save to
        """
        plt.savefig(saveFile, bbox_inches='tight')


if __name__ == '__main__':
    g = Gantt('sample.json')
    g.render()
    g.show()
    # g.save('img/GANTT.png')
