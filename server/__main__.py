import manage
import sys
import protocol
from twisted.python import log
from twisted.internet import reactor, task
from autobahn.twisted.websocket import WebSocketServerFactory
import os
import logging

class GameFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        self.protocol = protocol.GameServerProtocol
        super().__init__(f"ws://{hostname}:{port}")

        self.players: set[protocol.GameServerProtocol] = set()

        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / 20)  # 20 times per second

    def tick(self):
        for p in self.players:
            p.tick()

    # Override
    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        self.players.add(p)
        return p


if __name__ == '__main__':
    print("Starting")
    
    # Set up logging
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(format)
    logger.addHandler(stdout_handler)

    # Define the port for the server
    PORT: int = 8081
    factory = GameFactory('0.0.0.0', PORT)

    # Log the server start
    logger.info(f"Server listening on port {PORT}")
    
    # Start the reactor to handle incoming connections
    reactor.listenTCP(PORT, factory)
    reactor.run()
