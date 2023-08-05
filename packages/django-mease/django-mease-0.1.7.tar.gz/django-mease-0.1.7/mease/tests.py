import threading
from django.core.management import call_command
from django.test import TestCase

from .settings import TEST_WEBSOCKET_PORT


threading.Thread(
    target=call_command,
    args=['start_websocket_server'],
    kwargs={'port': TEST_WEBSOCKET_PORT, 'host': 'localhost'})


class MeaseTestCase(TestCase):
    def test_dicks(self):
        import time
        time.sleep(10)
