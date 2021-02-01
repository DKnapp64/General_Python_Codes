import threading

def test_timer():
  t = threading.Timer(15.0, test_timer)
  t.daemon = True
  t.start()
  print "Hi there!"

test_timer()
