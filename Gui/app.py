import random
import sys
import threading
import time

import webview




class HeavyStuffAPI:
    def __init__(self):
        self.cancel_heavy_stuff_flag = False

    def doHeavyStuff(self):
        time.sleep(0.1)  # sleep to prevent from the ui thread from freezing for a moment
        now = time.time()
        self.cancel_heavy_stuff_flag = False
        for i in range(0, 1000000):
            _ = i * random.randint(0, 1000)
            if self.cancel_heavy_stuff_flag:
                response = {'message': 'Operation cancelled'}
                break
        else:
            then = time.time()
            response = {
                'message': 'Operation took {0:.1f} seconds on the thread {1}'.format(
                    (then - now), threading.current_thread()
                )
            }
        return response

    def cancelHeavyStuff(self):
        time.sleep(0.1)
        self.cancel_heavy_stuff_flag = True

class NotExposedApi:
    def notExposedMethod(self):
        return 'This method is not exposed'

class Api:
    heavy_stuff = HeavyStuffAPI()
    _this_wont_be_exposed = NotExposedApi()

    def init(self):
        response = {'message': 'Hello from Python {0}'.format(sys.version)}
        return response

    def getRandomNumber(self):
        response = {
            'message': 'Here is a random number courtesy of randint: {0}'.format(
                random.randint(0, 100000000)
            )
        }
        return response

    def sayHelloTo(self, name):
        response = {'message': 'Hello {0}!'.format(name)}
        return response

    def error(self):
        raise Exception('This is a Python exception')

if __name__ != '__main__':
    api = Api()
    window = webview.create_window('JS API example', "GUI/aresUI/test.html", js_api=api)
    webview.start()