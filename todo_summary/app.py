# -*- coding: utf-8 -*- 

# when using py2app, this includes a lot of packages
import os
import sys
import time
import urwid 
import pickle
import logging
import datetime
import ConfigParser

from sys import platform
from threading import Timer

from todo import Todo
from widgets import ViEdit
from widgets import TodoEdit
from widgets import TodoItem
from sound import play_sound
from notifier import OSXNotifier, UbuntuNotifier

# static util functions
def last(n, li):
  # take a list return a string
  if n > 0 and n <= len(li):
    return ''.join(li[-1*n:])
  else:
    return ''

class MyUnpickler(pickle.Unpickler): 
  def find_class(self, module, name):
    if module == 'todo' and name == 'Todo':
      return Todo 
    else:
      return pickle.Unpickler.find_class(self, module, name)

class App:
  def __init__(self, dir='./', work_mins=25, rest_mins=5):
    """default config file directory is current directory
       work time 25 min
       rest time 5 min
    """
    self._dir = dir
    self._work_mins = work_mins
    self._rest_mins = rest_mins

    # Two Models App deals with
    self.todos = None
    self.summary = None

    # platform dependeny notifier
    if platform == 'darwin':
      self._nc = OSXNotifier() 
    elif platform == 'linux2':
      self._nc = UbuntuNotifier()
    else:
      self._nc = None

    self.init_ui()

    # ui style 
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

  def init_logger(self):
    # init logger
    # TODO get name, instead of hardcode
    logger = logging.getLogger('tosu')
    # TODO path should be defined in cfg file
    hdlr = logging.FileHandler('./tosu.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)

    logger.debug('init ok')

  def init_models(self):
    pass

  def init_ui(self):
    # reusable widges
    self.divider = urwid.Divider(u'-');

    # header 
    header_text = u'Summary' 
    self.header = urwid.AttrWrap(urwid.Text(u'Editing: %s\n' % header_text), 'header')

    # footer_pile = footer + txt
    self.footer = urwid.Text(u'')
    self.txt = urwid.Text(u'') # display
    self.footer_pile = urwid.AttrWrap(urwid.Pile( [self.txt, self.footer] ), 'footer')

    # Summary
    # summary_fill can be frame.body, option 1
    # This will be created when first typed command ':s'

    # Todos 
    # todo_fill can be frame.body, option 2
    self.todos = []
    self.todos_view = []

    # mode = 1, insert mode TODO costomize mode
    self.todo_edit = TodoEdit(caption=u'Todo:\n>>> ', multiline=False, mode=1, app=self)
    # TODO change this pile, need to change many parts
    self.todos_view.append(self.todo_edit)

    # Only todo data stored in pickle TODO move it
    self._pickle_file = os.path.join(self._dir, 'tosu_data.pickle')

    # if data available
    if os.path.exists(self._pickle_file):
      self.todos = MyUnpickler(open(self._pickle_file)).load() 

    # TODO why reverse?
    for obj in reversed(self.todos):
      # show undone todo item 
      if obj._done == False:
        # create view for each todo instance
        new_view_item = urwid.AttrWrap(TodoItem(str(obj), data=obj), 'body')
        self.todos_view.append(new_view_item)

    """ todos_view 
        1. todo_edit widget
        2. todo_item
        3. todo_item
        .
        .
        .
    """
    self.todo_pile = urwid.Pile(self.todos_view, focus_item=0)
    self.todo_fill = urwid.Filler(self.todo_pile, 'top')

    # TODO chose which view to show first in cfg file, now show todo by default
    self.frame = urwid.AttrWrap(urwid.Frame(self.todo_fill, header=self.header, footer=self.footer_pile), 'body')

    # used by TodoEdit in widgets.py
    self._todo_focus = 0 # focus todo_edit at first place

  def get_todo_focus(self):
    # used by TodoEdit in widgets.py
    # TODO this is same as todos_view.focus
    return self._todo_focus

  def set_todo_focus(self, i):
    # used by TodoEdit in widgets.py
    # TODO this is same as todos_view.focus
    self._todo_focus = i

  def run(self):
    self.todo = Todo(app=self, dirname=self._dir)
    self.header.set_text(self.todo.md_filepath) # TODO change this title
    self.loop.run()

  def display(self, something):
    self.txt.set_text(u'Display: ' + str(something))

  def app_keypress(self, key):
    # 1. Check Body = ?
    if self.frame.get_body() == self.todo_fill:
      target = self.todo_edit
      target_label = 'todo'
    elif self.frame.get_body() == self.summary_fill:
      target = self.summary_pile.focus_item
      target_label= 'summary'
    else:
      return

    if target == None:
      return key

    # 2. Handle
    if key == 'esc':
      pass
    elif key == 'tab' and target_label== 'summary':
      # tab only works in summary mode
      cur = self.summary_pile.focus_position
      summary_pile_len = len(self.summary_pile.widget_list)

      if cur == summary_pile_len - 1:
        self.summary_pile.focus_position = 0
      else:
        self.summary_pile.focus_position = cur + 1

    elif key == 'enter':
      command = target.key_buf[:-1] # pop the 'enter' key
      target.key_buf = []
      # self.display(command)

      if last(2, command) == ':q': 
        raise urwid.ExitMainLoop()

      if last(2, command) == ':w': 
        self.update(target_label)
        self.save(target_label)

      if last(2, command) == ':x' or last(3, command) ==  ':wq': 
        self.update(target_label)
        self.save(target_label)
        time.sleep(0.2) # flash the message 
        raise urwid.ExitMainLoop()

      if last(3, command) == ':to' or last(2, command) == ':t':
        self.update(target_label)
        self.save(target_label)
        self.frame.set_body(self.todo_fill)
        self.todo_edit.keypress = self.todo_edit.cmd_keypress

      if last(3, command) == ':su' or last(2, command) == ':s':
        self.update(target_label)
        self.save(target_label)

        summary_list = []

        for todo_obj in self.todos:
          # Generate Summary views
          if todo_obj._done:  
            # TODO load existing summary
            summary_list.append(ViEdit("* " + todo_obj.content + '\n', multiline=True, app=self, todo=todo_obj))
        if len(summary_list) == 0:
          return

        self.summary_pile = urwid.Pile(summary_list)
        self.summary_fill = urwid.Filler(self.summary_pile, 'top')
        self.frame.set_body(self.summary_fill)
        #self.summary_edit.keypress = self.summary_edit.cmd_keypress
    # End elif 'enter'
  # End func

  def update(self, target_label=None):
    if target_label== None:
      return
    elif target_label== 'summary':
      for summary_view in self.summary_pile.widget_list:
        if summary_view.todo:
          summary_view.todo._summary = summary_view.edit_text
    elif target_label== 'todo':
      pass

  def save(self, target_label=None):
    if target_label== None:
      return
    elif target_label== 'summary':
      f = open("test.json", 'w')
      f.write("\n{[")
      f.write("\n".join([ su.todo.to_json() for su in self.summary_pile.widget_list if su.todo]))
      f.write("\n]}")
      f.close()

#      msg = self.summary.save_md()
#      self.footer.set_text(u'Summary saved to: %s' % msg)
      
    elif target_label== 'todo':
      self.footer.set_text(u'todo saved')

#      for item in self.todos:
#        item.view = None

      # TODO backup 
      pickle.dump(self.todos, open(self._pickle_file, 'wb'))

  def set_alarm(self):
    # Read mins from config file
    if not self._work_mins:
      sec = 25 * 60
    else:
      sec = self._work_mins * 60

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
    self.footer.set_text(u'Timer stopped.')
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
        cur = self.get_todo_focus()
        if cur != 0:
          view = self.todo_pile.widget_list[cur]
          view.update_time()

        if self._nc:
          self._nc.notify('Time to break', title='todo-summary')
        # TODO make sound in cfg
        play_sound('horn.wav')
        self.footer.set_text('Coffee time...')

        self._m1 = None
        self._m2 = None
        self._break = True
        # Start break timer
        self._timer_handle = self.loop.set_alarm_in(1, self.timer, self._rest_mins * 60) 
      else:
        # break stop
        # TODO play a different sound
        self._break = False
        if self._nc:
          self._nc.notify('Break done', title='todo-summary')
        play_sound('paper.wav')

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
  config = ConfigParser.ConfigParser()
  config_file = os.path.expanduser('~/.tosuconf')

  # Default values
  dir = os.path.expanduser('~/Desktop')
  work_mins = 25
  rest_mins = 5

  # if config file exists, we might override default values
  if os.path.exists(config_file):
    config.read(config_file)
    try:
      temp_dir = config.get('tosu', 'dir')
      if os.path.isdir(temp_dir):
        dir = temp_dir
      work_mins = config.getint('tosu', 'work_mins')
      rest_mins = config.getint('tosu', 'rest_mins')
    except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
      pass
      #print 'using default'

  app = App(dir, work_mins, rest_mins)
  app.run()

if __name__ == '__main__':
  main()

