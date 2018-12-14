# -*- coding: utf-8 -*-

from .provider import Provider
from ..utils.extra import gen_enoslib_roles

import copy
from enoslib.api import expand_groups
from enoslib.infra.enos_vmong5k import provider
from enoslib.infra.enos_vmong5k.configuration import Configuration
import logging


logger = logging.getLogger(__name__)


# - SPHINX_DEFAULT_CONFIG
DEFAULT_CONFIG = {
    'job_name': 'Enos',             # Job name in oarstat/gant
    'walltime': '02:00:00',         # Reservation duration time
    'env_name': 'debian9-x64-nfs',  # Environment to deploy
    'queue': 'default'              # default, production, testing
}
# + SPHINX_DEFAULT_CONFIG


# - SPHINX_DEFAULT_FLAVOURS
FLAVOURS = {
    "control": {"core": 8, "mem": 32000000},
    "compute": {"core": 4, "mem": 8000000},
    "network": {"core": 8, "mem": 16000000}
}
# + SPHINX_DEFAULT_FLAVOURS

DEFAULT_FLAVOUR = {"core": 4, "mem": 8000000}

def _build_enoslib_conf(config):
    conf = copy.deepcopy(config)
    enoslib_conf = conf.get("provider", {})
    enoslib_conf.pop("type", None)

    if enoslib_conf.get("resources") is not None:
        # enoslib mode
        logger.debug("Getting resources specific to the provider")
        return enoslib_conf

    # EnOS legacy mode
    logger.debug("Getting generic resources from configuration")
    machines = []

    # get a plain configuration of resources
    resources = conf.get("resources", {})
    for desc in gen_enoslib_roles(resources):
        groups = expand_groups(desc["group"])
        for group in groups:
            machine = {"roles": [group, desc["role"]],
                       "number": desc["number"],
                       "cluster": desc["flavor"],
                       # assign a flavour to the vms here
                       "flavour_desc": FLAVOURS.get(desc["flavor"],
                                                    DEFAULT_FLAVOUR)}
            machines.append(machine)
    networks = ["network_interface"]
    enoslib_conf.update(resources={"machines": machines,
                                   "networks": networks})
    return enoslib_conf


class Vmong5k(Provider):
    """Prepare VMs on G5k."""

    def init(self, config, force=False):
        logger.debug("Building enoslib configuration")
        enoslib_conf = _build_enoslib_conf(config)
        conf = Configuration.from_dictionnary(enoslib_conf)
        logger.debug("Creating G5K provider")
        vmong5k = provider.VMonG5k(conf)
        logger.info("Initializing G5K provider")
        roles, networks = vmong5k.init(force)
        return roles, networks


    def destroy(self, env):
        pass

    def default_config(self):
        return {}

    def __str__(self):
        return 'VMonG5k'

