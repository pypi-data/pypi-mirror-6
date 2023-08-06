# Copyright (C) 2012 Science and Technology Facilities Council.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import json
import mimetypes
import os
import re
import time

import cherrypy
from cherrypy import HTTPError, HTTPRedirect
from mako import exceptions
from mako.lookup import TemplateLookup
from mako.template import Template

from crab import CrabError, CrabStatus
from crab.util.filter import CrabEventFilter

def empty_to_none(value):
    if value == '':
        return None

    return value

class CrabWebQuery:
    """CherryPy handler class for the JSON query part of the crab web
    interface."""

    def __init__(self, store, monitor, service):
        """Constructor: saves the given storage backend and reference
        to the monitor thread."""

        self.store = store
        self.monitor = monitor
        self.service = service

    @cherrypy.expose
    def jobstatus(self, startid, alarmid, finishid):
        """CherryPy handler returning the job status dict fetched
        from the monitor thread."""

        try:
            s = self.monitor.wait_for_event_since(int(startid),
                                                  int(alarmid), int(finishid))
            s['service'] = dict((s, self.service[s].is_alive())
                                for s in self.service)
            return json.dumps(s)
        except ValueError:
            raise HTTPError(400, 'Query parameter not an integer')


    @cherrypy.expose
    def jobinfo(self, id_):
        """CherryPy handler returning the job information for the given job."""
        try:
            info = self.store.get_job_info(int(id_))
        except ValueError:
            raise HTTPError(400, 'Job ID not a number')
        if info is None:
            raise HTTPError(404, 'Job not found')

        info["id"] = id_
        return json.dumps(info)

