"""
Copyright (c) 2011, 2012, Regents of the University of California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions 
are met:

 - Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 - Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
OF THE POSSIBILITY OF SUCH DAMAGE.
"""
"""
@author Tyler Hoyt <thoyt@berkeley.edu>
"""
from twisted.internet import task, reactor, defer
import util
import time

class SmapJob:
    
    def __init__(self, job):
        self.name = job['Name'] if 'Name' in job else None
        self.after = job['After'] if 'After' in job else None
        self.start_time = job['StartTime'] if 'StartTime' in job else None
        self.actions = job['Actions']
        if 'Async' in job: 
            str_async = job['Async'].lower()
            self.async = True if str_async in ['true', 't', '1'] else False
        else:
            self.async = True
        if self.async: self.d_inner = defer.Deferred()

class SmapJobsManager:
    
    def __init__(self, path, inst):
        self.jobs = []
        self._job_ids = {}
        self.inst = inst
        self.actuators = [path]

    def add_job(self, job):
        j = SmapJob(job)
        self.jobs.append(j)
        if 'StartTime' in job:
            start = job['StartTime'] / 1000.
            wait = start - util.now()
        else:
            wait = 0
        assert wait >= 0
        actions = j.actions
        if j.after:
            previous_job = util.find(lambda x: x.name == j.after, self.jobs)
            if previous_job is None:
                raise SmapException("No job named %s") % j.after
            else:
                j.d_outer = previous_job.d_outer
                j.job_id = previous_job.job_id
                self._job_ids[job['uuid']] = j.job_id
        else: # assign it its own deferred
            j.d_outer = defer.Deferred()

        # closure that will carry out all of the job's actions
        def act(_):
            for action in actions:
                path = action['Path']
                state = action['State']
                actuator = self.inst.get_timeseries(path)
                print 'setting', path, 'to', state
                if j.async:
                    j.d_inner.addCallback(lambda: actuator.set_state(None,state))
                else:
                    actuator.set_state(None, state)

        # queue the callback
        j.d_outer.addCallback(act)
        print 'added callback to', j.d_outer
       
        if not j.after:
            # job_id will let you cancel it
            # j.job_id = reactor.callLater(wait, act)
            j.job_id = reactor.callLater(wait, j.d_outer.callback, None)
            self._job_ids[job['uuid']] = j.job_id
        
        return j.d_outer
  
    def cancel_job(self, uuids):
        for uuid in uuids:
            print 'cancelling job', uuid
            call_id = self._job_ids[uuid]
            call_id.cancel()

