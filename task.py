import datetime 

class Task(object):
  """Task class"""

  def __init__(self, time_unit=0, content=""):
    super(Task, self).__init__()

    # datetime obj
    self._created = datetime.datetime.now()

    # integer
    self._time_unit = time_unit

    # over time
    self._ot = 0

    # done unit
    self._done = 0

    # text
    self.content = content

  def days_passed(self): 
    # delta, datetime.timedelta obj
    delta = date.datetime.now() - self._created
    # return days passed
    return delta.days

    
    
