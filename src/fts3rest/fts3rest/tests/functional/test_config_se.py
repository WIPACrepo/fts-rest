#   Copyright notice:
#   Copyright CERN, 2014.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import ConfigAudit, Optimize, OperationConfig, Se


class TestConfigSe(TestController):

    def setUp(self):
        super(TestConfigSe, self).setUp()
        self.setup_gridsite_environment()
        Session.query(Optimize).delete()
        Session.query(ConfigAudit).delete()
        Session.query(OperationConfig).delete()
        Session.commit()


    def test_set_se_config(self):
        """
        Set SE config
        """
        config = {
            'test.cern.ch': {
                'operations': {
                    'atlas': {
                        'delete': 22,
                        'staging': 32,
                    },
                    'dteam': {
                        'delete': 10,
                        'staging': 11
                    }
                },
                'se_info': {
                    'ipv6': True,
                    'outbound_max_active': 55,
                    'inbound_max_active': 1,
                    'inbound_max_throughput': 33
                }
            }
        }
        self.app.post_json("/config/se",
            params= config,
            status=200
        )

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

        ops = Session.query(OperationConfig).filter(OperationConfig.host == 'test.cern.ch').all()
        self.assertEqual(4, len(ops))
        for op in ops:
            self.assertEqual(config[op.host]['operations'][op.vo_name][op.operation], op.concurrent_ops)

        se = Session.query(Se).filter(Se.storage == 'test.cern.ch').first()
        self.assertEqual(True, se.ipv6)
        self.assertEqual(55, se.outbound_max_active)
        self.assertEqual(1, se.inbound_max_active)
        self.assertEqual(33, se.inbound_max_throughput)

    def test_reset_se_config(self):
        """
        Reset SE config
        """
        self.test_set_se_config()

        config = {
            'test.cern.ch': {
                'operations': {
                    'atlas': {
                        'delete': 1,
                        'staging': 2,
                    },
                    'dteam': {
                        'delete': 3,
                        'staging': 4
                    }
                },
                'se_info': {
                    'ipv6': False,
                    'outbound_max_active': 88,
                    'inbound_max_active': 11,
                    'inbound_max_throughput': 10
                }
            }
        }
        self.app.post_json("/config/se",
            params= config,
            status=200
        )

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(4, len(audits))

        ops = Session.query(OperationConfig).filter(OperationConfig.host == 'test.cern.ch').all()
        self.assertEqual(4, len(ops))
        for op in ops:
            self.assertEqual(config[op.host]['operations'][op.vo_name][op.operation], op.concurrent_ops)

        se = Session.query(Se).filter(Se.storage == 'test.cern.ch').first()
        self.assertEqual(False, se.ipv6)
        self.assertEqual(88, se.outbound_max_active)
        self.assertEqual(11, se.inbound_max_active)
        self.assertEqual(10, se.inbound_max_throughput)

    def test_get_se_config(self):
        """
        Get SE config
        """
        self.test_set_se_config()

        cfg = self.app.get_json("/config/se?se=test.cern.ch", status=200).json

        self.assertIn('test.cern.ch', cfg.keys())
        se_cfg = cfg['test.cern.ch']

        self.assertIn('operations', se_cfg.keys())
        self.assertIn('se_info', se_cfg.keys())

        self.assertEqual(
            {'atlas': {'delete': 22, 'staging': 32}, 'dteam': {'delete': 10, 'staging': 11}},
            se_cfg['operations']
        )

        self.assertEqual(True, se_cfg['se_info']['ipv6'])
        self.assertEqual(55, se_cfg['se_info']['outbound_max_active'])
        self.assertEqual(1, se_cfg['se_info']['inbound_max_active'])
        self.assertEqual(33, se_cfg['se_info']['inbound_max_throughput'])

    def test_set_malformed(self):
        """
        Malformed configurations
        """
        config = {'test.cern.ch': 'what?'}
        self.app.post_json("/config/se",
            params=config,
            status=400
        )
        self.app.post_json("/config/se",
            params={
                'test.cern.ch': {
                    'operations': {
                        'atlas': {
                            'delete': 'must be a number!',
                        }
                    },
                    'se_info': {
                        'ipv6': False,
                        'outbound_max_active': 88,
                        'inbound_max_active': 11,
                        'inbound_max_throughput': 10
                    }
                }
            },
            status=400
        )
        self.app.post_json("/config/se",
            params={
                'test.cern.ch': {
                    'operations': {
                        'atlas': {
                            'delete': 2,
                        }
                    },
                    'se_info': {
                        'ipv6': False,
                        'active': 'not again!',
                        'inbound_max_active': 11,
                        'inbound_max_throughput': 10
                    }
                }
            },
            status=400
        )
        self.app.post_json("/config/se",
            params={
                'test.cern.ch': {
                    'se_info': {
                        'ipv6': True,
                        'inbound_max_active': 0.5,
                        'inbound_max_throughput': 10
                    }
                }
            },
            status=400
        )

    def test_remove_se_config(self):
        """
        Remove the configuration for a given SE
        """
        self.test_get_se_config()
        self.app.delete(url="/config/se",  status=400)
        self.app.delete(url="/config/se?se=test.cern.ch",  status=204)
