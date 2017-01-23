import RPi.GPIO as gpio
import requests
import json
import io
from time import sleep
from picamera import PiCamera


SECONDS = 10

FACE_LIST = 'keg_list'

API_KEY = FILL_ME_IN

FACE_LIST_ADD_URL = 'https://westus.api.cognitive.microsoft.com/face/v1.0/facelists/%s/persistedFaces' % FACE_LIST
DETECT_URL = 'https://westus.api.cognitive.microsoft.com/face/v1.0/detect?returnFaceId=True'
FIND_SIMILAR_URL = 'https://westus.api.cognitive.microsoft.com/face/v1.0/findsimilars'

OCTET_HEADERS = {'Content-type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': API_KEY}
JSON_HEADERS = {'Content-type': 'application/json', 'Ocp-Apim-Subscription-Key': API_KEY}


gpio.setmode(gpio.BCM)
gpio.setup(4, gpio.OUT)

cam = PiCamera()
sleep(2)


def open_valve():
  gpio.output(4, 1)
  print('Opening Valve')
  sleep(SECONDS)
  print('Closing Valve')
  gpio.output(4, 0)


def get_face_id(path):
  data = open(path, 'rb').read()
  resp = requests.post(url=DETECT_URL, data=data, headers=OCTET_HEADERS)
  if resp.ok:
    try:
      face_id = json.loads(resp.content)[0].get('faceId')
      return face_id
    except:
      return None
  else:
    return None


def add_face_to_face_list():
  file_name = take_pic()
  data = open(file_name, 'rb').read()
  resp = requests.post(url=FACE_LIST_ADD_URL, data=data, headers=OCTET_HEADERS)
  if resp.ok:
    return True
  else:
    return False


def find_similar(face_id):
  payload = {
    'faceId': face_id,
    'faceListId': FACE_LIST,
    'maxNumOfCandidatesReturned': 1
  }
  resp = requests.post(url=FIND_SIMILAR_URL, data=json.dumps(payload), headers=JSON_HEADERS)
  if resp.ok:
    print(resp.content)
    try:
      p_id = json.loads(resp.content)[0]
      return True
    except:
      return False
  return False


def take_pic():
  raw_input('Press any key to take pic')
  cam.capture('temp.jpeg')
  return 'temp.jpeg'


def verify_user():
  file_name = take_pic()
  #file_name = 'temp.jpeg'
  new_id = get_face_id(path=file_name)
  if not new_id:
    print 'no face detected'
    return
  print(new_id)
  verified = find_similar(new_id)
  if verified:
    print 'have a beer!'
    open_valve()
  else:
    print 'nope'


while True:
  option = raw_input('press (v) to verify\n' +
                     'press (a) to add a user\n')
  if option.lower() == 'a':
    add_face_to_face_list()
  elif option.lower() == 'v':
    verify_user()
  elif option.lower() == 'super admin override':
    open_valve()
  elif option.lower() == 'end this program':
    gpio.cleanup()
    exit()
