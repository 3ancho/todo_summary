import json
import datetime
import os

class Summary(object):
  """docstring for Summary"""

  def __init__(self, app=None, content="", tag=[], dirname="./" ):
    super(Summary, self).__init__()
    self._app = app # a handle to editor
    self._tag = tag # a list
    self._content = content
    self._created = datetime.datetime.now()
    self._dirname = dirname
    filename = "%s.md" % self._created.strftime('%d_%m_%Y')
    self._filepath = os.path.join(self._dirname, filename)

    if os.path.exists(self._filepath):
      self._exists = True
      self.load_from(self._filepath)
    else:
      self._exists = False

  def set_tag(self, tag):
    self._tag = tag

  def set_content(self, content):
    self._content = content

  def load_from(self, filepath):
    load_tag = False
    load_content = False

    tag_line = []
    content_lines = []
    with open(filepath, 'r') as f:
      for line in f.readlines():
        line = line.strip()

        if load_content and line and line[0] != '-':
          content_lines.append(line)
        if load_tag and line and line[0] != '-':
          tag_line.append(line)
          load_tag = False

        if line == 'tag:':
          load_tag = True
        if line == 'content:':
          load_content = True

    self._tag = " ".join(tag_line)
    self._content = "\n".join(content_lines)

    if self._app:
      self._app.summary_edit.set_edit_text(self._tag + "\n\n" + self._content)
        
  @property
  def filepath(self):
    return self._filepath

  def to_json(self, pretty=None):
    if pretty:
      pretty = 4

    d = {}
    d['created'] = self._created.strftime('%d_%m_%Y')
    d['tag'] = self._tag
    d['content'] = self._content
    return json.dumps(d, indent=pretty, separators=(',',': '))

  def set_content_from(self, raw_content):
    # raw_content contains both tag and content

    content = []
    tag = []
    for line in raw_content.split("\n"):
      words = line.split(' ')
      # a line must have both tag and content TODO, correct it
      if len(words) > 0 and len(words[0].strip()) >0 and words[0].strip()[0] == ':':
        tag.append(words[0])
        content.append(" ".join(words[1:]))

    
    self.set_content( "\n".join(content) )
    self.set_tag( ", ".join(tag) )

  def save_md(self):
    with open(self.filepath, 'w') as f:
      f.write("tag:\n")
      f.write("-----\n\n")
      f.write(self._tag)
      f.write("\n\ncontent:\n")
      f.write("--------\n\n")
      f.write(self._content)
    return "saved to file %s" % format(self._filepath)
 
  def save_pickle(self, tag="", content=""):
    pass
