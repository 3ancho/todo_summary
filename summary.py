import json
import datetime

class Summary(object):
  """docstring for Summary"""

  def __init__(self, content="", tags=[]):
    super(Summary, self).__init__()
    # self.tags is a list
    self._tags = tags
    self._content = content
    self._created = datetime.datetime.now()

  def to_json(self, pretty=None):
    if pretty:
      pretty = 4

    d = {}
    d['created'] = self._created.strftime('%d_%m_%Y')
    d['tags'] = self._tags
    d['content'] = self._content
    return json.dumps(d, indent=pretty, separators=(',',': '))

  # static method
  @staticmethod
  def bootstrap():
    sum = Summary()
    
    # test file existense
    # if exist append ? 

    now = datetime.datetime.now()
    filename = "{}.md".format(now.strftime('%d_%m_%Y'))
    with open(filename, 'w+') as f:
      f.write("tags:\n")
      f.write("-----\n\n")
      f.write("content:\n")
      f.write("--------\n\n")

    print "created file {}".format(filename)
 





    
