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
  print(str(utime.time()) + ": " + text)

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

  infoLine = None

  try:
    title = r.get("dates").get("summary")
    time = r.get("dates").get("start").get("dateTime")[11:16]
    infoLine = time +  " - " + title
  except:
    print("no cal")

  try:
    if infoLine is None:
      infoLine = r.get("news")
  except:
    print("no news")

  try:
    if infoLine is None:
      infoLine = r.get("other")
  except:
    print("no other")

  if infoLine is not None:
    font = "DejaVuSans20"
    if (ugfx.get_string_width(infoLine, "DejaVuSans20") > 592):
      font = "Roboto_Regular12"

    firstLine = infoLine
    while (ugfx.get_string_width(firstLine, font) > 296):
      firstLine = firstLine[:-1]

    secondLine = None
    # Check for second line
    if len(firstLine) != len(infoLine):
      secondLine = infoLine[len(firstLine):]
      while (ugfx.get_string_width(secondLine, font) > 296):
        secondLine = secondLine[:-1]
      if font == "Roboto_Regular12":
        ugfx.string(2, 82, secondLine, font, ugfx.BLACK)
      else:
        ugfx.string(2, 90, secondLine, font, ugfx.BLACK)

    # Third line
    if font == "Roboto_Regular12":
      if (len(firstLine) + len(secondLine)) != len(infoLine):
        ugfx.string(2, 94, infoLine[len(firstLine)+len(secondLine):], font, ugfx.BLACK)

    singleLineOffset = 0;
    if secondLine is None:
      singleLineOffset += 10

    ugfx.string(2, 70 + singleLineOffset, firstLine, font, ugfx.BLACK)

  try:
    ugfx.string(2, 110, "£" +  str(r.get("bank")), "DejaVuSans20", ugfx.BLACK)
  except:
    print("no balance")

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
if(esp.rtcmem_read_string(2) != "niall"):
  esp.rtcmem_write_string("0", 0)
  esp.rtcmem_write_string("0", 1)
  esp.rtcmem_write_string("niall", 2)
# 35 mins, seems that works.
deepsleep.start_sleeping(2100  * 1000)
