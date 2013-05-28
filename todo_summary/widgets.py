# -*- coding: utf-8 -*- 

import urwid
import logging
import time
from urwid.util import move_next_char
from urwid.widget import LEFT, SPACE

from todo import Todo

# Vi mode Edit box
class ViEdit(urwid.Edit):
  CMD_MODE = 0
  INPUT_MODE = 1

  def __init__(self, caption=u'', edit_text=u'', multiline=False,
          align=LEFT, wrap=SPACE, allow_tab=False,
          edit_pos=None, layout=None, mask=None, 
          app=None, timeout=0.7, last_press=598233600,
          mode=CMD_MODE):

    # additional stuff 
    self.mode = mode 
    self.timeout = timeout
    self.last_press = last_press
    self.key_buf = []
    self.j_pressed = last_press 
    self._app = app
    super(ViEdit, self).__init__(caption, edit_text, multiline,
           align, wrap, allow_tab,
           edit_pos, layout, mask)

    self.origin_keypress = self.keypress

    if mode == ViEdit.CMD_MODE:
      self.keypress = self.cmd_keypress
    else:
      self.mode = ViEdit.INPUT_MODE
      self._app.footer.set_text(u'-- INSERT --')

  def get_app(self):
    return self._app

  def cmd_keypress(self, size, key):
    # Step 1.
    # timeout 
    if time.time() - self.last_press > self.timeout:
      self.key_buf = []
      self.key_buf.append(key)
      self.last_press = time.time()

    else:
      self.key_buf.append(key)
      self.last_press = time.time()

    # print key pressed in mode bar
    # self._app.display(self.key_buf[-10:])

    # Step 2.
    if key == 'i':
      self.mode = ViEdit.INPUT_MODE
      self._app.footer.set_text(u'-- INSERT --')
      # key control shift
      self.keypress = self.origin_keypress

    elif key == 'a':
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0] + 1, pos[1])
      self.mode = ViEdit.INPUT_MODE
      self._app.footer.set_text(u'-- INSERT --')
      # key control shift
      self.keypress = self.origin_keypress

    elif key == 'esc':
      # in cmd mode just clear key buffer
      self._app.display(u'')
      self._app.footer.set_text(u'')
      self.key_buf = []

    elif key == 'k' or key == 'up':
      # up 
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0], pos[1] - 1)

    elif key == 'j' or key == 'down':
      # down 
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0], pos[1] + 1)

    elif key == 'h' or key == 'left':
      # left 
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0] - 1, pos[1])

    elif key == 'l' or key == 'right':
      # right 
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0] + 1, pos[1])

    elif key == 'w':
      pass

    elif key == 'b':
      pass

    elif key == '$':
        pos = self.get_cursor_coords(size)
        x_pos = pos[0] + 1
        self.move_cursor_to_coords(size, x_pos, pos[1])

        while x_pos == self.get_cursor_coords(size)[0]:
          x_pos = x_pos + 1
          self.move_cursor_to_coords(size, x_pos, pos[1])

    elif key == '^' or key == '0':
        pos = self.get_cursor_coords(size)
        self.move_cursor_to_coords(size, 0, pos[1])

    elif key == 'G' :
        pos = self.get_cursor_coords(size)
        y_pos = pos[1] + 1
        self.move_cursor_to_coords(size, 0, y_pos)

        while y_pos == self.get_cursor_coords(size)[1]:
          y_pos = y_pos + 1
          self.move_cursor_to_coords(size, 0, y_pos)

    elif key == 'g' and len(self.key_buf) > 1 and self.key_buf[-2] == 'g':
        self.move_cursor_to_coords(size, 0, 1)

    elif key == 'x':
        p = self.edit_pos
        if p >= len(self.edit_text):
          return key
        p = move_next_char(self.edit_text, p, len(self.edit_text))
        self.set_edit_text( self.edit_text[:self.edit_pos] 
            + self.edit_text[p:] )
    else:
      # return key to be handled by mainloop 
      return key

  def keypress(self, size, key):
    
    if key == 'esc': # 1. Change mode
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0] - 1, pos[1])
      # clear buffer
      self.key_buf = []
      self.mode = ViEdit.CMD_MODE
      self._app.footer.set_text(u'')
      # key control shift
      self.origin_keypress = self.keypress
      self.keypress = self.cmd_keypress
    elif key == 'j':
      # jk -> esc -> enter cmd mode 
      self.j_pressed = time.time()
    elif key == 'k':
      # jk -> esc -> enter cmd mode 
      if (time.time() - self.j_pressed) < 0.2:
        self.keypress(size, 'esc')
      else:
        return super(ViEdit, self).keypress(size, key) 
    else:
      return super(ViEdit, self).keypress(size, key) 

class TodoPile(urwid.Pile):
  def __init__(self, widget_list, focus_item=None, app=None):
    self._app = app
    super(TodoPile, self).__init__(widget_list, focus_item)

