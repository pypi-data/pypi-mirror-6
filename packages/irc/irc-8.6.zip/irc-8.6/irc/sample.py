import irc.client

class StoppingManifold(irc.client.Manifold):
    "A custom Manifold that will stop when _running is set to False"
    _running = True

    def stop_process_forever(self):
        self._running = False

    def process_forever(self):
        while self._running:
            self.process_once()

class ThreadBot(irc.bot.SingleServerIRCBot):
    manifold_class = StoppingManifold

    def die(self, msg="Bye, cruel world!"):
        self.connection.disconnect(msg)
        self.manifold.stop_process_forever()
