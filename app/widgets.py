import urwid
import time
from urwid.util import move_next_char
from urwid.widget import LEFT, SPACE

# Vi mode Edit box
class ViEdit(urwid.Edit):
  CMD_MODE = 0
  INPUT_MODE = 1

  def __init__(self, caption=u"", edit_text=u"", multiline=False,
          align=LEFT, wrap=SPACE, allow_tab=False,
          edit_pos=None, layout=None, mask=None, 
          app=None, timeout=0.7, last_press=598233600,
          mode=CMD_MODE):

    # additional stuff 
    self.mode = mode 
    self.timeout = timeout
    self.last_press = last_press
    self.key_buf = []
    self._app = app
    super(ViEdit, self).__init__(caption, edit_text, multiline,
           align, wrap, allow_tab,
           edit_pos, layout, mask)

    self.origin_keypress = self.keypress

    if mode == ViEdit.CMD_MODE:
      self.keypress = self.cmd_keypress
    else:
      self.mode = ViEdit.INPUT_MODE
      self._app.footer.set_text('-- INSERT --')
      self._app.txt.set_text('INSERT')

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
    self._app.txt.set_text(self.key_buf[-10:])

    # Step 2.
    if key == 'i':
      self.mode = ViEdit.INPUT_MODE

      self._app.footer.set_text('-- INSERT --')
      self._app.txt.set_text('INSERT')

      # key control shift
      self.keypress = self.origin_keypress

    elif key == 'esc':
      # in cmd mode just clear key buffer
      self._app.txt.set_text('')
      self._app.footer.set_text('')
      self.key_buf = []

    elif key == 'k':
      # up 
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0], pos[1] - 1)

    elif key == 'j':
      # down 
      pos = self.get_cursor_coords(size)
      self.move_cursor_to_coords(size, pos[0], pos[1] + 1)

    elif key == 'h':
      # left 
        pos = self.get_cursor_coords(size)
        self.move_cursor_to_coords(size, pos[0] - 1, pos[1])

    elif key == 'l':
      # right 
        pos = self.get_cursor_coords(size)
        self.move_cursor_to_coords(size, pos[0] + 1, pos[1])

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
      # clear buffer
      self.key_buf = []
      self.mode = ViEdit.CMD_MODE
      self._app.footer.set_text(u'')
      # key control shift
      self.origin_keypress = self.keypress
      self.keypress = self.cmd_keypress
    else:
      return super(ViEdit, self).keypress(size, key) 

class TodoPile(urwid.Pile):

  def __init__(self, widget_list, focus_item=None, app=None):
    self._app = app
    super(TodoPile, self).__init__(widget_list, focus_item)

 # def keypress(self, size, key):
 #   self._app.debug("heehhheee")
 #   if key == 'k':
 #     self._app.debug("heeeee")
 #     fo = self._app.todo_pile.focus_position - 1
 #     #self._app.debug(fo + 1)
 #     self._app.todo_pile.set_focus(fo)
 #     urwid.AttrMap(self._app.todo_pile.get_focus(), 'select')
 #   elif key == 'j':
 #     self._app.debug("heeeee")
 #     fo = self._app.todo_pile.focus_position + 1
 #     #self._app.debug(fo - 1)
 #     self._app.todo_pile.set_focus(fo)
 #     urwid.AttrMap(self._app.todo_pile.get_focus(), 'select')
 #   else:
 #     return key

class TodoEdit(ViEdit):
  def cmd_keypress(self, size, key):
    if key == 'k':
      fo = self._app._todo_focus
      self._app._todo_focus -= 1
      fo -= fo
      self._app.debug(fo + 1)
      if fo > 0:
        self._app.todo_pile.set_focus(fo)
        w = self._app.todo_pile.get_focus()
        urwid.AttrWrap(w, 'body', 'select')
        w.set_text( "---" + str(w.get_text()) + " ---")
        self._app.todo_pile.set_focus(0)
    elif key == 'j':
      fo = self._app._todo_focus
      self._app._todo_focus += 1
      fo += fo
      self._app.debug(fo - 1)
      if fo <= len(self._app.todo_pile.widget_list) and fo > 0:
        self._app.todo_pile.set_focus(fo)
        w = self._app.todo_pile.get_focus()
        urwid.AttrWrap(w, 'body', 'select')
        w.set_text( "---" + str(w.get_text()) + " ---")
        self._app.todo_pile.set_focus(0)
    else:
      return super(TodoEdit, self).cmd_keypress(size, key) 

  def keypress(self, size, key):
    if key == 'enter':
      new_item = TodoItem(" * " + self.edit_text)
      self._app.todos.insert(1, new_item)

      self._app.todo_pile = urwid.Pile(self._app.todos)
      self._app.todo_fill = urwid.Filler(self._app.todo_pile, 'top')
      self._app.frame.set_body(self._app.todo_fill)
    elif key == 'shift enter':
      self.insert_text(u'\n')
    else:
      return super(TodoEdit, self).keypress(size, key) 

class TodoItem(urwid.Text):
  def selectable(self):
    return True

  def keypress(self, size, key):
    return key


