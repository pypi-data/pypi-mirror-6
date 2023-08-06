import os

import logging
import threading
import time
import datetime
import pytz
import string
from pybm.util import enum

from pybm.Job import Status
from pybm.Job import Job

from pybm.HttpClient import Request
from collections import OrderedDict

Color = enum(DISABLED="disabled", NOTBUILT="notbuilt", ERROR="red", ABORTED="aborted", OK="blue", WARNING="yellow")

class ParseException(Exception):
    pass

class UnknownProgressException(Exception):
    pass

class JenkinsMonitor():
    api_postfix = '/api/python'

    def __init__(self, httpclient, url, view):
        self.base_url = url
        self.url = url + '/view/' + view + self.api_postfix
        self.view = view
        self.job_list = []
        self.httpclient = httpclient
        self.logger = logging.getLogger(__name__)
#        print self.url

    def get_job_list(self):
        return self.job_list

    def start(self):
        self.alive = True
        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()

    def get_queue(self):
        url = self.base_url + '/queue' + self.api_postfix
        result = {}
        try:
            r = self.httpclient.get(Request(url))
            obj = self.parse_result(r.text)

            d = {}
            # Get the 'in queue time' of each job in queue
            if 'items' in obj:
                for item in obj['items']:
                    d[item['task']['name']] = item['inQueueSince']
            # Order job by the 'in queue time'
            ordered_list = OrderedDict(sorted(d.items(), key=lambda t: t[1]))
            i = 0
            for job in ordered_list:
                i += 1
                result[job] = i
        except Exception, e:
            self.logger.exception(e)
        return result

    def get_job_progress(self, job):
        if 'url' in job:
            try:
                r = self.httpclient.get(Request(job['url'] + self.api_postfix))
                job_details = self.parse_result(r.text)
            except ParseException:
                raise UnknownProgressException('could not parse job details from {0}'.format(r.text))
            except Exception, inner_e:
                self.logger.exception(inner_e)
                raise UnknownProgressException('could not get job details from {0}'.format(job['url'] + self.api_postfix))

            if 'lastBuild' in job_details:
                if 'url' in job_details['lastBuild']:
                    try:
                        r = self.httpclient.get(Request(job_details['lastBuild']['url'] + self.api_postfix))
                    except Exception, inner_e:
                        self.logger.exception(inner_e)
                        raise UnknownProgressException('could not get build details from {0}'.format(job_details['lastBuild']['url'] + self.api_postfix))

                    try:
                        build = self.parse_result(self.repair_erroneous_build_response(r.text))
                    except Exception:
                        self.logger.warning('Could not parse the return value, will try to repair the response')
                        try:
                            build = self.parse_result(self.repair_erroneous_build_response(r.text))
                        except Exception, e:
                            self.logger.exception(e.message)
                            raise UnknownProgressException('could not parse build details')

                    if 'estimatedDuration' in build and 'timestamp' in build:
                        estimated_duration = build['estimatedDuration']
                        timestamp = build['timestamp']
                        return self.calculate_progress(timestamp, estimated_duration)
                    else:
                        raise UnknownProgressException('No "estimatedDuration" or "timestamp" in build details.')
                else:
                    raise UnknownProgressException('No "url" in job"lastBuild".')
            else:
                raise UnknownProgressException('No "lastBuild" in job.')
        else:
            raise UnknownProgressException('No "url" in job.')

    def get_jobs(self):
        queue = self.get_queue()
        try:
            temp_job_list = []
            r = self.httpclient.get(Request(self.url))
#            print r.text
            view = self.parse_result(r.text)
            for job in view['jobs']:
                try:
                    queue_position = queue[job['name']]
                except:
                    queue_position = None
                if job['color'].endswith('anime'):
                    try:
                        temp_job_list.append(Job(job['name'], Status.BUILDING, self.get_job_progress(job), queue_position))
                    except UnknownProgressException:
                        temp_job_list.append(Job(job['name'], self.translate_state(job['color']), 100, queue_position))
                else:
                    temp_job_list.append(Job(job['name'], self.translate_state(job['color']), 100, queue_position))
        except (ParseException, UnknownProgressException):
            temp_job_list = []
            temp_job_list.append(Job('Error getting view "' + self.view + '" from ' + self.url, Status.ERROR, 100))
        except Exception, e:
            self.logger.exception(e.message)
            temp_job_list = []
            temp_job_list.append(Job('Error getting view "' + self.view + '" from ' + self.url, Status.ERROR, 100))
        return temp_job_list

    def run(self):
        while self.alive:
            temp_job_list = self.get_jobs()

            self.job_list = []
            for job in temp_job_list:
                self.job_list.append(job)

            time.sleep(5)

    def stop(self):
        self.alive = False

    def translate_state(self, color_string):
        status = Status.UNKNOWN
        if color_string == Color.NOTBUILT:
            status = Status.UNKNOWN
        elif color_string == Color.DISABLED:
            status = Status.DISABLED
        elif color_string == Color.ERROR:
            status = Status.ERROR
        elif color_string == Color.ABORTED:
            status = Status.UNKNOWN
        elif color_string == Color.OK:
            status = Status.OK
        elif color_string == Color.WARNING:
            status = Status.WARNING
        elif color_string.endswith('anime'):
            status = Status.BUILDING
        return status

    def calculate_progress(self, timestamp, estimated_duration):
        estimated_seconds = datetime.timedelta(milliseconds=estimated_duration).seconds
        naive_timestamp = datetime.datetime(*time.gmtime(timestamp / 1000.0)[:6])
        timerunning = pytz.utc.localize(datetime.datetime.utcnow()) - pytz.utc.localize(naive_timestamp)
        if estimated_seconds <= 0:
            return 100
        else:
            progress = int(float(timerunning.seconds)/float(estimated_seconds)*100)
            if progress > 100:
                progress = 100
            return progress

    def parse_result(self, text):
        try:
            return eval(text)
        except Exception, eval_e:
            self.logger.error('{0} when parsing "{1}"'.format(eval_e, text[0:60].replace('\n', '')))
            raise ParseException()

    def repair_erroneous_build_response(self, text):
        pos = string.find(text, '"changeSet":{"items":')
        if pos == -1:
            return text
        return text[0:pos] + '}'