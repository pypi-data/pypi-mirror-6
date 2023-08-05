import sys
import pygame
import socket
from pybm.Job import Status
from pybm.JenkinsMonitor import JenkinsMonitor
from pybm.ProgressBar import ProgressBar
from pybm.HttpClient import HttpClient

OK = (0, 150, 0)
WARNING = (255, 204, 51)
ERROR = (150, 0, 0)
UNKNOWN = (172, 172, 172)
BUILDING = (0, 122, 172)

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('url', metavar='Url', type=str,
                   help='jenkins url')
parser.add_argument('view', metavar='View', type=str,
                   help='view to visualise')

args = parser.parse_args()

print args.view, args.url

def get_color(state):
    if state == Status.OK:
        return OK
    elif state == Status.WARNING:
        return WARNING
    elif state == Status.ERROR:
        return ERROR
    elif state == Status.WARNING:
        return WARNING
    elif state == Status.BUILDING:
        return BUILDING
    else:
        return UNKNOWN

pygame.init()
clock = pygame.time.Clock()
#size = width, height = 1024, 768
#screen = pygame.display.set_mode(size)
size = width, height = 0, 0
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
font = pygame.font.SysFont('sans-serif', 160, True)
pygame.mouse.set_visible(0)

margin = 10

jobMonitor = JenkinsMonitor(HttpClient(), args.url, args.view)
jobMonitor.start()

show_info = False

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()  # Exit the main loop
            sys.exit()
        elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()  # Exit the main loop
                    sys.exit()
                elif event.key == pygame.K_i: # display info when 'i' is pressed
                    if show_info:
                        show_info = False
                    else:
                        show_info = True

    screen.fill((0, 0, 0))

    jobs = jobMonitor.get_job_list()
    disabled_builds = 0
    for job in jobs:
        if job.status == Status.DISABLED:
            disabled_builds += 1

    job_count = len(jobs) - disabled_builds

    if job_count > 0:
        bar_height = (screen.get_size()[1]-((job_count+1)*margin))/job_count
        bars = []
        j = 0

        for job in jobs:
            if job.status != Status.DISABLED:
                bar_x = margin
                bar_y = (margin*(j + 1)) + (bar_height * j)
                bar_width = screen.get_size()[0]-(margin*2)
                bars.append(ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, job.name))
                bars[j].set_color(get_color(job.status))
                bars[j].update(job.percentage)
                j += 1
    else:
        bar_height = screen.get_size()[1] - margin
        bar_x = margin
        bar_y = margin
        bar_width = screen.get_size()[0]-(margin*2)
        bar = ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, 'Loading')
        bar.set_color(get_color(Status.UNKNOWN))
        bar.update(100)

    # display the ip address(es)
    if show_info:
        ip_list = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
        ip_string = ''
        for ip in ip_list:
            ip_string = ip_string + ' ' + ip
        txt_color = (255, 255, 255)
        font = pygame.font.Font(None, 64)
        text = font.render(ip_string, True, txt_color)
        screen.blit(text, (0, 0))

    pygame.display.flip()
    clock.tick(1)
