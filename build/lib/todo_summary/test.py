import urwid
import random
import urwid.html_fragment

class ItemWidget (urwid.WidgetWrap):

    def __init__ (self, id, description):
        self.id = id
        self.title = urwid.Text('item %s' % str(id))
        self.description = urwid.Text(description)
        self.item = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap( self.title, 'body', 'focus'), left=2)),
            urwid.AttrWrap(self.description, 'body', 'focus'),
        ]
        self.content = 'item %s: %s...' % (str(id), description[:25])
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class CustomEdit(urwid.Edit):

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'done', self.get_edit_text())
            return
        elif key == 'esc':
            urwid.emit_signal(self, 'done', None)
            return

        urwid.Edit.keypress(self, size, key)

class MyApp(object):

    def __init__(self):

        palette = [
            ('body','dark blue', '', 'standout'),
            ('focus','dark red', '', 'standout'),
            ('head','light red', 'black'),
            ]

        lorem = [
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'Sed sollicitudin, nulla id viverra pulvinar.',
            'Cras a magna sit amet felis fringilla lobortis.',
        ]


        items = []
        for i in range(100):
            item = ItemWidget(i, random.choice(lorem))
            items.append(item)

        header = urwid.AttrMap(urwid.Text('selected:'), 'head')
        walker = urwid.SimpleListWalker(items)
        self.listbox = urwid.ListBox(walker)
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), header=header)

        loop = urwid.MainLoop(self.view, palette, unhandled_input=self.keystroke)
        urwid.connect_signal(walker, 'modified', self.update)
        loop.run()
    
    def update(self):
        focus = self.listbox.get_focus()[0].content
        self.view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'head'))

    def keystroke (self, input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        if input is 'enter':
            focus = self.listbox.get_focus()[0].content
            self.view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'head'))

        if input == 'e':
            self.edit()

    def edit(self):
        self.foot = CustomEdit(' >> ')
        self.view.set_footer(self.foot)
        self.view.set_focus('footer')
        urwid.connect_signal(self.foot, 'done', self.edit_done)

    def edit_done(self, content):
        self.view.set_focus('body')
        urwid.disconnect_signal(self, self.foot, 'done', self.edit_done)
        if content:
            focus = self.listbox.get_focus()[0]
            focus.description.set_text(content)
        self.view.set_footer(None)

if __name__ == '__main__':
    MyApp()
