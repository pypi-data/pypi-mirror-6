import datetime
from bson import ObjectId
import pymongo
import time
from .exceptions import RetryInterrupt, CancelInterrupt
from .utils import load_class_by_path
from .queue import Queue
from .context import get_current_worker, log, connections, get_current_config
import gevent


class Job(object):

  # Seconds the job can last before timeouting
  timeout = 300

  # Seconds the results are kept in MongoDB
  result_ttl = 7 * 24 * 3600

  # Exceptions that don't mark the task as failed but as retry
  retry_on_exceptions = (
    pymongo.errors.AutoReconnect,
    pymongo.errors.OperationFailure,
    pymongo.errors.ConnectionFailure,
    RetryInterrupt
  )

  # Exceptions that will make the task as cancelled
  cancel_on_exceptions = (
    CancelInterrupt
  )

  def __init__(self, job_id, worker=None, queue=None, start=False, fetch=False):
    self.worker = get_current_worker()
    self.queue = queue
    self.datestarted = None

    self.collection = connections.mongodb_jobs.mrq_jobs
    self.id = ObjectId(job_id)

    self.data = None
    self.task = None
    self.greenlet_switches = 0
    self.greenlet_time = 0

    if start:
      self.fetch(start=True, full_data=False)
    elif fetch:
      self.fetch(start=False, full_data=False)

  def exists(self):
    return bool(self.collection.find_one({"_id": self.id}, fields={"_id": 1}))

  def fetch(self, start=False, full_data=True):
    """ Get the current job data and possibly flag it as started. """

    if full_data is True:
      fields = None
    elif type(full_data) == dict:
      fields = full_data
    else:
      fields = {
        "_id": 0,
        "path": 1,
        "params": 1,
        "status": 1
      }

    if start:
      self.datestarted = datetime.datetime.utcnow()
      self.data = self.collection.find_and_modify({
        "_id": self.id,
        "status": {"$nin": ["cancel"]}
      }, {"$set": {
        "status": "started",
        "datestarted": self.datestarted,
        "worker": self.worker.id
      }}, fields=fields)
    else:
      self.data = self.collection.find_one({
        "_id": self.id
      }, fields=fields)

    if self.data is None:
      log.info("Job %s not found in MongoDB or status was cancelled!" % self.id)
    else:
      task_def = get_current_config().get("tasks", {}).get(self.data["path"]) or {}
      self.timeout = task_def.get("timeout", self.timeout)
      self.result_ttl = task_def.get("result_ttl", self.result_ttl)

    return self

  def save_status(self, status, result=None, traceback=None, dateretry=None, queue=None, w=1):

    now = datetime.datetime.utcnow()
    updates = {
      "status": status,
      "dateupdated": now
    }

    if self.datestarted:
      updates["totaltime"] = (now - self.datestarted).total_seconds()
    if result is not None:
      updates["result"] = result
    if traceback is not None:
      updates["traceback"] = traceback
    if dateretry is not None:
      updates["dateretry"] = dateretry
    if queue is not None:
      updates["queue"] = queue
    if get_current_config().get("trace_greenlets"):
      current_greenlet = gevent.getcurrent()
      updates["time"] = current_greenlet._trace_time
      updates["switches"] = current_greenlet._trace_switches

    # Make the job document expire
    if status in ("success", "cancel"):
      updates["dateexpires"] = now + datetime.timedelta(seconds=self.result_ttl)

    self.collection.update({
      "_id": self.id
    }, {"$set": updates}, w=w)

    if self.data:
      self.data.update(updates)

  def save_retry(self, exc, traceback=None):

    countdown = 24 * 3600

    if isinstance(exc, RetryInterrupt) and exc.countdown is not None:
      countdown = exc.countdown

    queue = None
    if isinstance(exc, RetryInterrupt) and exc.queue:
      queue = exc.queue

    if countdown == 0:
      self.requeue(queue=queue)
    else:
      self.save_status(
        "retry",
        traceback=traceback,
        dateretry=datetime.datetime.utcnow() + datetime.timedelta(seconds=countdown),
        queue=queue
      )

  def retry(self, queue=None, countdown=None, max_retries=None):

    if self.task.cancel_on_retry:
      raise CancelInterrupt()
    else:
      exc = RetryInterrupt()
      exc.queue = queue
      exc.countdown = countdown
      raise exc

  def cancel(self):
    self.save_status("cancel")

  def requeue(self, queue=None):

    if not queue:
      if not self.data or not self.data.get("queue"):
        self.fetch(full_data={"_id": 0, "queue": 1, "path": 1})
      queue = self.data["queue"]

    self.save_status("queued", queue=queue)

    # Between these two lines, jobs can become "lost" too.

    Queue(queue).enqueue_job_ids([str(self.id)])

  def perform(self):
    """ Loads and starts the main task for this job, the saves the result. """

    if self.data is None:
      return

    log.debug("Starting %s(%s)" % (self.data["path"], self.data["params"]))
    task_class = load_class_by_path(self.data["path"])

    self.task = task_class()

    self.task.is_main_task = True

    result = self.task.run(self.data["params"])

    self.save_status("success", result)

    if get_current_config().get("trace_greenlets"):

      # TODO: this is not the exact greenlet_time measurement because it doesn't
      # take into account the last switch's time. This is why we force a last switch.
      # This does cause a performance overhead. Instead, we should print the
      # last timing directly from the trace() function in context?

      gevent.sleep(0)
      current_greenlet = gevent.getcurrent()
      log.debug("Job %s success: %0.6fs total, %0.6fs in greenlet, %s switches" % (
        self.id, (datetime.datetime.utcnow() - self.datestarted).total_seconds(),
        current_greenlet._trace_time, current_greenlet._trace_switches - 1)
      )
    else:
      log.debug("Job %s success: %0.6fs total" % (
        self.id, (datetime.datetime.utcnow() - self.datestarted).total_seconds()
      ))

  def wait(self, poll_interval=1, timeout=None, full_data=False):
    """ Wait for this job to finish. """

    collection = connections.mongodb_jobs.mrq_jobs

    end_time = None
    if timeout:
      end_time = time.time() + timeout

    while (end_time is None or time.time() < end_time):

      job_data = collection.find_one({
        "_id": ObjectId(self.id),
        "status": {"$nin": ["started", "queued"]}
      }, fields=({
        "_id": 0,
        "result": 1,
        "status": 1
      } if not full_data else None))

      if job_data:
        return job_data

      time.sleep(poll_interval)

    raise Exception("Waited for job result for %ss seconds, timeout." % timeout)
