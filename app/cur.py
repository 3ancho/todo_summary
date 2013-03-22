# when using py2app, this includes a lot of packages
import pygame.mixer as sound_player
import time

import urwid 
import summary


#class MyEdit(urwid.Edit):
#
#  def hello():
#    print "hello"
#
#  def keypress(self, size, key):
#    super(MyEdit, self).keypress(size, key)

class App:
  CMD_MODE = 0
  INPUT_MODE = 1

  def __init__(self):
#    palette = [ ('header', 'black', 'light gray'),
#                ('body', 'black', 'dark red'),
#                ('bg', 'black', 'dark blue'),]

    # summary
    self.summary = None
    # init sound, register alerm
    sound_player.init()
    self.alarm = sound_player.Sound("thermo.wav")

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
    self.pres_thres = 0.8
    self.last_press = 598233600
    self.key_buf = []

    # set main loop
    self.loop = urwid.MainLoop(self.frame, unhandled_input=self.insert_keypress_handler)

    self.good = False

    self.old = urwid.Edit.keypress 
    
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
    # timeout 
    if time.time() - self.last_press > self.pres_thres:
      self.key_buf = []
      self.key_buf.append(key)
      self.last_press = time.time()

    else:
      self.key_buf.append(key)
      self.last_press = time.time()


    # print key pressed
    self.txt.set_text(str(self.key_buf))

    if key == 'i':
      self.mode = App.INPUT_MODE
      self.pile.set_focus(self.pre_focus)
      self.footer.set_text('-- INSERT --')
      self.txt.set_text('-- INSERT --')
      # key control shift
      self.tag.keypress = self.tag.old
      self.content.keypress = self.content.old

    elif key == 'esc':
      # in cmd mode just clear key buffer
      self.txt.set_text('')
      self.footer.set_text('')
      self.key_buf = []

    # single key
    #if key == 'i':
    #  self.mode = App.INPUT_MODE
    #  self.pile.set_focus(self.pre_focus)
    #  self.footer.set_text('-- INSERT --')
    #  self.txt.set_text('-- INSERT --')

    # combinations
    if key == 'enter':
      command = "".join(self.key_buf)
      self.key_buf = []
      self.txt.set_text(command)

      if command == ':qenter': 
        raise urwid.ExitMainLoop()

      if command == ':wenter': 
        self.update_summary()
        self.save_summary()

      if command in (':xenter', ':wqenter'): 
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

