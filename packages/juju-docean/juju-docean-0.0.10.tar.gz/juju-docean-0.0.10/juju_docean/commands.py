import logging
import time
import uuid
import yaml

from juju_docean.constraints import IMAGE_MAP, solve_constraints
from juju_docean.exceptions import ConfigError
from juju_docean import ops
from juju_docean.runner import Runner


log = logging.getLogger("juju.docean")


class BaseCommand(object):

    def __init__(self, config, provider, environment):
        self.config = config
        self.provider = provider
        self.env = environment
        self.runner = Runner()

    def solve_constraints(self):
        size, region = solve_constraints(self.config.constraints)
        return IMAGE_MAP[self.config.series], size, region

    def get_do_ssh_keys(self):
        return [k.id for k in self.provider.get_ssh_keys()]

    def check_preconditions(self):
        """Check for provider ssh key, and configured environments.yaml.
        """
        keys = self.get_do_ssh_keys()
        if not keys:
            raise ConfigError(
                "SSH Public Key must be uploaded to digital ocean")

        env_name = self.config.get_env_name()
        with open(self.config.get_env_conf()) as fh:
            conf = yaml.safe_load(fh.read())
            if not 'environments' in conf:
                raise ConfigError(
                    "Invalid environments.yaml, no 'environments' section")
            if not env_name in conf['environments']:
                raise ConfigError(
                    "Environment %r not in environments.yaml" % env_name)
            env = conf['environments'][env_name]
            if not env['type'] in ('null', 'manual'):
                raise ConfigError(
                    "Environment %r provider type is %r must be 'null'" % (
                        env_name, env['type']))
            if env['bootstrap-host']:
                raise ConfigError(
                    "Environment %r already has a bootstrap-host" % (
                        env_name))
        return keys


class Bootstrap(BaseCommand):
    """
    Actions:
    - Launch an instance
    - Wait for it to reach running state
    - Update environment in environments.yaml with bootstrap-host address.
    - Bootstrap juju environment

    Preconditions:
    - named environment found in environments.yaml
    - environment provider type is null
    - bootstrap-host must be null
    - at least one ssh key must exist.
    - ? existing digital ocean with matching env name does not exist.
    """
    def run(self):
        keys = self.check_preconditions()
        image, size, region = self.solve_constraints()
        log.info("Launching bootstrap host")
        params = dict(
            name="%s-0" % self.config.get_env_name(), image_id=image,
            size_id=size, region_id=region, ssh_key_ids=keys)

        op = ops.MachineAdd(
            self.provider, self.env, params, series=self.config.series)
        instance = op.run()

        log.info("Bootstrapping environment")
        try:
            self.env.bootstrap_jenv(instance.ip_address)
        except:
            self.provider.terminate_instance(instance.id)
            raise

    def check_preconditions(self):
        return super(Bootstrap, self).check_preconditions()


class AddMachine(BaseCommand):

    def run(self):
        keys = self.check_preconditions()
        image, size, region = self.solve_constraints()
        log.info("Launching %d instances", self.config.num_machines)

        template = dict(
            image_id=image, size_id=size, region_id=region, ssh_key_ids=keys)

        for n in range(self.config.num_machines):
            params = dict(template)
            params['name'] = "%s-%s" % (
                self.config.get_env_name(), uuid.uuid4().hex)
            self.runner.queue_op(
                ops.MachineRegister(
                    self.provider, self.env, params,
                    series=self.config.series))

        for (instance, machine_id) in self.runner.iter_results():
            log.info("Registered id:%s name:%s ip:%s as juju machine",
                     instance.id, instance.name, instance.ip_address)


class TerminateMachine(BaseCommand):

    def run(self):
        """Terminate machine in environment.
        """
        self.check_preconditions()
        self._terminate_machines(lambda x: x in self.config.options.machines)

    def _terminate_machines(self, remove_machines):
        log.debug("Checking for machines to terminate")
        status = self.env.status()
        machines = status.get('machines', {})

        # Using the api instance-id can be the provider id, but
        # else it defaults to ip, and we have to disambiguate.
        remove = []
        for m in machines:
            if remove_machines(m):
                remove.append(
                    {'address': machines[m]['dns-name'],
                     'instance_id': machines[m]['instance-id'],
                     'machine_id': m})

        if not remove:
            return

        log.info("Terminating machines %s",
                 " ".join([m['machine_id'] for m in remove]))
        address_map = dict([(d.ip_address, d.id) for
                            d in self.provider.get_instances()])

        for m in remove:
            instance_id = address_map.get(m['address'])
            if instance_id is None:
                log.warning(
                    "Couldn't resolve machine %s's address %s to instance" % (
                        m['machine_id'], m['address']))
                continue
            self.runner.queue_op(
                ops.MachineDestroy(
                    self.provider, self.env, {
                        'machine_id': m['machine_id'],
                        'instance_id': instance_id}))
        for result in self.runner.iter_results():
            pass


class DestroyEnvironment(TerminateMachine):

    def run(self):
        """Destroy environment.
        """
        self.check_preconditions()

        # Manual provider needs machines removed prior to env destroy.
        def state_service_filter(m):
            if m == "0":
                return False
            return True
        self._terminate_machines(state_service_filter)

        # sadness, machines are marked dead, but juju is async to
        # reality. either sleep (racy) or retry loop.
        time.sleep(10)
        log.info("Destroying environment")
        self.env.destroy_environment()
