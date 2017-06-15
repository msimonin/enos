import unittest
from enos.utils.extra import *
from enos.utils.errors import *
from enos.provider.host import Host
import copy

class TestExpandGroups(unittest.TestCase):
    def test_expand_groups(self):
        grps = "grp[1-3]"
        expanded = expand_groups(grps)
        self.assertEquals(3, len(expanded))

    def test_expand_one_group(self):
        grps = "grp"
        expanded = expand_groups(grps)
        self.assertEquals(1, len(expanded))

    def test_expand_groups_with_weird_name(self):
        grps = "a&![,[1-3]"
        expanded = expand_groups(grps)
        self.assertEquals(3, len(expanded))


class TestBuildRoles(unittest.TestCase):

    def setUp(self):
        self.config = {
            "resources": {
                "a": {
                    "controller": 1,
                    "compute" : 2,
                    "network" : 1,
                    "storage" : 1,
                    "util"    : 1
                }
            }
        }

    def byCluster(self, n):
        """G5K provider"""
        return n.address.split('-')[0]

    def bySize(self, n):
        """Vagrant provider"""
        return n["size"]

#    def test_not_enough_nodes(self):
#        deployed_nodes = map(lambda x: Host(x), ["a-1", "a-2", "a-3", "a-4"])
#        with self.assertRaises(Exception):
#            roles = build_roles(self.config, deployed_nodes, self.byCluster)

    def test_build_roles_same_number_of_nodes(self):
        deployed_nodes = map(lambda x: Host(x), ["a-1", "a-2", "a-3", "a-4", "a-5", "a-6"])
        roles = build_roles(self.config, deployed_nodes, self.byCluster)
        self.assertEquals(1, len(roles["controller"]))
        self.assertEquals(1, len(roles["storage"]))
        self.assertEquals(2, len(roles["compute"]))
        self.assertEquals(1, len(roles["network"]))
        self.assertEquals(1, len(roles["util"]))

    def test_build_roles_one_less_deployed_nodes(self):
        deployed_nodes = map(lambda x: Host(x), ["a-1", "a-2", "a-3", "a-4", "a-5"])
        roles = build_roles(self.config, deployed_nodes, self.byCluster)
        self.assertEquals(1, len(roles["controller"]))
        self.assertEquals(1, len(roles["storage"]))
        self.assertEquals(1, len(roles["compute"]))
        self.assertEquals(1, len(roles["network"]))
        self.assertEquals(1, len(roles["util"]))

    def test_build_roles_with_multiple_clusters(self):
        config = {
            "resources": {
                "a": {
                    "controller": 1,
                    "compute" : 2,
                    "network" : 1,
                    "storage" : 1,
                    "util"    : 1
                },
                "b": {
                    "compute": 2
                 }
            }
        }
        deployed_nodes = map(lambda x: Host(x), ["a-1", "a-2", "a-3", "a-4", "a-5", "a-6", "b-1", "b-2"])
        roles = build_roles(config, deployed_nodes, self.byCluster)
        self.assertEquals(1, len(roles["controller"]))
        self.assertEquals(1, len(roles["storage"]))
        self.assertEquals(4, len(roles["compute"]))
        self.assertEquals(1, len(roles["network"]))
        self.assertEquals(1, len(roles["util"]))

    def test_build_roles_with_multiple_sizes(self):
        config = {
            "resources": {
                "a": {
                    "controller": 1,
                },
                "b": {
                    "compute": 2
                 },
                "c": {
                    "compute": 2
                },
                "d": {
                    "storage": 1
                 }
            }
        }
        deployed_nodes = map(lambda x: {
            "size": x[0],
            "name": x
        }, ["a1", "b1", "b2", "c1", "c2", "d1"])

        roles = build_roles(config, deployed_nodes, self.bySize)
        self.assertEquals(4, len(roles["compute"]))
        self.assertEquals(1, len(roles["controller"]))
        self.assertEquals(1, len(roles["storage"]))

    def test_build_roles_with_topology(self):
        config = {
            "topology": {
                "grp1": {
                    "a":{
                        "control": 1,
                        "network": 1,
                        "util": 1
                        }
                    },
                "grp2": {
                    "a":{
                        "compute": 1,
                        }
                    },
                "grp3": {
                    "a":{
                        "compute": 1,
                        }
                    }
                },
               # resources is an aggregated view of the topology
               "resources": {
                   "a": {
                       "control": 1,
                       "network": 1,
                       "util": 1,
                       "compute": 2
                    }
               }
            }
        deployed_nodes = map(lambda x: Host(x), ["a-1", "a-2", "a-3", "a-4", "a-5"])
        roles = build_roles(config, deployed_nodes, self.byCluster)
        # Check the sizes
        self.assertEquals(2, len(roles["compute"]))
        self.assertEquals(1, len(roles["network"]))
        self.assertEquals(1, len(roles["control"]))
        # Check the consistency betwwen groups
        self.assertListEqual(sorted(roles["grp1"]), sorted(roles["control"] + roles["network"] + roles["util"]))
        self.assertListEqual(sorted(roles["grp2"] + roles["grp3"]), sorted(roles["compute"]))


