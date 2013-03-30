# -*- coding: utf-8 -*- 

# when using py2app, this includes a lot of packages
import time
import datetime
import logging
import urwid 

from sys import platform
from threading import Timer

from summary import Summary
from todo import Todo
from widgets import ViEdit
from widgets import TodoEdit
from widgets import TodoItem
from sound import play_sound

# static util functions
def last(n, li):
  # take a list return a string
  if n > 0 and n <= len(li):
    return ''.join(li[-1*n:])
  else:
    return ''

class App:
  def __init__(self, dist=None):
    # init logger

    logger = logging.getLogger('tosu')
    hdlr = logging.FileHandler('./tosu.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)

    logger.debug('init ok')

    # Path for file
    if not dist:
      dist = "./"
    self.dist = dist

    # Two Models App deals with
    self.todos = None
    self.summary = None

    # Sound player
    if platform == "darwin":
      from pync import Notifier
      self._nc = Notifier
    else:
      self._nc = None

    self.init_ui()

    palette = [
        ('body','dark blue', '', 'standout'),
        ('footer','light red', '', 'black'),
        ('header','light blue', 'black'),
        ('select','light red', '', 'black'),
    ]

    # set main loop
    self.loop = urwid.MainLoop(self.frame, palette, unhandled_input=self.app_keypress)

    # Store alarm handles
    self._timer_handle = None
    # you don't break until you finish a task
    self._break = False

  def init_models(self):
    pass

  def init_ui(self):
    # reusable widges
    self.divider = urwid.Divider(u"-");

    # header 
    header_text = "Summary" 
    self.header = urwid.AttrWrap(urwid.Text("Editing: %s\n" % header_text), 'header')

    # footer_pile = footer + txt
    self.footer = urwid.Text(u'')
    self.txt = urwid.Text(u'') # display
    self.footer_pile = urwid.AttrWrap(urwid.Pile( [self.txt, self.footer] ), 'footer')

    # Summary
    # summary_fill can be frame.body, option 1
    self.summary_edit = ViEdit(u"Summary:\n", multiline=True, app=self)
    self.summary_pile = urwid.Pile([self.summary_edit, self.divider])
    self.summary_fill = urwid.Filler(self.summary_pile, 'top')

    # Todos 
    # todo_fill can be frame.body, option 2
    self.todos = []
    # Load defualt items
    item = urwid.AttrWrap(TodoItem(" * " + "Default one lean this software"), 'body')
    self.todos.append(item)

    # mode = 1, insert mode
    self.todo_edit = TodoEdit(caption=u'Todo:\n>>> ', multiline=False, mode=1, app=self)

    self.todos.insert(0, self.todo_edit)
    self.todo_pile = urwid.Pile(self.todos, focus_item=0)
    self.todo_fill = urwid.Filler(self.todo_pile, 'top')

    # TODO chose which view to show first in cfg file
    self.frame = urwid.AttrWrap(urwid.Frame(self.todo_fill, header=self.header, footer=self.footer_pile), 'body')

    # used by TodoEdit in widgets.py
    self._todo_focus = 0 # focus todo_edit at first place

  def get_todo_focus(self):
    # used by TodoEdit in widgets.py
    return self._todo_focus

  def set_todo_focus(self, i):
    # used by TodoEdit in widgets.py
    self._todo_focus = i


  def run(self):
    self.todo = Todo(app=self)
    self.summary = Summary(app=self, dirname=self.dist)
    self.header.set_text(self.summary.filepath)
    self.loop.run()

  def display(self, something):
    self.txt.set_text("Display: " + str(something))

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

    self.display(target.key_buf) 
    # 2. Handle
    if key == 'esc':
      pass
    elif key == 'tab':
      pass
    elif key == 'enter':
      command = target.key_buf[:-1] # pop the 'enter' key
      target.key_buf = []
      self.display(command)

      if last(2, command) == ':q': 
        raise urwid.ExitMainLoop()

      if last(2, command) == ':w': 
        self.display("saving " + t)
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

  def set_alarm(self, mins=None):
    if not mins:
      sec = 25 * 60
    else:
      sec = mins * 60

    logger = logging.getLogger('tosu')

    # starting sound effect & notification
    # the dict is passed into callback: self.alarm
    play_sound('scifi_start.wav')
    if self._nc:
      self._nc.notify('A task [name] has started', title='todo-summary')

    self._m1 = sec * 1 /3 
    self._m2 = sec * 2 /3 
    self._timer_handle = self.loop.set_alarm_in(0, self.timer, sec)

    # TODO 
    # 5. Add time, minuste time, move to next task 

  def remove_clock_alarm(self):
    self.footer.set_text("Timer stopped.")
    self.loop.remove_alarm(self._timer_handle)
    self._timer_handle = None

  def clock_tick(self, time_left):
    # refresh display
    self.display( str(datetime.timedelta(seconds=time_left))[2:] )

  def timer(self, loop, sec):
    # count down timer, it is a callback.
    # When called, it will register itself to be called after 1 sec.
    if sec == 0:
      self.clock_tick(sec)


      self._timer_handle = None

      if not self._break:
        # Start break timer
        if self._nc:
          self._nc.notify('Time to break', title='todo-summary')
        # TODO make sound in cfg
        play_sound('horn.wav')
        self.footer.set_text("Coffee time...")

        self._m1 = None
        self._m2 = None
        self._break = True
        self._timer_handle = self.loop.set_alarm_in(1, self.timer,  10) 
      else:
        # break stop
        # TODO play a sound
        self._break = False
        if self._nc:
          self._nc.notify('Break done', title='todo-summary')

      logger = logging.getLogger('tosu')
      logger.debug('timer exit')
      return
    else:
      self.clock_tick(sec)

      # TODO make sound in cfg
      if sec == self._m1 or sec == self._m2:
        play_sound('paper.wav')

      logger = logging.getLogger('tosu')
      logger.debug('timer')
      # save handle for the newly set alarm in app
      self._timer_handle = self.loop.set_alarm_in(1, self.timer,  sec-1) 

# End of App
def main():
  app = App()
  app.run()

if __name__ == '__main__':
  main()

