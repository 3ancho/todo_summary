# when using py2app, this includes a lot of packages
import time
import urwid 
import summary

from urwid.util import move_next_char


# util functions 
def last(n, li):
  # take a list return a string
  if n > 0 and n <= len(li):
    return ''.join(li[-1*n:])
  else:
    return ''

class App:
  CMD_MODE = 0
  INPUT_MODE = 1

  def __init__(self):
    palette = [ ('header', 'black', 'light gray'),
                ('body', 'black', 'dark red'),
                ('footer', 'black', 'dark blue'),]

    # summary
    self.summary = None

    # init sound, register alerm

    # reusable widges
    self.divider = urwid.Divider(u"-");

    # widgets
    header_text = "Summary" 

    self.header = urwid.Text("Editing: %s\n" % header_text)

    self.content = urwid.Edit(u"Content:\n", multiline=True)

    self.tag = urwid.Edit(u"Tags:\n")

    self.footer = urwid.Text(u"-- INSERT --")

    self.txt = urwid.Text(u"-- INSERT --") # debug

    self.pile = urwid.Pile([ self.tag, self.divider, self.content, self.divider, self.txt])
    self.fill = urwid.Filler(self.pile, 'top')

    self.frame = urwid.Frame(self.fill, header=self.header, footer=self.footer)

    # UI block focus, mode
    self.tag_focused = True
    self.pre_focus = 0
    self.mode = App.INPUT_MODE

    # key press 
    self.pres_thres = 0.7
    self.last_press = 598233600
    self.key_buf = []

    # set main loop
    self.loop = urwid.MainLoop(self.frame, unhandled_input=self.insert_keypress_handler)

    self.good = False

    self.old = urwid.Edit.keypress 

    self._content_line_count = 0
    
  def run(self):
    self.summary = summary.Summary(app=self)
    self.header.set_text(self.summary.filepath)
    self.loop.run()

  def change_cmd_mode(self):
    if self.mode == App.INPUT_MODE:
      self.mode = App.CMD_MODE
      self.pre_focus = self.pile.focus_position
      #self.pile.set_focus(3)

  def cmd_keypress_handler(self, size, key):

    # Step 1.
    # timeout 
    if time.time() - self.last_press > self.pres_thres:
      self.key_buf = []
      self.key_buf.append(key)
      self.last_press = time.time()

    else:
      self.key_buf.append(key)
      self.last_press = time.time()

    # print key pressed in mode bar
    self.txt.set_text(self.key_buf[-10:])

    # Step 2.
    if key == 'i':
      self.mode = App.INPUT_MODE
      self.pile.set_focus(self.pre_focus)
      self.footer.set_text('-- INSERT --')
      self.txt.set_text('-- INSERT --')
      # key control shift
      self.tag.keypress = self.tag.old
      self.content.keypress = self.content.old

    elif key == 'tab':
      if (self.tag_focused):
        self.pile.set_focus(2)
        self.tag_focused = False
        self.pre_focus = 2
      else:
        self.pile.set_focus(0)
        self.tag_focused = True
        self.pre_focus = 0

    elif key == 'esc':
      # in cmd mode just clear key buffer
      self.txt.set_text('')
      self.footer.set_text('')
      self.key_buf = []

    elif key == 'k':
      # up 
      if self.pile.focus_position == 0: # in tag 
        pos = self.tag.get_cursor_coords(size)
        self.tag.move_cursor_to_coords(size, pos[0], pos[1] - 1)
      else: # in content
        pos = self.content.get_cursor_coords(size)
        self.content.move_cursor_to_coords(size, pos[0], pos[1] - 1)

    elif key == 'j':
      # down 
      if self.pile.focus_position == 0: # in tag 
        pos = self.tag.get_cursor_coords(size)
        self.tag.move_cursor_to_coords(size, pos[0], pos[1] + 1)
      else: # in content
        pos = self.content.get_cursor_coords(size)
        self.content.move_cursor_to_coords(size, pos[0], pos[1] + 1)

    elif key == 'h':
      # left 
      if self.pile.focus_position == 0: # in tag 
        pos = self.tag.get_cursor_coords(size)
        self.tag.move_cursor_to_coords(size, pos[0] - 1, pos[1])
      else: # in content
        pos = self.content.get_cursor_coords(size)
        self.content.move_cursor_to_coords(size, pos[0] - 1, pos[1])

    elif key == 'l':
      # right 
      if self.pile.focus_position == 0: # in tag 
        pos = self.tag.get_cursor_coords(size)
        self.tag.move_cursor_to_coords(size, pos[0] + 1, pos[1])
      else: # in content
        pos = self.content.get_cursor_coords(size)
        self.content.move_cursor_to_coords(size, pos[0] + 1, pos[1])

    elif key == '$':
      if self.pile.focus_position == 0: # in tag 
        pos = self.tag.get_cursor_coords(size)
        x_pos = pos[0] + 1
        self.tag.move_cursor_to_coords(size, x_pos, pos[1])

        while x_pos == self.tag.get_cursor_coords(size)[0]:
          x_pos = x_pos + 1
          self.tag.move_cursor_to_coords(size, x_pos, pos[1])

      else: # in content
        pos = self.content.get_cursor_coords(size)
        x_pos = pos[0] + 1
        self.content.move_cursor_to_coords(size, x_pos, pos[1])

        while x_pos == self.content.get_cursor_coords(size)[0]:
          x_pos = x_pos + 1
          self.content.move_cursor_to_coords(size, x_pos, pos[1])

    elif key == '^' or key == '0':
      if self.pile.focus_position == 0: # in tag 
        pos = self.tag.get_cursor_coords(size)
        self.tag.move_cursor_to_coords(size, 0, pos[1])
      else: # in content
        pos = self.content.get_cursor_coords(size)
        self.content.move_cursor_to_coords(size, 0, pos[1])

    elif key == 'G' :
      if self.pile.focus_position == 0: # in tag 
        pos = self.tag.get_cursor_coords(size)
        flag = self.tag.move_cursor_to_coords(size, 0, 1)

      else: # in content
        pos = self.content.get_cursor_coords(size)
        y_pos = pos[1] + 1
        self.txt.set_text(str(self.content.position_coords(10, 0)))
        flag = self.content.move_cursor_to_coords(size, 0, self._content_line_count)

    elif key == 'g' and len(self.key_buf) > 1 and self.key_buf[-2] == 'g':
      if self.pile.focus_position == 0: # in tag 
        self.tag.move_cursor_to_coords(size, 0, 1)
      else: # in content
        self.content.move_cursor_to_coords(size, 0, 1)

    elif key == 'x':
      if self.pile.focus_position == 0: # in tag 
        p = self.tag.edit_pos
        if p >= len(self.tag.edit_text):
          return key
        p = move_next_char(self.tag.edit_text, p, len(self.tag.edit_text))
        self.tag.set_edit_text( self.tag.edit_text[:self.tag.edit_pos] 
            + self.tag.edit_text[p:] )

      else: # in content
        p = self.content.edit_pos
        if p >= len(self.content.edit_text):
          return key
        p = move_next_char(self.content.edit_text, p, len(self.content.edit_text))
        self.content.set_edit_text( self.content.edit_text[:self.content.edit_pos] 
            + self.content.edit_text[p:] )

    # end of single key press handler 

    # Step 3
    # combinations
    elif key == 'enter':
      command = self.key_buf[:-1] # pop the 'enter' key
      self.key_buf = []

      if last(2, command) == ':q': 
        raise urwid.ExitMainLoop()

      if last(2, command) == ':w': 
        self.update_summary()
        self.save_summary()

      if last(2, command) == ':x' or last(3, command) ==  ':wq': 
        self.update_summary()
        self.save_summary()
        time.sleep(0.2) # flash the message 
        raise urwid.ExitMainLoop()


  def insert_keypress_handler(self, key):
    if key == 'esc': # 1. Change mode

      # clear buffer
      self.txt.set_text('')
      self.footer.set_text('')
      self.key_buf = []

      self.mode = App.CMD_MODE
      self.pre_focus = self.pile.focus_position
      self.frame.set_focus('body')

      # key control shift
      self.tag.old = self.tag.keypress
      self.tag.keypress = self.cmd_keypress_handler

      self.content.old = self.content.keypress
      self.content.keypress = self.cmd_keypress_handler

    elif key == 'tab':
      if (self.tag_focused):
        self.pile.set_focus(2)
        self.tag_focused = False
      else:
        self.pile.set_focus(0)
        self.tag_focused = True

  def update_summary(self):
    self.summary.set_tag( self.tag.get_edit_text() )
    self.summary.set_content( self.content.get_edit_text() )

  def save_summary(self):
    filepath = self.summary.save_md()
    self.footer.set_text('Saved to: %s' % filepath)

# End of App

def main():
  app = App()
  app.run()

if __name__ == '__main__':
  main()

