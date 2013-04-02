import datetime 

class Todo(object):
  """Task class"""

  def __init__(self, time_unit=0, content="", app=None):
    super(Todo, self).__init__()

    # datetime obj
    self._created = datetime.datetime.now()

    # integer
    self._time_unit = time_unit

    # over time
    self._ot = 0

    # done time
    self._dt = 0

    # text
    self.content = content

    self.view = None

    self._done = False

  def toggle_done(self):
    if self._done:
      self._done = False
    else:
      self._done = True
    

  def days_passed(self): 
    # delta, datetime.timedelta obj
    delta = date.datetime.now() - self._created
    # return days passed
    return delta.days