class TestMakeProvider(unittest.TestCase):

    def __provider_env(self, provider_name):
        "Returns env with a provider key"
        return {"config": {"provider": provider_name}}

    def __provider_env_ext(self, provider_name):
        "Returns env with an extended provider key that may include options"
        return {"config": {"provider": {"type": provider_name}}}

    def test_make_g5k(self):
        "Tests the creation of G5k provider"
        from enos.provider.g5k import G5k
        self.assertIsInstance(make_provider(self.__provider_env('g5k')), G5k)
        self.assertIsInstance(make_provider(self.__provider_env_ext('g5k')), G5k)

    def test_make_vbox(self):
        "Tests the creation of Vbox provider"
        from enos.provider.enos_vagrant import Enos_vagrant
        self.assertIsInstance(make_provider(self.__provider_env('vagrant')), Enos_vagrant)
        self.assertIsInstance(make_provider(self.__provider_env_ext('vagrant')), Enos_vagrant)

    def test_make_static(self):
        "Tests the creation of Static provider"
        from enos.provider.static import Static
        self.assertIsInstance(make_provider(self.__provider_env('static')), Static)
        self.assertIsInstance(make_provider(self.__provider_env_ext('static')), Static)

    def test_make_unexist(self):
        "Tests the raise of error for unknown/unloaded provider"
        with self.assertRaises(ImportError):
            make_provider(self.__provider_env('unexist'))

class TestGenerateInventoryString(unittest.TestCase):
    def test_address(self):
        h = Host("1.2.3.4")
        role = "test"
        self.assertEqual("1.2.3.4 ansible_host=1.2.3.4 ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' g5k_role=test", generate_inventory_string(h, role))

    def test_address_alias(self):
        h = Host("1.2.3.4", alias="alias")
        role = "test"
        self.assertEqual("alias ansible_host=1.2.3.4 ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' g5k_role=test", generate_inventory_string(h, role))


    def test_address_user(self):
        h = Host("1.2.3.4", user="foo")
        role = "test"
        self.assertEqual("1.2.3.4 ansible_host=1.2.3.4 ansible_ssh_user=foo ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' g5k_role=test", generate_inventory_string(h, role))

    def test_address_gateway(self):
        h = Host("1.2.3.4", extra={'gateway': '4.3.2.1'})
        role = "test"
        self.assertEqual("1.2.3.4 ansible_host=1.2.3.4 ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand=\"ssh -W %h:%p -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 4.3.2.1\"' g5k_role=test", generate_inventory_string(h, role))

    def test_address_gateway_same_user(self):
        h = Host("1.2.3.4", user="foo", extra={'gateway': '4.3.2.1'})
        role = "test"
        self.assertEqual("1.2.3.4 ansible_host=1.2.3.4 ansible_ssh_user=foo ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand=\"ssh -W %h:%p -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -l foo 4.3.2.1\"' g5k_role=test", generate_inventory_string(h, role))


class TestGetTotalWantedMachines(unittest.TestCase):
    def test_get_total_wanted_machines(self):
        config = {
            "resources": {
                "a": {
                    "controller": 1,
                    "compute" : 2,
                    "network" : 1,
                    "storage" : 1,
                    "util"    : 1
                },
                "b": {
                    "compute": 2
                 }
            }
        }
        self.assertEquals(8, get_total_wanted_machines(config["resources"]))

class TestResourcesIterator(unittest.TestCase):
    def test_resources_iterator(self):
        config = {
            "resources": {
                "a": {
                    "controller": 1,
                    "network" : 1,
                    "storage" : 3,
                },
                "b": {
                    "compute": 2
                 }
            }
        }
        actual = []
        for l1, l2, l3 in gen_resources(config["resources"]):
            actual.append((l1, l2, l3))
        expected = [("a", "controller", 1),
                    ("a", "network", 1),
                    ("a", "storage", 3),
                    ("b", "compute", 2)]
        self.assertItemsEqual(expected, actual)


