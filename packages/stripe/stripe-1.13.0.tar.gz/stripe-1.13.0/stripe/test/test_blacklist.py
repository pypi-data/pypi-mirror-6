import ssl

from stripe import blacklist
from stripe.error import APIError
from stripe.test.helper import StripeTestCase


class BlacklistTest(StripeTestCase):

    def test_revoked_cert_is_revoked(self):
        hostname = "revoked.stripe.com"
        cert = ssl.get_server_certificate((hostname, 443))
        self.assertRaises(APIError, lambda: blacklist.verify(hostname, cert))

    def test_live_cert_is_not_revoked(self):
        hostname = "api.stripe.com"
        cert = ssl.get_server_certificate((hostname, 443))
        self.assertTrue(blacklist.verify(hostname, cert))
