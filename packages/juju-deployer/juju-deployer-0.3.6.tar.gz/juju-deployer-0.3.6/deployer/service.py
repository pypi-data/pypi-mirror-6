from feedback import Feedback


class Service(object):

    def __init__(self, name, svc_data):
        self.svc_data = svc_data
        self.name = name

    def __repr__(self):
        return "<Service %s>" % (self.name)

    @property
    def annotations(self):
        a = self.svc_data.get('annotations')
        if a is None:
            return a
        # core annotations only supports string key / values
        d = {}
        for k, v in a.items():
            d[str(k)] = str(v)
        return d

    @property
    def config(self):
        return self.svc_data.get('options', None)

    @property
    def constraints(self):
        return self.svc_data.get('constraints', None)

    @property
    def num_units(self):
        return int(self.svc_data.get('num_units', 1))

    @property
    def unit_placement(self):
        # Separate checks to support machine 0 placement.
        value = self.svc_data.get('to')
        if value is None:
            value = self.svc_data.get('force-machine')
        if value is not None and not isinstance(value, list):
            value = [value]
        return value and map(str, value) or []

    @property
    def expose(self):
        return self.svc_data.get('expose', False)


class ServiceUnitPlacement(object):

    def __init__(self, service, deployment, status):
        self.service = service
        self.deployment = deployment
        self.status = status

    @staticmethod
    def _format_placement(machine, container=None):
        if container:
            return "%s:%s" % (container, machine)
        else:
            return machine

    def validate(self):
        feedback = Feedback()

        unit_placement = self.service.unit_placement
        if unit_placement is None:
            return feedback

        if not isinstance(unit_placement, list):
            unit_placement = [unit_placement]
        unit_placement = map(str, unit_placement)

        services = dict([(s.name, s) for s in self.deployment.get_services()])

        for idx, p in enumerate(unit_placement):
            if ':' in p:
                container, p = p.split(':')
                if container not in ('lxc', 'kvm'):
                    feedback.error(
                        "Invalid service:%s placement: %s" % (
                            self.service.name, unit_placement[idx]))
            if '=' in p:
                p, u_idx = p.split("=")
                if not u_idx.isdigit():
                    feedback.error(
                        "Invalid service:%s placement: %s",
                        self.service.name, unit_placement[idx])
            if p.isdigit() and p == '0':
                continue
            elif p.isdigit():
                feedback.error(
                    "Service placement to machine not supported %s to %s",
                    self.service.name, unit_placement[idx])
            elif p in services:
                if services[p].unit_placement:
                    feedback.error(
                        "Nested placement not supported %s -> %s -> %s" % (
                            self.service.name, p, services[p].unit_placement))
            else:
                feedback.error(
                    "Invalid service placement %s to %s" % (
                        self.service.name, unit_placement[idx]))
        return feedback

    def get(self, unit_number):
        status = self.status
        svc = self.service

        unit_mapping = svc.unit_placement
        if not unit_mapping:
            return None
        if len(unit_mapping) <= unit_number:
            return None

        unit_placement = placement = str(unit_mapping[unit_number])
        container = None
        u_idx = unit_number

        if ':' in unit_placement:
            container, placement = unit_placement.split(":")
        if '=' in placement:
            placement, u_idx = placement.split("=")

        if placement.isdigit() and placement == "0":
            return self._format_placement(placement, container)

        with_service = status['services'].get(placement)
        if with_service is None:
            # Should be caught in validate relations but sanity check
            # for concurrency.
            self.deployment.log.error(
                "Service %s to be deployed with non existant service %s",
                svc.name, placement)
            # Prefer continuing deployment with a new machine rather
            # than an in-progress abort.
            return None

        svc_units = with_service['units']
        if len(svc_units) <= unit_number:
            self.deployment.log.warning(
                "Service:%s deploy-with Service:%s, but no with unit found",
                svc.name, placement)
            return None
        unit_names = svc_units.keys()
        unit_names.sort()
        machine = svc_units[unit_names[int(u_idx)]].get('machine')
        if not machine:
            self.deployment.log.warning(
                "Service:%s deploy-with unit missing machine %s",
                svc.name, unit_names[unit_number])
            return None
        return self._format_placement(machine, container)