class CrabWeb:
    """CherryPy handler for the HTML part of the crab web interface."""

    def __init__(self, store, monitor, crab_home, service, options):
        """Constructor for CrabWeb class.

        Stores a reference to the given storage backend, and
        the home directory from the config dict.  Prepares the template
        engine and instantiates a CrabWebQuery object which CherryPy
        can find as 'query'."""
        self.store = store
        self.monitor = monitor
        self.options = options
        self.templ = TemplateLookup(directories=[crab_home + '/templ'])
        self.query = CrabWebQuery(store, monitor, service)

    @cherrypy.expose
    def index(self):
        """Displays the main crab dashboard."""

        try:
            jobs = self.store.get_jobs()
            return self._write_template('joblist.html', {'jobs': jobs})

        except CrabError as err:
            raise HTTPError(message=str(err))

    @cherrypy.expose
    def job(self, id_, command=None, finishid=None,

            barerows=None, unfiltered=None, limit=None, enddate=None,

            submit_config=None, submit_relink=None,
            submit_confirm=None, submit_cancel=None,
            orphan=None, graceperiod=None, timeout=None,
            crabid=None,

            submit_notify=None, **kwargs):
        """Displays information about a current job.

        Currently also supports showing the job output.
        If command='output' but the finishid is not provided, then
        it will find the most recent output for the given job."""

        try:
            id_ = int(id_)
        except ValueError:
            raise HTTPError(400, 'Job number not a number')

        info = self.store.get_job_info(id_)
        if info is None:
            raise HTTPError(404, 'Job not found')

        if command is None:
            if limit is None:
                limit = 100
            else:
                try:
                    limit = int(limit)
                except ValueError:
                    raise HTTPError(400, 'Limit is not a number')
                if limit < 1:
                    raise HTTPError(400, 'Limit should not be less than one')
                elif limit > 1000:
                    raise HTTPError(400, 'Limit greater than a thousand')

            if unfiltered is None:
                squash_start = True
            else:
                squash_start = False

            if enddate is not None:
                try:
                    enddate = self.store.parse_datetime(enddate)
                except ValueError:
                    raise HTTPError(400, 'Start date format is invalid')

            events = self.store.get_job_events(id_, limit, end=enddate)

            if events:
                lastdatetime = events[-1]['datetime']
            else:
                lastdatetime = None

            # Filter the events.
            filter = CrabEventFilter(self.store, info['timezone'])
            events = filter(events, squash_start=squash_start,
                            skip_trivial=squash_start)

            if barerows is not None:
                return self._write_template('jobevents.html',
                           {'id': id_, 'events': events,
                            'lastdatetime': lastdatetime})

            # Try to convert the times to the timezone shown on the page.
            info['installed'] = filter.in_timezone(info['installed'])
            info['deleted'] = filter.in_timezone(info['deleted'])

            # Fetch configuration.
            config = self.store.get_job_config(id_)

            # Fetch job notifications.
            if config is not None:
                notification = self.store.get_job_notifications(
                                   config['configid'])
            else:
                notification = None

            return self._write_template('job.html',
                       {'id': id_, 'info': info, 'config': config,
                        'status': self.monitor.get_job_status(id_),
                        'notification': notification, 'events': events,
                        'lastdatetime': lastdatetime})

        elif command == 'clear':
            if submit_confirm:
                self.store.log_alarm(id_, CrabStatus.CLEARED)

                # Wait for the monitor to process new events so that
                # that the job is in an 'OK' state before we reload the page.
                with self.monitor.new_event:
                    self.monitor.new_event.wait(10)

                raise HTTPRedirect("/job/" + str(id_))

            elif submit_cancel:
                raise HTTPRedirect("/job/" + str(id_))

            else:
                return self._write_template('confirm.html',
                       {'id': id_, 'info': info,
                        'title': 'clear status',
                        'description': 'Reset the job status?',
                        'target': '/job/' + str(id_) + '/clear'})

        elif command == 'delete':
            notdeleted = info['deleted'] is None
            if submit_confirm:
                if notdeleted:
                    self.store.delete_job(id_)
                else:
                    self.store.undelete_job(id_)

                raise HTTPRedirect('/job/' + str(id_))

            elif submit_cancel:
                raise HTTPRedirect('/job/' + str(id_))

            else:
                return self._write_template('confirm.html',
                       {'id': id_, 'info': info,
                       'title': 'delete' if notdeleted else 'undelete',
                       'description': ('Delete' if notdeleted else 'Undelete') +
                                       ' this job from the server?',
                       'target': '/job/' + str(id_) + '/delete'})

        elif command == 'changeid':
            if submit_confirm:
                if crabid != '':
                    if self.store.get_jobs(info['host'], info['user'],
                            include_deleted=True, crabid=crabid):
                        raise HTTPError(400, 'Specified job ID already exists.')
                    else:
                        self.store.update_job(id_, crabid=crabid)
                        raise HTTPRedirect('/job/' + str(id_))
                else:
                    raise HTTPError(400, 'Specified job ID is blank.')

            elif submit_cancel:
                raise HTTPRedirect('/job/' + str(id_))

            else:
                return self._write_template('confirm.html',
                       {'id': id_, 'info': info,
                       'title': 'change identifier',
                       'description': 'Change Job ID for this job?  Please note '
                                      'that the ID which will be used to report '
                                      'events related to this job should be '
                                      'updated at the same time to ensure that '
                                      'the job continues to be correctly '
                                      'identified.  This should be done in the '
                                      'crontab if the CRABID variable is used, '
                                      'or in the cron job itself in the case '
                                      'of Crab-aware cron jobs.',
                       'target': '/job/' + str(id_) + '/changeid',
                       'data': {'crabid': crabid}})

        elif command == 'output':
            finishid_next = None
            finishid_prev = None

            if finishid is None:
                # If finishid is not specified, select the most recent
                # for this job.
                finishes = self.store.get_job_finishes(id_, limit=2)

                if not finishes:
                    raise HTTPError(404, 'No job output found')

                finish = finishes[0]
                finishid = finish['finishid']

                if len(finishes) > 1:
                    finishid_prev = finishes[1]['finishid']

            else:
                try:
                    finishid = int(finishid)
                except ValueError:
                    raise HTTPError(400, 'Finish ID is not a number')

                finishes = self.store.get_job_finishes(id_, finishid=finishid)
                if not finishes:
                    raise HTTPError(404, 'Finish ID not found or wrong job')
                finish = finishes[0]

                finishes = self.store.get_job_finishes(id_, 1, before=finishid)
                if finishes:
                    finishid_prev = finishes[0]['finishid']

                finishes = self.store.get_job_finishes(id_, 1, after=finishid)
                if finishes:
                    finishid_next = finishes[0]['finishid']

            (stdout, stderr) = self.store.get_job_output(finishid,
                    info['host'], info['user'], id_, info['crabid'])

            filter = CrabEventFilter(self.store, info['timezone'])
            finish['datetime'] = filter.in_timezone(finish['datetime'])

            return self._write_template('joboutput.html',
                       {'id': id_, 'info': info, 'finish': finish,
                        'stdout': stdout, 'stderr': stderr,
                        'next': finishid_next, 'prev': finishid_prev})

        elif command == 'config':
            if submit_relink:
                try:
                    orphan = int(orphan)
                except ValueError:
                    raise HTTPError(400, 'Orphan number not a number')

                self.store.relink_job_config(orphan, id_)
                raise HTTPRedirect("/job/" + str(id_))

            elif submit_config:
                try:
                    if timeout == '':
                        timeout = None
                    elif timeout is not None:
                        timeout = int(timeout)
                    if graceperiod == '':
                        graceperiod = None
                    elif graceperiod is not None:
                        graceperiod = int(graceperiod)
                except ValueError:
                    raise HTTPError(400, 'Time not a number')

                self.store.write_job_config(id_, graceperiod, timeout)
                raise HTTPRedirect("/job/" + str(id_))

            else:
                config = self.store.get_job_config(id_)

                if config is None:
                    orphan = self.store.get_orphan_configs()
                else:
                    orphan = None

                return self._write_template('jobconfig.html',
                           {'id': id_, 'info': info, 'config': config,
                            'orphan': orphan})

        elif command == 'notify':
            if submit_notify:
                # Ensure that this job has a configuration entry
                # so that we can link to it.
                config = self.store.get_job_config(id_)

                if config is not None:
                    configid = config['configid']
                else:
                    configid = self.store.write_job_config(id_)

                # Make a list of notifications for this job
                # so that we can delete those which are not
                # included in the POST parameters.
                existing = set()
                for notification in self.store.get_job_notifications(configid):
                    existing.add(notification['notifyid'])

                # Update existing notifications.
                for kwarg in kwargs:
                    match = re.search('method_(new_)?(\d+)', kwarg)
                    if not match:
                        continue

                    if match.group(1):
                        key = ''.join(match.groups())
                        notifyid = None
                    else:
                        key = match.group(2)
                        notifyid = int(key)
                        existing.discard(notifyid)

                    self.store.write_notification(
                            notifyid, configid,
                            None, None,
                            kwargs['method_' + key],
                            kwargs['address_' + key],
                            empty_to_none(kwargs['time_' + key]),
                            empty_to_none(kwargs['timezone_' + key]),
                            'include_ok_' + key not in kwargs,
                            'include_warning_' + key not in kwargs,
                            'include_error_' + key not in kwargs,
                            'include_output_' + key in kwargs)

                # Delete existing notifications which were not present.
                for notifyid in existing:
                    self.store.delete_notification(notifyid)

                raise HTTPRedirect('/job/' + str(id_))
            else:
                config = self.store.get_job_config(id_)

                if config is not None:
                    notifications = self.store.get_job_notifications(
                                        config['configid'])
                else:
                    notifications = None

                return self._write_template('editnotify.html',
                            {'match_mode': False,
                             'id': id_, 'info': info,
                             'notifications': notifications})

        else:
            raise HTTPError(404, 'Unknown job command')

    @cherrypy.expose
    def user(self, user):
        """Displays crontabs belonging to a particular user."""
        return self._user_host_crontabs(user=user)

    @cherrypy.expose
    def host(self, host):
        """Displays crontabs belonging to a particular user."""
        return self._user_host_crontabs(host=host)

    def _user_host_crontabs(self, host=None, user=None):
        """Displays crontab listing, either by host or user."""

        jobs = {}
        raw = {}
        info = {'jobs': jobs, 'raw': raw}

        if host is None and user is not None:
            by_user = False
            info['user'] = user
            info['host'] = None
        elif host is not None and user is None:
            by_user = True
            info['host'] = host
            info['user'] = None
        else:
            raise HTTPError(500, 'Need one of host or user to be specified')

        for job in self.store.get_jobs(host, user, include_deleted=True):
            if by_user:
                key = job['user']
            else:
                key = job['host']

            if key in jobs:
                jobs[key].append(job)
            else:
                jobs[key] = [job]
                raw[key] = self.store.get_raw_crontab(job['host'], job['user'])

        return self._write_template('crontabs.html', info)

    @cherrypy.expose
    def notify(self, submit_notify=None, **kwargs):
        """Allows match-based notifications to be viewed and configured."""

        notifications = self.store.get_match_notifications()

        if submit_notify:
            # Make a list of notifications for this job
            # so that we can delete those which are not
            # included in the POST parameters.
            existing = set()
            for notification in notifications:
                existing.add(notification['notifyid'])

            # Update existing notifications.
            for kwarg in kwargs:
                match = re.search('method_(new_)?(\d+)', kwarg)
                if not match:
                    continue

                if match.group(1):
                    key = ''.join(match.groups())
                    notifyid = None
                else:
                    key = match.group(2)
                    notifyid = int(key)
                    existing.discard(notifyid)

                self.store.write_notification(
                        notifyid, None,
                        empty_to_none(kwargs['host_' + key]),
                        empty_to_none(kwargs['user_' + key]),
                        kwargs['method_' + key],
                        kwargs['address_' + key],
                        empty_to_none(kwargs['time_' + key]),
                        empty_to_none(kwargs['timezone_' + key]),
                        'include_ok_' + key not in kwargs,
                        'include_warning_' + key not in kwargs,
                        'include_error_' + key not in kwargs,
                        'include_output_' + key in kwargs)

            # Delete existing notifications which were not present.
            for notifyid in existing:
                self.store.delete_notification(notifyid)

            raise HTTPRedirect('/')
        else:
            return self._write_template('editnotify.html',
                                        {'match_mode': True,
                                         'notifications': notifications})

    @cherrypy.expose
    def dynres(self, name):
        if name == 'crabutil.js':
            return self._write_template('dynres/crabutil.js', {})
        else:
            raise HTTPError(404, 'Dynamic resource not found')

    def _write_template(self, name, dict={}):
        """Returns the output from the named template when rendered
        with the given dict.

        Traps template errors and uses mako.exceptions to display them."""

        try:
            template = self.templ.get_template(name)
            return template.render(options=self.options, **dict)
        except:
            return exceptions.html_error_template().render()

