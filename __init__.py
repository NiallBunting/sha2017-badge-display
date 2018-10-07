import badge
import ugfx
import time
import wifi
import utime
import urequests as req

badge.init()
wifi.init()
ugfx.init()

def makeRequest():
  return req.get("http://turing.niallbunting.com:4444/personal", headers={"Authorization": "apiKey 3kzWILoPBMhmKzlhtI1Ama:7FoBOTc4D3KD7TaXW3UdU6"}).json()

def clear_ghosting():
  ugfx.clear(ugfx.BLACK)
  ugfx.flush()
  badge.eink_busy_wait()
  ugfx.clear(ugfx.WHITE)
  ugfx.flush()
  badge.eink_busy_wait()

def log(text):
  print(text)

def weather(data, x, y):
  return ugfx.Imagebox(x, y, 32, 32, '/lib/niall/icons/' + data.get("icon") + '.png')

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

  ugfx.thickline(106,0,106,68,ugfx.BLACK,3,0)
  ugfx.thickline(0,68,296,68,ugfx.BLACK,3,0)
  try:
    ugfx.string(42, 6, "17:00", "DejaVuSans20", ugfx.BLACK)
    ugfx.string(42, 38, str(int(r.get("weatherevening").get("precipProbability") * 100)) + "%", "DejaVuSans20", ugfx.BLACK)
    ugfx.string(152, 22, "WS:" + str(int(r.get("weathertomorrow").get("windSpeed"))) + "mph", "DejaVuSans20", ugfx.BLACK)
    sunup = utime.localtime(int(r.get("weathertomorrow").get("sunriseTime")))
    sundown = utime.localtime(int(r.get("weathertomorrow").get("sunsetTime")))
    ugfx.string(152, 44, "S:" + str(sunup[3])+ ":" + str(sunup[4]) + "-" + str(sundown[3]) + ":" + str(sundown[4]), "DejaVuSans20", ugfx.BLACK)
    ugfx.string(152, 0, "Temp:" + str(int(r.get("weathertomorrow").get("apparentTemperatureLow"))) + "-" + str(int(r.get("weathertomorrow").get("apparentTemperatureHigh"))) + u"\u00b0" + "C" , "DejaVuSans20", ugfx.BLACK)
  except:
    print("missing precip chance")

  first = ""
  second = ""
  try:
    first = weather(r.get("weatherevening"), 5, 16)
    second = weather(r.get("weathertomorrow"), 115, 16)
  except:
    print("no weather")

  ugfx.flush()

  try:
    first.destroy()
    second.destroy()
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
  # 20 mins
  time.sleep(3600)
