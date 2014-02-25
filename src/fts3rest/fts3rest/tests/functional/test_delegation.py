from datetime import datetime, timedelta
from M2Crypto import EVP
from nose.plugins.skip import SkipTest
import json
import pytz

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Credential, CredentialCache


class TestDelegation(TestController):
    """
    Tests for the delegation controller
    """

    def _get_termination_time(self, dlg_id):
        answer = self.app.get(url="/delegation/%s" % dlg_id)
        tt = datetime.strptime(str(json.loads(answer.body)['termination_time']), '%Y-%m-%dT%H:%M:%S')
        return tt.replace(tzinfo=pytz.UTC)

    def test_put_cred_without_cache(self):
        """
        This is a regression test. It tries to PUT directly
        credentials without the previous negotiation, so there is no
        CredentialCache in the database. This attempt must fail.
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)
        proxy = self.getX509Proxy(request.body)

        Session.delete(Session.query(CredentialCache).get((creds.delegation_id, creds.user_dn)))

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=400)

    def test_put_malformed_pem(self):
        """
        Putting a malformed proxy must fail
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                     status=200)

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params='MALFORMED!!!1',
                     status=400)

    def test_valid_proxy(self):
        """
        Putting a well-formed proxy with all the right steps must succeed
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)
        proxy = self.getX509Proxy(request.body)

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=201)

        proxy = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertNotEqual(None, proxy)
        return proxy

    def test_dn_mismatch(self):
        """
        A well-formed proxy with mismatching issuer and subject must fail
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)

        proxy = self.getX509Proxy(request.body, subject=[('DC', 'dummy')])

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=400)

    def test_signed_wrong_priv_key(self):
        """
        Regression for FTS-30
        If a proxy is signed with an invalid private key, reject it
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)

        proxy = self.getX509Proxy(request.body, private_key=EVP.PKey())

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=400)

    def test_get_request_different_dlg_id(self):
        """
        A user should be able only to get his/her own proxy request,
        and be denied any other.
        """
        self.setupGridsiteEnvironment()

        self.app.get(url="/delegation/12345xx/request",
                     status=403)

    def test_view_different_dlg_id(self):
        """
        A user should be able only to get his/her own delegation information.
        """
        self.setupGridsiteEnvironment()

        self.app.get(url="/delegation/12345x",
                     status=403)

    def test_remove_delegation(self):
        """
        A user should be able to remove his/her proxy
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        self.test_valid_proxy()

        self.app.delete(url="/delegation/%s" % creds.delegation_id,
                        status=204)

        self.app.delete(url="/delegation/%s" % creds.delegation_id,
                        status=404)

        proxy = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertEqual(None, proxy)

    def test_set_voms(self):
        """
        The server must regenerate a proxy with VOMS extensions
        Need a real proxy for this one
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        # Need to push a real proxy :/
        proxy_pem = self.getRealX509Proxy()
        if proxy_pem is None:
            raise SkipTest('Could not get a valid real proxy for test_set_voms')

        proxy = Credential()
        proxy.dn = creds.user_dn
        proxy.dlg_id = creds.delegation_id
        proxy.termination_time = datetime.utcnow() + timedelta(hours=1)
        proxy.proxy = proxy_pem
        Session.merge(proxy)
        Session.commit()

        # Now, request the voms extensions
        self.app.post(url="/delegation/%s/voms" % creds.delegation_id,
                      content_type='application/json',
                      params=json.dumps(['dteam:/dteam/Role=lcgadmin']),
                      status=203)

        # And validate
        proxy2 = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertNotEqual(proxy.proxy, proxy2.proxy)
        self.assertEqual('dteam:/dteam/Role=lcgadmin', proxy2.voms_attrs)