class TestLoadProviderConfig(unittest.TestCase):
    def test_load_provider_config_nest_type(self):
        provider_config = 'myprovider'
        expected = {
            'type': 'myprovider'
        }
        provider_config = load_provider_config(copy.deepcopy(provider_config))
        self.assertDictEqual(expected, provider_config)

    def test_load_provider_config_nest_type_with_defaults(self):
        provider_config = 'myprovider'
        default_provider_config = {
            'option1': 'value1',
            'option2': 'value2',
        }
        expected = {
            'type': 'myprovider',
            'option1': 'value1',
            'option2': 'value2',
        }
        provider_config = load_provider_config(
            copy.deepcopy(provider_config),
            default_provider_config=default_provider_config)
        self.assertDictEqual(expected, provider_config)

    def test_load_provider_config_with_defaults(self):
        provider_config = {
            'type': 'myprovider',
            'option1': 'myvalue1'
        }
        default_provider_config = {
            'option1': 'value1',
            'option2': 'value2',
        }
        expected = {
            'type': 'myprovider',
            'option1': 'myvalue1',
            'option2': 'value2',
        }
        provider_config = load_provider_config(
            copy.deepcopy(provider_config),
            default_provider_config=default_provider_config)
        self.assertDictEqual(expected, provider_config)

    def test_load_provider_config_with_missing_keys(self):
        from collections import OrderedDict

        provider_config = {
            'is-overrided1': 'overrided-value',
            'is-overrided2': 'overrided-value'
        }

        # Note: Go with an OrderedDict and its order preserving keys
        # extraction, rather than vanilla dict. OrderedDict makes the
        # assertRaisesRegexp reliable on the order of missing keys in
        # the error message.
        default_provider_config = OrderedDict([
            ('is-overrided1', None),
            ('missing-overriding1', None),
            ('is-overrided2', None),
            ('missing-overriding2', None),
            ('no-overriding-needed', False)])

        with self.assertRaisesRegexp(
                EnosProviderMissingConfigurationKeys,
                "\['missing-overriding1', 'missing-overriding2'\]"):
            load_provider_config(
                provider_config,
                default_provider_config)


class TestGetHostNet(unittest.TestCase):
    def test_map_devices_all_match_single(self):
        networks = [{
            'cidr': '1.2.3.4/24'
            }, {
            'cidr': '4.5.6.7/24'
            }]
        devices = [{
            'device': 'eth0',
            'ipv4': [{'address': '1.2.3.5'}]
        }, {
            'device': 'eth1',
            'ipv4': [{'address': '4.5.6.7'}]
        }]
        expected = [{
            'cidr': '4.5.6.7/24',
            'devices': 'eth1'
            }, {
            'cidr': '1.2.3.4/24',
            'devices': 'eth0'
            }]
        self.assertItemsEqual(expected, map_device_on_host_networks(networks, devices))

    def test_map_devices_all_match_multiple(self):
        networks = [{
            'cidr': '1.2.3.4/24'
            }, {
            'cidr': '4.5.6.7/24'
            }]
        devices = [{
            'device': 'eth0',
            'ipv4': [{'address': '1.2.3.5'}]
        }, {
            'device': 'eth1',
            'ipv4': [{'address': '1.2.3.254'}]
        }]
        # only the last match is taken into account
        expected = [{
            'cidr': '1.2.3.4/24',
            'devices': 'eth1'
            }, {
            'cidr': '4.5.6.7/24',
            'devices': None
            }]
        self.assertItemsEqual(expected, map_device_on_host_networks(networks, devices))

    def test_map_devices_net_veth(self):
        networks = [{
            'cidr': '1.2.3.4/24'
            }, {
            'cidr': '4.5.6.7/24'
            }]
        devices = [{
            'device': 'eth0',
            'ipv4': [{'address': '1.2.3.5'}]
        }, {
            'device': 'veth0',
            'ipv4': []
        }]
        expected = [{
            'cidr': '4.5.6.7/24',
            'devices': None
            }, {
            'cidr': '1.2.3.4/24',
            'devices': 'eth0'
            }]
        self.assertItemsEqual(expected, map_device_on_host_networks(networks, devices))


