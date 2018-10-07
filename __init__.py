import badge
import ugfx
import time
import wifi
import urequests as req

badge.init()
wifi.init()
ugfx.init()

def makeRequest():
  return req.get("http://niallbunting.com", headers={"Authorization": "mykey"}).json()

def clear_ghosting():
  ugfx.clear(ugfx.BLACK)
  ugfx.flush()
  badge.eink_busy_wait()
  ugfx.clear(ugfx.WHITE)
  ugfx.flush()
  badge.eink_busy_wait()

def log(text):
  print(text)

def weather(data, loc):
  return ugfx.Imagebox(loc, 0, 64, 64, '/lib/niall/icons/' + data.get("icon") + '.png')

def draw(r):
  # Rows: 32
  try:
    ugfx.string(2, 102, "Balance: £" +  str(r.get("bank")), "DejaVuSans20", ugfx.BLACK)
  except:
    print("no balance")

  try:
    title = r.get("dates").get("summary")[0:19]
    time = r.get("dates").get("start").get("dateTime")[11:16]
    ugfx.string(2, 75, time +  " - " + title, "DejaVuSans20", ugfx.BLACK)
  except:
    print("no cal")

  ugfx.thickline(148,0,148,68,ugfx.BLACK,3,0)
  ugfx.thickline(0,68,296,68,ugfx.BLACK,3,0)
  try:
    ugfx.string(64, 6, "09:00", "DejaVuSans20", ugfx.BLACK)
    ugfx.string(152, 6, "17:00", "DejaVuSans20", ugfx.BLACK)
    ugfx.string(64, 38, str(int(r.get("morning").get("precipProbability") * 100)) + "%", "DejaVuSans20", ugfx.BLACK)
    ugfx.string(152, 38, str(int(r.get("evening").get("precipProbability") * 100)) + "%", "DejaVuSans20", ugfx.BLACK)
  except:
    print("missing precip chance")

  morn = ""
  even = ""
  try:
    morn = weather(r.get("morning"), 0)
    even = weather(r.get("evening"), 232)
  except:
    print("no weather")

  ugfx.flush()

  try:
    morn.destroy()
    even.destroy()
  except:
    print("no weather")

def wait_for_network():
  # Handle network connection
  if not wifi.sta_if.isconnected():
    while not wifi.sta_if.isconnected():
      log('Waiting for network')
      time.sleep(1)
    log('Connected!')

clear_ghosting()
time.sleep(1)

while True:
  clear_ghosting()
  wait_for_network()
  draw(makeRequest())
  time.sleep(180)
