#!/usr/bin/env python
'''
Controller script for the rabbitMQ consumers. rabbitMQ and worker settings defined in psettings.py.

This controller is also responsible for declaring the correct exchanges, queues, and bindings that its workers need.
'''
from __future__ import absolute_import
import os,sys
import importlib
import multiprocessing
import time
import signal
import pika
import subprocess
import argparse

import psettings
import workers
from workers import RabbitMQWorker

#Do we continue to distribute this in lib?
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
from lib import daemon


#----------------------------------------------------------
# Define usage args: status|stop|start
COMMANDS = {}
def command(func):
  n = func.__name__
  COMMANDS[n] = func
  return func

def send_signal(sig,pid):
  try:
    os.kill(pid,sig)
  except OSError:
    print "Unable to send signal to pid=%s, maybe stale pid file?" % (pid)
    raise

@command
def status():
  L=Lockfile()
  if L.exists and L.old_pid:
    #Poll the controller process that has been previously started.
    print "Main controller.py process seems to be running with pid=%s" % L.old_pid
    send_signal(signal.SIGUSR1,L.old_pid)
  else:
    print "No master instances could be found."

@command
def stop():
  L=Lockfile()
  if L.exists and L.old_pid:
    print "Shutting down master process=%s and its workers" % L.old_pid
    send_signal(signal.SIGHUP,L.old_pid)
  else:
    print "No master instances could be found."

@command
def start():
  L=Lockfile()
  if L.exists and L.old_pid:
    print "Process seems to be running already:"
    status()
  else:
    print "Starting master process and workers..."
    TM = TaskMaster(psettings.RABBITMQ_URL,psettings.RABBITMQ_ROUTES,psettings.WORKERS)
    dc = daemon.DaemonContext()
    dc.signal_map = {
     signal.SIGHUP: TM.quit,
     signal.SIGUSR1: TM.status,
    }
    dc.stdout=sys.stdout
    dc.stderr=sys.stderr
    dc.open()
    try:
      with dc:
        TM.getLock()
        if not TM.lockfile.acquired:
          print "ERR: Could not acquire logfile, exiting"
        TM.initialize_rabbitmq()
        TM.start_workers()
        print "OK."
        TM.poll_loop()
    except:
      L.release()
      raise

# @command
# def restart():
#   stop()
#   start()
#----------------------------------------------------------

#----------------------------------------------------------

class Singleton:
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

class Lockfile(Singleton):
  def __init__(self,path=psettings.PIDFILE):
    self.path = path
    self.this_pid = os.getpid()
    self.exists = False
    self.old_pid = None
    if os.path.isfile(self.path):
      self.exists = True
      with open(self.path,'r') as fp:
        self.old_pid = int(fp.read())

  def acquire(self):
    try:
      with open(self.path,'w') as fp:
        fp.write('%s' % 

          self.this_pid)
        self.acquired = True
    except:
      self.acquired = False
      raise
    return self.acquired

  def release(self):
    try:
      os.unlink(self.path)
      self.acquired = False
      self.released = True
    except:
      self.released = False
    return self.released


class TaskMaster(Singleton):
  '''TODO: Since this class is run as a daemon, the print statments dont make any sense. 
  Should re-factor to write to a logfile or some other strategy'''
  def __init__(self,rabbitmq_url,rabbitmq_routes,workers):
    self.rabbitmq_url = rabbitmq_url
    self.rabbitmq_routes = rabbitmq_routes
    self.workers = workers

  def getLock(self):
    self.lockfile = Lockfile()
    self.lockfile.acquire()

  def quit(self,signal,frame):
    #Kill child workers if master gets SIGTERM
    try:
      self.stop_workers()
    except:
      print "WARN: Workers not stopped gracefully."
    finally:
      if not self.lockfile.release():
        print "WARN: Lockfile [%s] wasn't removed properly" % (self.lockfile.path)
      self.running = False
      sys.exit(0)

  def status(self,signal,frame):
    #Print status of master+workers
    print "Running workers:"
    for worker,params in self.workers.iteritems():
      for a in params['active']:
        s = "  %s:\t(uptime %0.2f hours)"
        print s % (worker,((time.time()-a['start'])/60/60))
      print "Total: %s" % (len(params['active']))
  def initialize_rabbitmq(self):
    #Make sure the plumbing in rabbitMQ is correct; this procedure is idempotent
    w = RabbitMQWorker()
    w.connect(self.rabbitmq_url)
    w.declare_all(*[self.rabbitmq_routes[i] for i in ['EXCHANGES','QUEUES','BINDINGS']])
    w.connection.close()

  def poll_loop(self,poll_interval=psettings.POLL_INTERVAL,ttl=None):
    while self.running:
      time.sleep(poll_interval)
      for worker,params in self.workers.iteritems():
        current = params['active']
        for active in current:
          if not active['proc'].is_alive():
            print active['proc'],"is not alive, restarting:",worker
            #This is seemingly required by multiprocessing to remove from the OS process list
            active['proc'].terminate()
            active['proc'].is_alive()
            params['active'].remove(active)
            continue
          if ttl:
            if time.time()-active['start']>ttl:
              active['proc'].terminate()
              active['proc'].is_alive()
              params['active'].remove(active)
      self.start_workers(verbose=False)

  def start_workers(self,verbose=True):
    for worker,params in self.workers.iteritems():
      params['active'] = params.get('active',[])
      params['RABBITMQ_URL'] = psettings.RABBITMQ_URL

      while len(params['active']) < params['concurrency']:
        #parent_conn, child_conn = multiprocessing.Pipe()
        w = eval('workers.%s' % worker)(params)
        proc = multiprocessing.Process(target=w.run)
        proc.start()
        if verbose:
          print "Started %s-%s" % (worker,proc.name)
        params['active'].append({
          'proc': proc,
          'start': time.time(),
          })
    self.running=True

  def stop_workers(self):
    for worker,params in self.workers.iteritems():
      params['active'] = params.get('active',[])
      for active in params['active']:
        #This is equivalent to sending SIGTERM to the process;
        #Abrupt termination is fine, since we send ACK only after
        #processing is complete.
        active['proc'].terminate()

#----------------------------------------------------------







#----------------------------------------------------------
def main(argv=sys.argv):
  parser = argparse.ArgumentParser()
  parser.add_argument(
    'command',
    help='|'.join([c for c in COMMANDS]),
    )
  args = parser.parse_args()
  if args.command not in COMMANDS:
    parser.error("Unknown command '%s'" % args.command)

  COMMANDS[args.command]()


#----------------------------------------------------------
   





#----------------------------------------------------------

if __name__ == '__main__':
  main()

#----------------------------------------------------------