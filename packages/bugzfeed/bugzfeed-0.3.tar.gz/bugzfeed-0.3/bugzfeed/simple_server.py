import tornado
from websocket import WebSocketHandler

port = 8844
address = '0.0.0.0'

application = tornado.web.Application([
    (r'/', WebSocketHandler),
])

ioloop = tornado.ioloop.IOLoop.instance()
print 'Starting WebSocket server on port %d.' % port
application.listen(port, address)
try:
    ioloop.start()
except KeyboardInterrupt:
    pass
