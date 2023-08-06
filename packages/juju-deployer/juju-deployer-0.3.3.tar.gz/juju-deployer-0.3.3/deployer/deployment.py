from base64 import b64encode

import logging
import pprint
import os
import yaml

from .charm import Charm
from .feedback import Feedback
from .service import Service, ServiceUnitPlacement
from .relation import Endpoint
from .utils import path_join, yaml_dump, ErrorExit, resolve_include


class Deployment(object):

    log = logging.getLogger("deployer.deploy")

    def __init__(self, name, data, include_dirs, repo_path=""):
        self.name = name
        self.data = data
        self.include_dirs = include_dirs
        self.repo_path = repo_path

    @property
    def series(self):
        # Series could use a little help, charm series should be inferred
        # directly from a store url
        return self.data.get('series', 'precise')

    @property
    def series_path(self):
        return path_join(self.repo_path, self.series)

    def pretty_print(self):
        pprint.pprint(self.data)

    def get_service(self, name):
        if not name in self.data['services']:
            return
        return Service(name, self.data['services'][name])

    def get_services(self):
        services = []
        for name, svc_data in self.data.get('services', {}).items():
            services.append(Service(name, svc_data))
        services.sort(self._placement_sort)
        return services

    def get_service_names(self):
        """Return a sequence of service names for this deployment."""
        return self.data.get('services', {}).keys()

    @staticmethod
    def _placement_sort(svc_a, svc_b):
        if svc_a.unit_placement:
            if svc_b.unit_placement:
                return cmp(svc_a.name, svc_b.name)
            return 1
        if svc_b.unit_placement:
            return -1
        return cmp(svc_a.name, svc_b.name)

    def get_unit_placement(self, svc, status):
        if isinstance(svc, (str, unicode)):
            svc = self.get_service(svc)
        return ServiceUnitPlacement(svc, self, status)

    def get_relations(self):
        if 'relations' not in self.data:
            return

        # Strip duplicate rels
        seen = set()

        def check(a, b):
            k = tuple(sorted([a, b]))
            if k in seen:
                #self.log.warning(" Skipping duplicate relation %r" % (k,))
                return
            seen.add(k)
            return True

        # Support an ordered list of [endpoints]
        if isinstance(self.data['relations'], list):
            for end_a, end_b in self.data['relations']:
                # Allow shorthand of [end_a, [end_b, end_c]]
                if isinstance(end_b, list):
                    for eb in end_b:
                        if check(end_a, eb):
                            yield (end_a, eb)
                else:
                    if check(end_a, end_b):
                        yield (end_a, end_b)
            return

        # Legacy format (dictionary of dictionaries with weights)
        rels = {}
        for k, v in self.data['relations'].items():
            expanded = []
            for c in v['consumes']:
                expanded.append((k, c))
            by_weight = rels.setdefault(v.get('weight', 0), [])
            by_weight.extend(expanded)
        for k in sorted(rels, reverse=True):
            for r in rels[k]:
                if check(*r):
                    yield r
        #self.log.debug(
        #    "Found relations %s\n  %s" % (" ".join(map(str, seen))))

    def get_charms(self):
        for k, v in self.data.get('services', {}).items():
            yield Charm.from_service(k, self.series_path, v)

    def get_charm_for(self, svc_name):
        svc_data = self.data['services'][svc_name]
        return Charm.from_service(svc_name, self.series_path, svc_data)

    def fetch_charms(self, update=False, no_local_mods=False):
        if not os.path.exists(self.series_path):
            os.mkdir(self.series_path)
        for charm in self.get_charms():
            if charm.is_local():
                if charm.exists():
                    if no_local_mods:
                        if charm.is_modified():
                            self.log.warning(
                                "Charm %r has local modifications",
                                charm.path)
                            raise ErrorExit()
                    if update:
                        charm.update(build=True)
                    continue
            charm.fetch()

    def resolve(self, cli_overides=()):
        # Once we have charms definitions available, we can do verification
        # of config options.
        self.load_overrides(cli_overides)
        self.resolve_config()
        self.validate_relations()
        self.validate_placement()

    def load_overrides(self, cli_overrides=()):
        """Load overrides."""
        overrides = {}
        overrides.update(self.data.get('overrides', {}))

        for o in cli_overrides:
            key, value = o.split('=', 1)
            overrides[key] = value

        for k, v in overrides.iteritems():
            found = False
            for svc_name, svc_data in self.data['services'].items():
                charm = self.get_charm_for(svc_name)
                if k in charm.config:
                    if 'options' not in svc_data:
                        svc_data['options'] = {}
                    svc_data['options'][k] = v
                    found = True
            if not found:
                self.log.warning(
                    "Override %s does not match any charms", k)

    def resolve_config(self):
        """Load any lazy config values (includes), and verify config options.
        """
        self.log.debug("Resolving configuration")
        # XXX TODO, rename resolve, validate relations
        # against defined services
        feedback = Feedback()
        for svc_name, svc_data in self.data.get('services', {}).items():
            if not 'options' in svc_data:
                continue
            charm = self.get_charm_for(svc_name)
            config = charm.config
            options = {}

            for k, v in svc_data['options'].items():
                if not k in config:
                    feedback.error(
                        "Invalid config charm %s %s=%s" % (charm.name, k, v))
                    continue
                iv = self._resolve_include(svc_name, k, v)
                if isinstance(iv, Feedback):
                    feedback.extend(iv)
                    continue
                if iv is not None:
                    v = iv
                options[k] = v
            svc_data['options'] = options
        self._handle_feedback(feedback)

    def _resolve_include(self, svc_name, k, v):
        feedback = Feedback()
        for include_type in ["file", "base64"]:
            if (not isinstance(v, basestring)
                or not v.startswith(
                    "include-%s://" % include_type)):
                continue
            include, fname = v.split("://", 1)
            ip = resolve_include(fname, self.include_dirs)
            if ip is None:
                feedback.error(
                    "Invalid config %s.%s include not found %s" % (
                    svc_name, k, v))
                continue
            with open(ip) as fh:
                v = fh.read()
                if include_type == "base64":
                    v = b64encode(v)
                return v
        if feedback:
            return feedback

    def validate_relations(self):
        # Could extend to do interface matching against charms.
        services = dict([(s.name, s) for s in self.get_services()])
        feedback = Feedback()
        for e_a, e_b in self.get_relations():
            for ep in [Endpoint(e_a), Endpoint(e_b)]:
                if not ep.service in services:
                    feedback.error(
                        ("Invalid relation in config,"
                         " service %s not found, rel %s") % (
                             ep.service, "%s <-> %s" % (e_a, e_b)))
                    continue
        self._handle_feedback(feedback)

    def validate_placement(self):
        services = dict([(s.name, s) for s in self.get_services()])
        feedback = Feedback()
        for name, s in services.items():
            placement = self.get_unit_placement(s, {})
            feedback.extend(placement.validate())
        self._handle_feedback(feedback)

    def _handle_feedback(self, feedback):
        for e in feedback.get_errors():
            self.log.error(e)
        for w in feedback.get_warnings():
            self.log.warning(w)
        if feedback.has_errors:
            raise ErrorExit()

    def save(self, path):
        with open(path, "w") as fh:
            fh.write(yaml_dump(self.data))

    @staticmethod
    def to_yaml(dumper, deployment):
        return dumper.represent_dict(deployment.data)

yaml.add_representer(Deployment, Deployment.to_yaml)
