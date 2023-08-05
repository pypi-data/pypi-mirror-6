Vase is a webframework for Tulip/asyncio
~~~~~~~~~~~~~~~~~~~~~~

Inspired by Flask
It currently has a basic WSGI interface and WebSocket support.
A demo websocket app is available here http://vase-chat.herokuapp.com/

Sample echo app
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from vase import Vase

    app = Vase(__name__)


    @app.route(path="/")
    def hello(request):
        return "Hello Vase!"


    @app.endpoint(path="/ws/echo")
    class EchoEndpoint:
        """
        WebSocket endpoint
        Has the following attributes:
        `bag` - a dictionary that is shared between all instances of this endpoint
        `transport` - used to send messages into the websocket
        """
        def on_connect(self):
            self.transport.send("You are successfully connected")

        def on_message(self, message):
            self.transport.send(message)

        def on_close(self, exc=None):
            print("Connection closed")

    if __name__ == '__main__':
        app.run()
