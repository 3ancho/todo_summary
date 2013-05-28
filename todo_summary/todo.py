# -*- coding: utf-8 -*-
import datetime 

class Todo(object):
  """Todo item class"""

  def __init__(self, time_unit=0, content=u'', app=None):
    super(Todo, self).__init__()

    # datetime obj
    self._created = datetime.datetime.now()
    self._done_date = None 

    # integer
    self._time_unit = time_unit
    self._done_unit = 0 

    # over time
    self._ot = 0

    # done time
    self._dt = 0

    # text
    self.content = content

    self.view = None

    self._done = False

  def toggle_done(self):
    # toggle binded TodoItem in UI
    if self._done:
      self._done = False
      self._done_date = None
    else:
      self._done = True
      self._done_date = datetime.datetime.now()
    self.view._change_mark()
    
  def days_passed(self): 
    # delta, datetime.timedelta obj
    delta = date.datetime.now() - self._created
    # return days passed
    return delta.days

  def update_time(self):
    self._done_unit += 1

  def to_edit(self):
    title = self.content 
    return title

  @property
  def mark(self):
    if self._done:
      return u'✓'
    else:
      return u'*'

  def __unicode__(self):
    percent = (u' %d/%d' % (self._done_unit, self._time_unit)).ljust(5)
    
    return u' %s %s %s' % (self.mark, percent, self.content)

  def __str__(self):
    return unicode(self).encode('utf-8')


