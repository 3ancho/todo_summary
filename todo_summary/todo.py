# -*- coding: utf-8 -*-
import datetime 
import json
import os

class Todo(object):
  """Todo item class"""

  def __init__(self, time_unit=0, content=u'', app=None, dirname='./'):
    super(Todo, self).__init__()
    self.view = None # need this

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

    # The name of the task 
    self.content = content

    self._done = False
    self.tags = ["abc"] # a list
    self._summary = ""  # summary not ready yet
    self._dirname = dirname

    md_filename = '%s.md' % self._created.strftime('%Y_%m_%d')
    self._md_filepath = os.path.join(self._dirname, md_filename)

    json_filename = '%s.json' % self._created.strftime('%Y_%m_%d')
    self._json_filepath = os.path.join(self._dirname, json_filename)

  def set_tags(self, tags):
    self.tags = tags

  def set_content(self, content):
    self._content = content

  # need read from json
  def load_from(self, filepath):
    pass
        
  @property
  def md_filepath(self):
    return self._md_filepath

  @property
  def json_filepath(self):
    return self._json_filepath

  def to_json(self, pretty=None):
    if pretty:
      pretty = 4

    d = {}
    d['created'] = self._created.strftime('%d_%m_%Y')
    d['done_date'] = self._done_date.strftime('%d_%m_%Y')
    d['time_unit'] = self._time_unit
    d['done_unit'] = self._done_unit
#    d['tags'] = self.tags
    d['content'] = self.content
    d['summary'] = self._summary
    return json.dumps(d, indent=pretty, separators=(',',': '))

  def save_md(self):
    with open(self.filepath, 'w') as f:
      f.write(self._content)
    return 'saved to file %s' % format(self._filepath)
 
  def save_pickle(self, tag='', content=''):
    pass
  

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


