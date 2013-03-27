# when using py2app, this includes a lot of packages
import time
import urwid 
from sys import platform

from threading import Timer

from summary import Summary
from todo import Todo
from widgets import ViEdit
from widgets import TodoEdit
from widgets import TodoItem
from widgets import TodoPile
from sound import play_sound

# static util functions
def last(n, li):
  # take a list return a string
  if n > 0 and n <= len(li):
    return ''.join(li[-1*n:])
  else:
    return ''

class App:
  def __init__(self):
    palette = [
        ('body','dark blue', '', 'standout'),
        ('footer','light red', '', 'black'),
        ('header','light blue', 'black'),
        ('select','light red', '', 'black'),
    ]

    # Two Models App deals with
    self.todos = None
    self.summary = None

    if platform == "darwin":
      from pync import Notifier
      self._nc = Notifier
    else:
      self._nc = None
      

    # init sound, register alerm
    # TODO

    # reusable widges
    self.divider = urwid.Divider(u"-");

    # header 
    header_text = "Summary" 
    self.header = urwid.Text("Editing: %s\n" % header_text)
    self.v_header = urwid.AttrMap(self.header, 'header')

    # summary
    self.summary_edit = ViEdit(u"Summary:\n", multiline=True, app=self)

    # v_footer = footer + txt
    self.footer = urwid.Text(u'')
    self.txt = urwid.Text(u"Display") # debug
    self.footer_pile = urwid.Pile( [self.txt, self.footer] )
    self.v_footer = urwid.AttrMap(self.footer_pile, 'footer')

    # summary_fill can be frame.body, option 1
    self.summary_pile = urwid.Pile([ self.summary_edit, self.divider])
    self.summary_fill = urwid.Filler(self.summary_pile, 'top')

    # Todos 
    self.todos = []
    item = urwid.AttrWrap(TodoItem(" * " + "Default one lean this software"), 'body')
    self.todos.append(item)

    self.todo_edit = TodoEdit(caption=u"Todo:\n", multiline=False, mode=1, app=self)

    self.todos.insert(0, self.todo_edit)
    self.todo_pile = TodoPile(self.todos, app=self, focus_item=0)
    self.todo_fill = urwid.Filler(self.todo_pile, 'top')

    # TODO chose which view to show first in cfg file
    self.frame = urwid.Frame(self.todo_fill, header=self.v_header, footer=self.v_footer)
    self.v_frame = urwid.AttrMap(self.frame, 'body')

    # set main loop
    self.loop = urwid.MainLoop(self.v_frame, palette, unhandled_input=self.app_keypress)

    self._todo_focus = 0 # focus todo_edit at first place

  def get_todo_focus(self):
    return self._todo_focus

  def set_todo_focus(self, i):
    self._todo_focus = i

  def init_models(self):
    # Todo
    items = []
    items.append(TodoItem("Default one: lean this software"))

  def run(self):
    self.todo = Todo(app=self)
    # TODO make this path in config file
    # TODO create defaul for osx and linux
    self.summary = Summary(app=self, dirname='/Users/ruoran/Dropbox/todo_summary_doc')
    self.header.set_text(self.summary.filepath)
    self.loop.run()

  # TODO change txt into a display window
  def debug(self, something):
    self.txt.set_text("app level: " + str(something))

  def app_keypress(self, key):
    # 1. Check Body = ?
    if self.frame.get_body() == self.todo_fill:
      target = self.todo_edit
      t = 'todo'
    elif self.frame.get_body() == self.summary_fill:
      target = self.summary_edit
      t = 'summary'
    else:
      return 

    self.debug(target.key_buf) 
    # 2. Handle
    if key == 'esc':
      pass
    elif key == 'tab':
      pass
    elif key == 'enter':
      command = target.key_buf[:-1] # pop the 'enter' key
      target.key_buf = []
      self.debug(command)

      if last(2, command) == ':q': 
        raise urwid.ExitMainLoop()

      if last(2, command) == ':w': 
        self.debug("saving " + t)
        self.update(t)
        self.save(t)
        pass

      if last(2, command) == ':x' or last(3, command) ==  ':wq': 
        time.sleep(0.2) # flash the message 
        raise urwid.ExitMainLoop()

      if last(3, command) == ':to' or last(2, command) == ':t':
        self.frame.set_body(self.todo_fill)
        self.todo_edit.keypress = self.todo_edit.cmd_keypress

      if last(3, command) == ':su' or last(2, command) == ':s':
        self.frame.set_body(self.summary_fill)
        self.summary_edit.keypress = self.summary_edit.cmd_keypress
    # End elif 'enter'
  # End func

  def update(self, t=None):
    if t == None:
      return
    elif t == 'summary':
      self.summary.set_content_from( self.summary_edit.get_edit_text() )
    elif t == 'todo':
      pass

  def save(self, t=None):
    if t == None:
      return
    elif t == 'summary':
      filepath = self.summary.save_md()
      self.footer.set_text('Saved to: %s' % filepath)
    elif t == 'todo':
      pass

  def set_timer(self, time_in=25*60):
    self.loop.set_alarm_in(0, self.alarm, {'opt': 'start', 'name': 'scifi_start.wav'})
    if self._nc:
      self._nc.notify('A task has started', title='todo-summary')

    # TODO return 3 handles for app to stop it

    # time passed by
    self.loop.set_alarm_in(10*60, self.alarm, {'opt': 'middle', 'name': 'paper.wav'})
    # time passed by
    self.loop.set_alarm_in(20*60, self.alarm, {'opt': 'middle', 'name': 'paper.wav'})
    # time up 
    self.loop.set_alarm_in(25*60, self.alarm, {'opt': 'end', 'name': 'horn.wav'})

  def count(self, loop=None, sec=25*60):
    if sec == 0:
      return
    else:
      self.clock_tick(sec)
      # TODO handle for the newly set alarm
      self.loop.set_alarm_in(1, self.count, sec-1) 

  def clock_tick(self, time_left):
    # TODO Make window better, min: sec
    self.debug(time_left)

  def alarm(self, loop, data):
    if data['name']:
      play_sound(data['name'])
    if data['opt'] and data['opt'] == 'end':
      if self._nc:
        self._nc.notify('Time to break', title='todo-summary')
      # TODO 
      # 1. Notification for a 5 min break (move)
      # 2. Make sure alarm are closed.
      # 3. Footer set_text
      # 4. Time unit--
      # 5. Add time, minuste time, move to next task 
      pass

# End of App
def main():
  app = App()
  app.run()

if __name__ == '__main__':
  main()

