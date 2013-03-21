# when using py2app, this includes a lot of packages
import pygame.mixer as sound_player
import time

import urwid 
import summary

class App:
  CMD_MODE = 0
  INPUT_MODE = 1

  def __init__(self):
#    palette = [ ('header', 'black', 'light gray'),
#                ('body', 'black', 'dark red'),
#                ('bg', 'black', 'dark blue'),]

    # init sound, register alerm
    sound_player.init()
    self.alarm = sound_player.Sound("thermo.wav")

    # reusable widges
    self.divider = urwid.Divider(u"-");

    # widgets
    header_text = "Summary" # summary.Summary.bootstrap() # TODO change this

    self.header = urwid.Text("Editing: %s\n" % header_text)

    self.content = urwid.Edit(u"Content:\n", multiline=True)

    self.tag = urwid.Edit(u"Tags:\n")

    self.footer = urwid.Text(u"display")

    self.txt = urwid.Text(u"display") # debug

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
    self.loop = urwid.MainLoop(self.frame, unhandled_input=self.keypress_handler)


  def run(self):
    self.loop.run()

  def change_cmd_mode(self):
    #if self.mode == App.CMD_MODE:
    #  self.mode = App.INPUT_MODE
    #  self.pile.set_focus(self.pre_focus)
    #  self.footer.set_text("input mode")
    if self.mode == App.INPUT_MODE:
      self.mode = App.CMD_MODE
      self.pre_focus = self.pile.focus_position
      self.pile.set_focus(3)
      self.footer.set_text("cmd mode %s" % self.pre_focus)
      self.key_buf = []
      self.txt.set_text("")

  def keypress_handler(self, key):

    if time.time() - self.last_press > self.pres_thres:
      self.key_buf = []
      self.key_buf.append(key)
      self.last_press = time.time()
    else:
      self.key_buf.append(key)
      self.last_press = time.time()

    # 1. Change mode
    if key == 'esc':
      self.change_cmd_mode()

    # input mode
    elif self.mode == App.INPUT_MODE:
      if key == 'tab':
        self.footer.set_text(" %s  " % self.pile.focus_position)
        if (self.tag_focused):
          self.pile.set_focus(2)
          self.tag_focused = False
        else:
          self.pile.set_focus(0)
          self.tag_focused = True
    # command mode
    elif self.mode == App.CMD_MODE:
      self.txt.set_text(str(self.key_buf))

      # single key
      if key == 'i':
        self.mode = App.INPUT_MODE
        self.pile.set_focus(self.pre_focus)
        self.footer.set_text('input mode')

      # combinations
      if key == 'enter':
        command = "".join(self.key_buf)
        self.key_buf = []
        self.txt.set_text(command)

        if command == ':qenter': 
          raise urwid.ExitMainLoop()

        if command == ':wenter': 
          tag = self.tag.get_edit_text()
          content =self.content.get_edit_text()
          self.footer.set_text('Saved to: %s' % summary.Summary.bootstrap(tag, content))

        if command in (':xenter', ':wqenter'): 
          tag = self.tag.get_edit_text()
          content =self.content.get_edit_text()
          self.footer.set_text('Saved to: %s' % summary.Summary.bootstrap(tag, content))
          time.sleep(0.4)
          raise urwid.ExitMainLoop()
          

        if command == ':senter': 
          self.alarm.play()
          self.footer.set_text('Saved to: %s' % summary.Summary.bootstrap())

        

      #if key in ('esc'):
      #  if (self.footer_focused):
      #    self.footer_focused = False
      #  else:
      #    self.pile.set_focus(1)
      #    self.footer_focused = True


def main():
  app = App()
  app.run()

if __name__ == '__main__':
  main()

