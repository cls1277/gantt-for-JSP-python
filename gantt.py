import json
from operator import sub
import numpy as np
import matplotlib.pyplot as plt
import random
import matplotlib.patches as mpatches

def load_data(data_file):
    with open(data_file) as fh:
        data = json.load(fh)

    packages = []
    machine = [pkg['machine'] for pkg in data['packages']]
    job = [pkg['job'] for pkg in data['packages']]
    title = data.get('title', 'Gantt for JSP')
    xticks = data.get('xticks', "")
    machines = data.get('machines', 100)
    labels = [f"machine-{i}" for i in range(machines)]
    jobs = data.get('jobs', 100)
    operations = [0] * jobs

    for pkg in data['packages']:
        packages.append({
            'start': pkg['start'],
            'end': pkg['end'],
            'machine': pkg['machine'],
            'job': pkg['job'],
            'operation': operations[pkg['job']]
        })
        operations[pkg['job']] += 1

    return packages, machine, job, title, xticks, labels, machines, jobs

def process_data(packages):
    start = [pkg['start'] for pkg in packages]
    end = [pkg['end'] for pkg in packages]
    durations = list(map(sub, end, start))
    ypos = np.arange(machines, 0, -1)

    return start, end, durations, ypos

def random_color():
    red = random.randint(150, 255)
    green = random.randint(150, 255)
    blue = random.randint(150, 255)
    return "#{:02X}{:02X}{:02X}".format(red, green, blue)

def render_gantt(packages, machines, start, end, ypos, jobs, xticks, labels):
    def on_hover(event):
        for i, rect in enumerate(rectangles):
            if rect.contains(event)[0]:
                rect.set_edgecolor('black')
                rect.set_linewidth(2)
                txt = 'job:' + str(packages[i]['job']) + '\noperation:' + str(packages[i]['operation']) + '\ntime:[' + str(packages[i]['start']) + ',' + str(packages[i]['end']) + ']'
                text.set_text(txt)
                for j, rect1 in enumerate(rectangles):
                    if i == j or packages[i]['job'] != packages[j]['job']:
                        continue
                    rect1.set_edgecolor('red')
                    rect1.set_linewidth(2)
            else:
                rect.set_edgecolor('none')
                rect.set_linewidth(1)
        plt.draw()

    fig, ax = plt.subplots()
    ax.yaxis.grid(False)
    ax.xaxis.grid(True)

    rectangles = []
    text = ax.text(0.5, 1.05, '', transform=ax.transAxes, ha='center', va='center', color='black', fontsize=12)

    job_colors = [random_color() for _ in range(jobs)]
    colors = [job_colors[pkg['job']-1] for pkg in packages]

    for i, pkg in enumerate(packages):
        rect = mpatches.Rectangle((start[i], machines - pkg['machine'] - 0.25),
                                  end[i] - start[i], 0.5, facecolor=colors[i])
        rectangles.append(rect)
        plt.gca().add_patch(rect)

    plt.rc('font', family='serif', size=15)
    # for i in range(len(start)):
    #     plt.text((end[i] + start[i]) / 2, machines - packages[i]['machine'] - 0.05, str(job[i]))
    for i, rect in enumerate(rectangles):
        x_center = rect.get_x() + rect.get_width() / 2
        y_center = rect.get_y() + rect.get_height() / 2
        plt.text(x_center, y_center, str(job[i]), ha='center', va='center')

    plt.tick_params(axis='both', which='both', bottom='on', top='off', left='off', right='off')
    plt.xlim(0, max(end))
    plt.ylim(0.5, machines + 0.5)
    plt.yticks(ypos, labels)
    fig.canvas.mpl_connect('motion_notify_event', on_hover)

    if xticks:
        plt.xticks(xticks, map(str, xticks))

def show_plot():
    plt.show()

# def save_plot(title, save_file='img/GANTT.png'):
#     plt.title(title)
#     plt.savefig(save_file, bbox_inches='tight')

if __name__ == '__main__':
    data_file = 'sample.json'
    packages, machine, job, title, xticks, labels, machines, jobs = load_data(data_file)
    start, end, durations, ypos = process_data(packages)
    render_gantt(packages, machines, start, end, ypos, jobs, xticks, labels)
    show_plot()
    # save_plot(title, 'gantt.png')
