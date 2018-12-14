import unittest

import mock

from enos.provider.vmong5k import (_build_enoslib_conf)

PROVIDER = {'type': 'vmong5k',
            'job_name': 'enos-test'}


class TestGenEnoslibRoles(unittest.TestCase):

    def test_build_enoslib_conf(self):
        resources = {
            'parapluie': {
                'control': 1,
                'compute': 100,
                'notregistered': 2
            }
        }

        conf = {
            'resources': resources,
            'provider': PROVIDER
        }

        enoslib_conf = _build_enoslib_conf(conf)
        self.assertEquals(3, len(enoslib_conf["resources"]["machines"]))
