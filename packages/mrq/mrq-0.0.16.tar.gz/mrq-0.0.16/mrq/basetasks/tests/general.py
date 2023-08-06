from time import sleep
from mrq.task import Task
from mrq.context import log, retry_current_job, connections
import urllib2


class Add(Task):

  def run(self, params):

    log.info("adding", params)
    res = params.get("a", 0) + params.get("b", 0)

    if params.get("sleep", 0):
      log.info("sleeping", params.get("sleep", 0))
      sleep(params.get("sleep", 0))

    return res


class TimeoutFromConfig(Add):
  pass


class TimeoutFromConfigAndCancel(Add):
  cancel_on_timeout = True


class Fetch(Task):
  def run(self, params):

    f = urllib2.urlopen(params.get("url"))
    t = f.read()
    f.close()

    return len(t)


class Retry(Task):

  def run(self, params):

    log.info("Retrying in %s on %s" % (params.get("countdown"), params.get("queue")))

    connections.mongodb_logs.tests_inserts.insert(params)

    if params.get("cancel_on_retry"):
      self.cancel_on_retry = params.get("cancel_on_retry")

    retry_current_job(queue=params.get("queue"), countdown=params.get("countdown"))

    raise Exception("Should not be reached")


class RaiseException(Task):

  def run(self, params):

    sleep(params.get("sleep", 0))

    raise Exception(params.get("message", ""))


class ReturnParams(Task):

  def run(self, params):

    sleep(params.get("sleep", 0))

    return params


class MongoInsert(Task):

  def run(self, params):

    connections.mongodb_logs.tests_inserts.insert(params)


MongoInsert2 = MongoInsert
