class BaseNotifier(object):
  """docstring for BaseNotifier"""
  def __init__(self, title):
    super(BaseNotifier, self).__init__()

  def notify(self, message, title):
    pass

class OSXNotifier(BaseNotifier):
  def __init__(self, title=u''):
    super(OSXNotifier, self).__init__(title)
    from pync import Notifier
    self._nc = Notifier

  def notify(self, message, title):
    self._nc.notify(message, title=title)

class UbuntuNotifier(BaseNotifier):
  def __init__(self, title=u''):
    super(UbuntuNotifier, self).__init__(title)
    import pynotify
    pynotify.init(u'tosu')
    self._nc = pynotify.Notification('')

  def notify(self, message, title=None):
    self._nc.update(message)
    self._nc.show()