class TestUpdateProviderNets(unittest.TestCase):

    def setUp(self):
        def mapping(network, idx):
            if idx == 0:
                return 'network1'
            elif idx == 1:
                return 'network2'
            else:
                return None

        self.mapping = mapping

    def test_update_provider_nets(self):
        provider_nets = [
            {
                'cidr': '192.168.142.0/24',
            },
            {
                'cidr': '192.168.143.0/24',
            }
        ]
        internal_mapping_expected = {
            '192.168.142.0/24': 'network1',
            '192.168.143.0/24': 'network2',
        }

        internal_mapping = update_provider_nets(provider_nets, self.mapping)
        net1 = filter(lambda n: n['mapto'] == 'network1', provider_nets)[0]
        self.assertEqual('192.168.142.0/24', net1['cidr'])
        net2 = filter(lambda n: n['mapto'] == 'network2', provider_nets)[0]
        self.assertEqual('192.168.143.0/24', net2['cidr'])
        self.assertDictEqual(internal_mapping_expected, internal_mapping)


class TestUpdateHosts(unittest.TestCase):

    def setUp(self):
        self.mapping = {
            '1.2.3.0/24': 'network1',
            '2.2.3.0/24': 'network2',
        }

    def test_update_hosts(self):
        rsc = {'control': [Host('1.2.3.4', alias='foo'), Host('1.2.3.5', alias='bar')]}
        facts = {
                'foo': {
                    'networks': [{
                        'cidr': '1.2.3.0/24',
                        'devices': 'eth0'
                    }, {
                        'cidr': '2.2.3.0/24',
                        'devices': 'eth1'
                    }]},
                'bar': {
                    'networks': [{
                        'cidr': '1.2.3.0/24',
                        'devices': 'eth0'
                    }, {
                        'cidr': '2.2.3.0/24',
                        'devices': 'eth1'
                    }]},
                }

        update_hosts(rsc, facts, self.mapping)
        for host in gen_rsc(rsc):
            self.assertEqual('eth0', host.extra['network1'])
            self.assertEqual('eth1', host.extra['network2'])

    def test_update_hosts_inverted(self):
        rsc = {'control': [Host('1.2.3.4', alias='foo'), Host('1.2.3.5', alias='bar')]}
        facts = {
            'foo': {
                'networks': [{
                    'cidr': '1.2.3.0/24',
                    'devices': 'eth0'
                }, {
                    'cidr': '2.2.3.0/24',
                    'devices': 'eth1'
                }]},
            'bar': {
                'networks': [{
                    'cidr': '1.2.3.0/24',
                    'devices': 'eth1'
                }, {
                    'cidr': '2.2.3.0/24',
                    'devices': 'eth0'
                }]},
            }

        update_hosts(rsc, facts, self.mapping)
        for host in gen_rsc(rsc):
            if host.alias == 'foo':
                self.assertEqual('eth0', host.extra['network1'])
                self.assertEqual('eth1', host.extra['network2'])
            elif host.alias == 'bar':
                self.assertEqual('eth1', host.extra['network1'])
                self.assertEqual('eth0', host.extra['network2'])

    def test_update_hosts_unmatch(self):
        rsc = {'control': [Host('1.2.3.4', alias='foo')]}
        facts = {
                'foo': {
                    'networks': [{
                        'cidr': '1.2.3.0/24',
                        'devices': 'eth0'
                    }, {
                        'cidr': '2.2.3.0/24',
                        'devices': None
                    }]},
                }

        update_hosts(rsc, facts, self.mapping)
        for host in gen_rsc(rsc):
            self.assertEqual('eth0', host.extra['network1'])
            self.assertTrue('network2' not in host.extra)


class TestGetProviderNEt(unittest.TestCase):

    def setUp(self):
        self.provider_nets = [
            {
                'cidr': '192.168.142.0/24',
                'mapto': 'kolla_net1'
            },
            {
                'cidr': '192.168.143.0/24',
                'mapto': 'kolla_net2'
            }
        ]

    def test_get_provider_net_one_match(self):
        provider_net = get_provider_net(self.provider_nets, {'mapto': 'kolla_net1'})
        expected_provider_net = {
            'cidr': '192.168.142.0/24',
            'mapto': 'kolla_net1'
        }
        self.assertDictEqual(expected_provider_net, provider_net[0])

if __name__ == '__main__':
    unittest.main()
