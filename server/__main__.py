import manage
import sys
import protocol
from twisted.python import log
from twisted.internet import reactor, task, ssl, defer
from twisted.protocols import basic
from twisted.web import server
from autobahn.twisted.websocket import WebSocketServerFactory
from twisted.web.server import Site
from twisted.web.static import File
from OpenSSL import crypto
import os
import logging

# Enforce specific TLS version in the context factory
class CustomCertificateOptions(ssl.CertificateOptions):
    def __init__(self, privateKey, certificate, tls_version=ssl.TLSv1_2_METHOD):
        # Call the parent class constructor with required parameters
        super().__init__(privateKey=privateKey, certificate=certificate)
        # Set the desired TLS version (TLSv1.2 or TLSv1.3)
        self.method = tls_version

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
    
    # Set up logging
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(format)
    logger.addHandler(stdout_handler)

    # Load certificate and private key data
    certs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
    private_key_data = open(os.path.join(certs_dir, "server.key"), "rb").read()
    certificate_data = open(os.path.join(certs_dir, "server.crt"), "rb").read()

    # Load private key and certificate from PEM files
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data)
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, certificate_data)

    # Define the TLS version you want to enforce (use TLSv1_2_METHOD or TLSv1_3_METHOD)
    tls_version = ssl.TLSv1_2_METHOD  # You can change this to ssl.TLSv1_3_METHOD if needed

    # Create a custom certificate options object with the specified TLS version
    cert_options = CustomCertificateOptions(
        privateKey=private_key,
        certificate=certificate,
        tls_version=tls_version  # Pass the TLS version here
    )

    # Define the port for the server
    PORT: int = 8081
    factory = GameFactory('0.0.0.0', PORT)

    # Log the server start
    logger.info(f"Server listening on port {PORT}")
    
    # Start the SSL reactor with the custom certificate options
    reactor.listenSSL(PORT, factory, cert_options)

    # Run the reactor to handle incoming connections
    reactor.run()
