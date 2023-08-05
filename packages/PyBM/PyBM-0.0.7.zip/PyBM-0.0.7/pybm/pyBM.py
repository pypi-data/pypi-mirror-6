import logging
import logging.config
import sys
import pygame
import socket
import os
from pybm.Job import Status
from pybm.JenkinsMonitor import JenkinsMonitor
from pybm.ProgressBar import ProgressBar
from pybm.HttpClient import HttpClient
from optparse import OptionParser

__version__ = '0.0.2'
__date__ = '2013-04-22'
__updated__ = '2013-04-22'

OK = (0, 150, 0)
WARNING = (255, 204, 51)
ERROR = (150, 0, 0)
UNKNOWN = (172, 172, 172)
BUILDING = (0, 122, 172)

import argparse

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

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parseOptions()

    try:
        logging.config.fileConfig(args.logconfigfile)
    except:
        print "Could not parse logging config file '{0}', using defaults.".format(args.logconfigfile)

    logger = logging.getLogger(__name__)

    logger.info(args.view + " " + args.url)

    pygame.init()
    clock = pygame.time.Clock()
    if args.windowed:
        size = width, height = 1280, 1024
        screen = pygame.display.set_mode(size)
    else:
        size = width, height = 0, 0
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    font_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'segoeui.ttf')
    font = pygame.font.Font(font_file, 64)
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
                        print "i is pressed"
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
                    bars.append(ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, job.name, font))
                    bars[j].set_color(get_color(job.status))
                    bars[j].update(job.percentage)
                    j += 1
        else:
            bar_height = screen.get_size()[1] - margin
            bar_x = margin
            bar_y = margin
            bar_width = screen.get_size()[0]-(margin*2)
            bar = ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, 'Loading', font)
            bar.set_color(get_color(Status.UNKNOWN))
            bar.update(100)

        # display the ip address(es)
        if show_info:
            ip_list = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
            ip_string = 'IPs: '
            for ip in ip_list:
                ip_string = ip_string + ' ' + ip
            txt_color = (255, 255, 255)
            text = font.render(ip_string, True, txt_color)
            screen.blit(text, (0, 0))

        pygame.display.flip()
        clock.tick(1)

def parseOptions():
    program_name = os.path.basename(sys.argv[0])
    program_version = __version__
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2014 Jos (CircuitDB.com)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

    try:
        # setup option parser
        parser = argparse.ArgumentParser()
        parser.add_argument('url',  type=str, help='jenkins url')
        parser.add_argument('view', nargs='?', help='view to visualise', default='All')
        parser.add_argument('-l', nargs='?', dest="logconfigfile", help="specifies the config file for logging", metavar="FILE", default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging.conf'))
        parser.add_argument('-w', dest="windowed", action="store_true", help="run in 1024x768 which results in windowed mode", default=False)
        args = parser.parse_args()

        return args

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == '__main__':
    sys.exit(main())