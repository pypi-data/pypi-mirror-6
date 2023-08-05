import logging
import threading
import time
import datetime
import pytz
from pybm.util import enum

from pybm.Job import Status
from pybm.Job import Job

from pybm.HttpClient import Request

Color = enum(DISABLED="disabled", NOTBUILT="notbuilt", ERROR="red", ABORTED="aborted", OK="blue", WARNING="yellow")

class ParseException(Exception):
    pass

class JenkinsMonitor():
    api_postfix = '/api/python'

    def __init__(self, httpclient, url, view):
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

    def get_jobs(self):
        try:
            temp_job_list = []
            r = self.httpclient.get(Request(self.url))
#            print r.text
            view = self.parse_result(r.text)
            for job in view['jobs']:
                if job['color'].endswith('anime'):
                    try:
                        r = self.httpclient.get(Request(job['url'] + self.api_postfix))
                        job_details = self.parse_result(r.text)
                        r = self.httpclient.get(Request(job_details['lastBuild']['url'] + self.api_postfix))
                        build = self.parse_result(r.text)
                        estimated_duration = build['estimatedDuration'] # estimate duration is -1 for first build!
                        timestamp = build['timestamp']
                        temp_job_list.append(
                            Job(job['name'], Status.BUILDING, self.calculate_progress(timestamp, estimated_duration)))
                    except ParseException:
                        temp_job_list.append(Job(job['name'], Status.BUILDING, 100))
                    except Exception, inner_e:
                        self.logger.exception(inner_e)
                        temp_job_list.append(Job(job['name'], Status.BUILDING, 100))
                else:
                    temp_job_list.append(Job(job['name'], self.translate_state(job['color']), 100))
        except ParseException:
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
            self.logger.error('{0} when parsing {1}'.format(eval_e.message, text[0:30]))
            raise ParseException()