class TodoEdit(ViEdit):
  FOCUS = 'footer'
  NORMAL = 'body'

  # hook to app.get_todo_focus
  def get_pile_focus(self):
    # int
    return self._app.get_todo_focus()

  # hook to app.set_todo_focus
  def set_pile_focus(self, i):
    # int
    return self._app.set_todo_focus(i)
      
  # change is style of an item is todo_pile when selected
  def set_attr_for(self, i, attr=FOCUS):
    # i int, attr string
    # TODO check bound
    self._app.todo_pile.widget_list[i].set_attr(attr)

  # check bound for function select
  def get_todo_length(self):
    return len(self._app.todo_pile.widget_list)

  def select(self, direction):
    # direction = 1 down, -1 up
    # get cur_focus item
    cur = self.get_pile_focus()
    if cur == 0 and (cur + direction) >= 0 \
        and (cur + direction) < self.get_todo_length():
      cur += direction # update 
      self.set_attr_for(cur) # cur is updated
      self.set_pile_focus(cur) # save this value back to app obj
      self.pre = cur 

    # > 0 is because 0, TodoEdit field, doesn't need highlight
    elif cur !=0 and (cur + direction) > 0 \
        and (cur + direction) < self.get_todo_length():
      self.set_attr_for(self.pre, 'body')
      cur += direction # update 
      self.set_attr_for(cur) # cur is updated
      self.set_pile_focus(cur) # save this value back to app obj
      self.pre = cur 

  def cmd_keypress(self, size, key):
    if key == 'i':
      self._app.footer.set_text(u'-- INSERT --')
      self.keypress = self.origin_keypress
      # added bellow
      if hasattr(self, 'pre'):
        self.set_attr_for(self.pre, 'body')
        self.set_pile_focus(0) # will start from item 1 next time
    elif key == 'esc':
      self._app.display(u'')
      self._app.footer.set_text(u'')
      self.key_buf = []
      # added bellow
      return key
    elif key == 'k':
      self.select(-1) 
    elif key == 'j':
      self.select(1) 
    elif key == 'enter' and not ':' in self.key_buf:
      # toggle alarms.
      if self._app._timer_handle == None:
        # 1. Fresh start
        cur = self.get_pile_focus()
        if cur != 0:
          self._app.footer.set_text(u'Task Started...')
          self._app.set_alarm()
      elif self._app._timer_handle != None:
        # 2. re-start
        self._app.remove_clock_alarm()
        self._app.footer.set_text(u'Task Re-Started...')
        self._app.set_alarm()
      else:
        # TODO 3. pause and resume
        pass
    elif key == ' ' and not ':' in self.key_buf:
      cur = self.get_pile_focus()
      if cur != 0:
        view = self._app.todo_pile.widget_list[cur]
        view.toggle_done()
        # TODO sort todo and done task
       
    elif key == 'backspace' and not ':' in self.key_buf:
      self._app.remove_clock_alarm()
    else:
      return super(TodoEdit, self).cmd_keypress(size, key) 

  def keypress(self, size, key):
    if key == 'enter':
      # Create obj 
      unit = self.edit_text.lstrip().split(u' ')[0]

      if unit.isdigit():
        start_index = self.edit_text.find(unit) + len(unit)
        content = self.edit_text[start_index:].strip()
        unit = int(unit)
      else:
        content = self.edit_text.strip()
        unit = 0

      # TODO Order app.todos and Order views
      todo_obj = Todo(unit, content)
      self._app.todos.append(todo_obj)
        
      # Update UI
      new_view_item = urwid.AttrWrap(TodoItem(str(todo_obj), data=todo_obj), 'body')

      # 0 is the input field
      self._app.todo_pile.widget_list.insert(1, new_view_item)
      self.set_edit_text(u'')

    elif key == 'shift enter':
      self.insert_text(u'\n')
    else:
      return super(TodoEdit, self).keypress(size, key) 

class TodoItem(urwid.Text):
  # TodoItem is a UI widget, that associates with an todo instance
  # self.obj is an instance of todo class. 
  # overwrite
  def __init__(self, markup, align=LEFT, wrap=SPACE, layout=None, data=None):
    # data obj
    if data:
      self.set_obj(data)
    super(TodoItem, self).__init__(markup, align=LEFT, wrap=SPACE, layout=None)

  # TODO make this more usefull.   progress 1/3

  def selectable(self):
    return True
 
  def get_obj(self):
    if hasattr(self, 'obj'):
      return self.obj
    else:
      return None

  def toggle_done(self):
    # this will change data status first and also change UI
    if self.get_obj():
      self.get_obj().toggle_done()
    else:
      return

  def update_time(self):
    self.obj.update_time()
    self._change_mark()

  def _change_mark(self):
    # call chain started from toggle_done, then called from data binded
    self.set_text(str(self.obj))

  def set_obj(self, obj):
    self.obj = obj
    obj.view = self

  def keypress(self, size, key):
    return key


