import badge
import ugfx
import wifi
import utime
import deepsleep
import urequests as req
import esp

badge.init()
wifi.init()
ugfx.init()

#Set to London NTP TZ
utime.settimezone("GMT+0BST-1,M3.5.0/01:00:00,M10.5.0/02:00:00")

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

def weathericon(data, x, y):
  return ugfx.Imagebox(x, y, 32, 32, '/lib/niall/icons/' + data.get("icon") + '.png')

def drawweather(r):
  dayweather = r.get("weatherday")
  xline = 106
  xday = 115
  xevening = 5

  if(utime.localtime()[3] > 12):
    dayweather = dayweather[1]
  else:
    dayweather = dayweather[0]
    xline = 190
    xevening = 199
    xday = 5

  ugfx.thickline(xline,0,xline,68,ugfx.BLACK,3,0)

  try:
    ugfx.string(xevening + 37, 6, "17:00", "DejaVuSans20", ugfx.BLACK)
    ugfx.string(xevening + 37, 38, str(int(r.get("weatherevening").get("precipProbability") * 100)) + "%", "DejaVuSans20", ugfx.BLACK)

    ugfx.string(xday + 37, 22, "WS:" + str(int(dayweather.get("windSpeed"))) + "mph", "DejaVuSans20", ugfx.BLACK)
    sunup = utime.localtime(int(dayweather.get("sunriseTime")))
    sundown = utime.localtime(int(dayweather.get("sunsetTime")))
    ugfx.string(xday + 37, 44, "S:" + str(sunup[3])+ ":" + str(sunup[4]) + "-" + str(sundown[3]) + ":" + str(sundown[4]), "DejaVuSans20", ugfx.BLACK)
    ugfx.string(xday + 37, 0, "Temp:" + str(int(dayweather.get("apparentTemperatureLow"))) + "-" + str(int(dayweather.get("apparentTemperatureHigh"))) + u"\u00b0" + "C" , "DejaVuSans20", ugfx.BLACK)
  except:
    print("missing precip chance")

  first = ""
  second = ""
  try:
    first = weathericon(r.get("weatherevening"), xevening, 16)
    second = weathericon(dayweather, xday, 16)
  except:
    print("no weather")

  return (first, second)

def draw(r):
  # Rows: 32
  try:
    ugfx.string(2, 102, "£" +  str(r.get("bank")), "DejaVuSans20", ugfx.BLACK)
  except:
    print("no balance")

  isOtherSet = False

  try:
    title = r.get("dates").get("summary")[0:19]
    time = r.get("dates").get("start").get("dateTime")[11:16]
    ugfx.string(2, 75, time +  " - " + title, "DejaVuSans20", ugfx.BLACK)
    isOtherSet = True
  except:
    print("no cal")

  try:
    if not isOtherSet:
      title = r.get("news")[0:39]
      ugfx.string(2, 75, title, "DejaVuSans20", ugfx.BLACK)
      isOtherSet = True
  except:
    print("no news")

  try:
    if not isOtherSet:
      title = r.get("other")[0:39]
      ugfx.string(2, 75, title, "DejaVuSans20", ugfx.BLACK)
      isOtherSet = True
  except:
    print("no other")

  ugfx.thickline(0,68,296,68,ugfx.BLACK,3,0)

  boxes = drawweather(r)

  ugfx.flush()

  try:
    boxes[0].destroy()
    boxes[1].destroy()
  except:
    print("no weather")

def wait_for_network():
  # Handle network connection
  if not wifi.sta_if.isconnected():
    while not wifi.sta_if.isconnected():
      log('Waiting for network')
      utime.sleep(1)
    log('Connected!')

clear_ghosting()
wait_for_network()
draw(makeRequest())
# hour
esp.rtcmem_write_string("0", 0)
esp.rtcmem_write_string("0", 1)
esp.rtcmem_write_string("niall", 2)
deepsleep.start_sleeping(3600  * 1000)
