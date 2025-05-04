from time import sleep
import threading

def loading(c):
    c.toggleLock(True)
    for i in range(3):
        c.screenMessage.set("Processing" + (i + 1) * ".")
        sleep(0.2)
    c.toggleLock(False)


def blink(c, text):
    c.toggleLock(True)
    for _ in range(3):
        c.screenMessage.set(str(text))
        sleep(0.3)
        c.screenMessage.set("")
        sleep(0.2)
    c.screenMessage.set(text)
    c.toggleLock(False)
    
def typerwriter(c, messages):
  def startType():
    c.screenMessage.set("")
    c.toggleLock(True)
    for message in messages:
      for char in message:
        c.screenMessage.set(c.screenMessage.get() + char)
        sleep(0.08)
      if len(messages) > 0: sleep(1)
      c.screenMessage.set("")
    blink(c, messages[-1])
    sleep(1)
    c.screenMessage.set("Enter Item Code")
    c.toggleLock(False)
  threading.Thread(target=startType).start()