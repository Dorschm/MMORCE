import manage
import sys
import protocol
from twisted.python import log
from twisted.internet import reactor, task
from autobahn.twisted.websocket import WebSocketServerFactory


class GameFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        self.protocol = protocol.GameServerProtocol
        super().__init__(f"wss://{hostname}:{port}")

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
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(format)
    logger.addHandler(stdout_handler)

    certs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
    private_key_data = open(os.path.join(certs_dir, "server.key"), "rb").read()
    certificate_data = open(os.path.join(certs_dir, "server.crt"), "rb").read()

    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data)
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, certificate_data)

    cert_options = CertificateOptions(
        privateKey=private_key,
        certificate=certificate,
    )

    PORT: int = 8081
    factory = GameFactory('0.0.0.0', PORT)

    logger.info(f"Server listening on port {PORT}")
    reactor.listenSSL(PORT, factory, cert_options)

    reactor.run()