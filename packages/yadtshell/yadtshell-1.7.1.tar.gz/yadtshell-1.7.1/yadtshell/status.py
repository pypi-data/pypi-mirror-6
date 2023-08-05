# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#   YADT - an Augmented Deployment Tool
#   Copyright (C) 2010-2013  Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

import glob
import os
import logging
import sys
import traceback
import inspect
import shlex
import yaml
import simplejson as json

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import defer

from hostexpand.HostExpander import HostExpander
import yadtshell
from yadtshell.util import compute_dependency_scores


logger = logging.getLogger('status')

local_service_collector = None


def status_cb(protocol=None):
    return status()


def query_status(component, pi=None):
    p = yadtshell.twisted.YadtProcessProtocol(
        component, '/usr/bin/yadt-status', pi)
    p.deferred = defer.Deferred()
    p.deferred.name = component
    cmd = shlex.split(yadtshell.settings.SSH) + [component]
    reactor.spawnProcess(p, cmd[0], cmd, os.environ)
    return p.deferred


def create_host(protocol, components, yaml_loader):
    if isinstance(protocol, yadtshell.components.UnreachableHost):
        unreachable_host = protocol
        unreachable_host_uri = yadtshell.uri.create(
            type=yadtshell.settings.HOST, host=unreachable_host.hostname)
        components[unreachable_host_uri] = unreachable_host
        return unreachable_host

    def convert_string_to_host(data, host=None):
        try:
            return json.loads(data)
        except Exception, e:
            logger.debug(
                '%s: %s, falling back to yaml parser' % (host, str(e)))
            return yaml.load(data, Loader=yaml_loader)

    host = None
    data = convert_string_to_host(protocol.data, protocol.component)
    if data == yadtshell.settings.DOWN:
        host = yadtshell.components.Host(protocol.component)
        host.state = yadtshell.settings.DOWN
    elif data == yadtshell.settings.UNKNOWN:
        host = yadtshell.components.Host(protocol.component)
        host.state = yadtshell.settings.UNKNOWN
    elif data is None:
        logging.getLogger(protocol.component).warning(
            'no data? strange...')
    elif "hostname" not in protocol.data:
        logging.getLogger(protocol.component).warning(
            'no hostname? strange...')
    else:
        host = yadtshell.components.Host(data['hostname'])
        for key, value in data.iteritems():
            setattr(host, key, value)
        host.state = ['update_needed', 'uptodate'][not host.next_artefacts]
    loc_type = yadtshell.util.determine_loc_type(host.hostname)
    host.loc_type = loc_type
    host.update_attributes_after_status()
    host.next_artefacts = getattr(host, 'next_artefacts', [])
    if host.next_artefacts is None:
        host.next_artefacts = []
    host.logger = logging.getLogger(host.uri)
    components[host.uri] = host
    return host


def status(hosts=None, include_artefacts=True, **kwargs):
    try:
        from yaml import CLoader as Loader
        logger.debug("using C implementation of yaml")
    except ImportError:
        from yaml import Loader
        logger.debug("using default yaml")
    try:
        import cPickle as pickle
        logger.debug("using C implementation of pickle")
    except ImportError:
        import pickle
        logger.debug("using default pickle")

    yadtshell.settings.ybc.connect()
    if type(hosts) is str:
        hosts = [hosts]

    try:
        os.remove(
            os.path.join(yadtshell.settings.OUT_DIR, 'current_state.components'))
    except OSError:
        pass

    if hosts:
        state_files = [os.path.join(yadtshell.settings.OUT_DIR, 'current_state_%s.yaml' % h)
                       for h in hosts]
    else:
        state_files = glob.glob(
            os.path.join(yadtshell.settings.OUT_DIR, 'current_state*'))
    for state_file in state_files:
        logger.debug('removing old state %(state_file)s' % locals())
        try:
            os.remove(state_file)
        except OSError, e:
            logger.warning('cannot remove %s:\n    %s' % (state_file, e))

    logger.debug('starting remote queries')

    if not hosts:
        hosts = yadtshell.settings.TARGET_SETTINGS['hosts']

    components = yadtshell.components.ComponentDict()

    def store_service_up(protocol):
        protocol.component.state = yadtshell.settings.UP
        return protocol

    def store_service_not_up(reason):
        reason.value.component.state = yadtshell.settings.STATE_DESCRIPTIONS.get(
            reason.value.exitCode, yadtshell.settings.UNKNOWN)
        return protocol

    def query_local_service(service):
        cmd = service.status()
        if isinstance(cmd, defer.Deferred):
            # TODO refactor: integrate all store_service_* cbs
            def store_service_state(state, service):
                service.state = yadtshell.settings.STATE_DESCRIPTIONS.get(
                    state, yadtshell.settings.UNKNOWN)
            cmd.addCallback(store_service_state, service)

            def handle_service_state_failure(failure, service):
                logger.debug('Failure while determining state of {0}. Exit code was {1}.'
                             .format(service.uri, failure.value.exitCode))
            cmd.addErrback(handle_service_state_failure, service)
            return cmd
        query_protocol = yadtshell.twisted.YadtProcessProtocol(
            service.uri, cmd)
        query_protocol.deferred = defer.Deferred()
        reactor.spawnProcess(
            query_protocol, '/bin/sh', ['/bin/sh'], os.environ)
        query_protocol.component = service
        query_protocol.deferred.addCallbacks(
            store_service_up, store_service_not_up)
        return query_protocol.deferred

    def initialize_services(host):
        services = getattr(host, 'services', set())

        if yadtshell.util.not_up(host.state):
            return host
        host.defined_services = []
        for settings in services:
            if type(settings) is str or not settings:
                name = settings
                settings = services.get(settings, None)
                if settings:
                    service_class = settings.get('class', 'Service')
                else:
                    service_class = 'Service'
            else:
                name = settings.keys()[0]
                settings = settings[name]
                service_class = settings.get('class', 'Service')

            service = None
            for module_name in sys.modules.keys()[:]:
                if service:
                    break
                for classname, clazz in inspect.getmembers(sys.modules[module_name], inspect.isclass):
                    if classname == service_class:
                        service = clazz(host, name, settings)
                        break
            if not service:
                host.logger.debug(
                    '%s not a standard service, searching class' % service_class)
                clazz = None
                try:
                    host.logger.debug('fallback 1: checking loaded modules')
                    clazz = eval(service_class)
                except:
                    pass

                def get_class(service_class):
                    module_name, class_name = service_class.rsplit('.', 1)
                    host.logger.debug('trying to load module %s' % module_name)
                    __import__(module_name)
                    m = sys.modules[module_name]
                    return getattr(m, class_name)

                if not clazz:
                    try:
                        host.logger.debug(
                            'fallback 2: trying to load module myself')
                        clazz = get_class(service_class)
                    except Exception, e:
                        host.logger.debug(e)
                if not clazz:
                    try:
                        host.logger.debug(
                            'fallback 3: trying to lookup %s in legacies' % service_class)
                        import legacies
                        mapped_service_class = legacies.MAPPING_OLD_NEW_SERVICECLASSES.get(
                            service_class, service_class)
                        clazz = get_class(mapped_service_class)
                        host.logger.info(
                            'deprecation info: class %s was mapped to %s' %
                            (service_class, mapped_service_class))
                    except Exception, e:
                        host.logger.debug(e)

                if not clazz:
                    raise Exception(
                        'cannot find class %(service_class)s' % locals())

                try:
                    service = clazz(host, name, settings)
                except Exception, e:
                    host.logger.exception(e)
            if not service:
                raise Exception(
                    'cannot instantiate class %(service_class)s' % locals())
            components[service.uri] = service
            service.fqdn = host.fqdn
            service.needs = getattr(service, 'needs', set())
            service.needs.add(host.uri)
            host.defined_services.append(service)
        return host

    def add_local_state(host):
        local_state = []
        for service in getattr(host, 'defined_services', []):
            if getattr(service, 'state_handling', None) == 'serverside':
                if hasattr(service, 'prepare'):
                    service.prepare(host)
                if hasattr(service, 'get_local_service_collector'):
                    global local_service_collector
                    local_service_collector = service.get_local_service_collector(
                    )
                q = query_local_service(service)
                local_state.append(q)

        if local_state:
            dl = defer.DeferredList(local_state)
            dl.addCallback(lambda _: host)
            return dl
        return host

    def initialize_artefacts(host):
        try:
            for version in getattr(host, 'current_artefacts', []):
                artefact = yadtshell.components.Artefact(
                    host, version, version)
                artefact.state = yadtshell.settings.INSTALLED
                components[artefact.uri] = artefact
        except TypeError:
            type_, value_, traceback_ = sys.exc_info()
            traceback.format_tb(traceback_)

        try:
            for version in getattr(host, 'current_artefacts', []):
                uri = yadtshell.uri.create(
                    yadtshell.settings.ARTEFACT, host.host, version)
                artefact = components.get(
                    uri, yadtshell.components.MissingComponent(uri))
                artefact.revision = yadtshell.settings.CURRENT
                current_uri = yadtshell.uri.create(
                    yadtshell.settings.ARTEFACT, host.host, artefact.name + '/' + yadtshell.settings.CURRENT)
                components[uri] = artefact
                components[current_uri] = artefact
        except TypeError:
            pass

        try:
            for version in getattr(host, 'next_artefacts', set()):
                artefact = yadtshell.components.Artefact(
                    host, version, version)
                artefact.state = yadtshell.settings.INSTALLED
                artefact.revision = yadtshell.settings.NEXT
                components[artefact.uri] = artefact
        except TypeError:
            pass
        try:
            for version in getattr(host, 'next_artefacts', []):
                uri = yadtshell.uri.create(
                    yadtshell.settings.ARTEFACT, host.host, version)
                artefact = components.get(
                    uri, yadtshell.components.MissingComponent(uri))
                artefact.revision = yadtshell.settings.NEXT
                next_uri = yadtshell.uri.create(
                    yadtshell.settings.ARTEFACT, host.host, artefact.name + '/' + yadtshell.settings.NEXT)
                components[uri] = artefact
                components[next_uri] = artefact
                host.logger.debug('adding %(uri)s and %(next_uri)s' % locals())
        except TypeError:
            pass
        return host

    def check_responses(responses):
        logger.debug('check_responses')
        logger.debug(responses)
        all_ok = True
        for ok, response in responses:
            if not ok:
                logger.error(response)
                all_ok = False
        if not all_ok:
            raise Exception('errors occured during status')

    def build_unified_dependencies_tree(ignored):
        logger.debug('building unified dependencies tree')

        for component in components.values():
            component.logger = None

        components._add_when_missing_ = True
        logger.debug('wiring components')
        for component in components.values():
            for needed in getattr(component, 'needs', []):
                try:
                    needed_component = components[needed]
                    if not hasattr(needed_component, 'needed_by'):
                        needed_component.needed_by = set()
                    needed_component.needed_by.add(component.uri)
                    component.needs.remove(needed)
                    component.needs.add(needed_component.uri)
                except (KeyError, AttributeError), e:
                    logger.debug('needed: ' + needed)
                    raise e
        components._add_when_missing_ = False

        for component in components.values():
            for dependent in getattr(component, 'needed_by', []):
                try:
                    dependent_component = components[dependent]
                    dependent_component.needs.add(component.uri)
                except KeyError, ke:
                    logger.warning("unknown dependent key " + str(ke))

        compute_dependency_scores(components)

        def _open_component_file(component_type):
            return open(os.path.join(yadtshell.settings.OUT_DIR, component_type), 'w')

        component_files = {
            yadtshell.settings.ARTEFACT: _open_component_file('artefacts'),
            yadtshell.settings.SERVICE: _open_component_file('services'),
            yadtshell.settings.HOST: _open_component_file('hosts'),
        }
        for component in components.values():
            print >> component_files[component.type], component.uri

        for f in component_files.values():
            f.close()

        f = _open_component_file('current_state.components')
        pickle.dump(components, f)
        f.close()

        groups = []
        he = HostExpander()
        for grouped_hosts in yadtshell.settings.TARGET_SETTINGS['original_hosts']:
            hosts = []
            for hostname in he.expand(grouped_hosts):
                services = []
                host = components['host://%s' % hostname]

                host_services = getattr(host, 'defined_services', [])
                host_services.sort(key=lambda s: s.dependency_score)

                for service in host_services:
                    services.append({
                        'uri': service.uri,
                        'name': service.name,
                        'state': service.state
                    })

                artefacts = []
                for artefact in sorted(getattr(host, 'handled_artefacts', [])):
                    name, version = artefact.split('/')
                    artefacts.append({
                        'uri': 'artefact://%s/%s' % (hostname, name),
                        'name': name,
                        'current': version
                    })

                host = {
                    'name': hostname,
                    'services': services,
                    'artefacts': artefacts
                }
                hosts.append(host)
            groups.append(hosts)
        yadtshell.settings.ybc.sendFullUpdate(
            groups, tracking_id=yadtshell.settings.tracking_id)

        status_line = yadtshell.util.get_status_line(components)
        logger.debug('\nstatus: %s' % status_line)
        print status_line
        f = open(os.path.join(yadtshell.settings.OUT_DIR, 'statusline'), 'w')
        f.write('\n'.join(['', status_line]))
        f.close()

    def show_still_pending(deferreds):
        pending = [d.name for d in deferreds if not d.called]
        if pending:
            logger.info('pending: %s' % ' '.join(pending))
            reactor.callLater(10, show_still_pending, deferreds)

    def report_connection_error(failure):
        if failure.value.exitCode == 255:
            logger.critical(
                'ssh: cannot reach %s\n\t passwordless ssh not configured? network problems?' %
                failure.value.component)
            return yadtshell.components.UnreachableHost(failure.value.component)
        return failure

    def notify_collector(ignored):
        global local_service_collector
        if local_service_collector:
            logger.debug("collected services: %s " %
                         ", ".join(local_service_collector.services))
            return local_service_collector.notify()

    pi = yadtshell.twisted.ProgressIndicator()

    deferreds = []
    for host in hosts:
        deferred = query_status(host, pi)
        deferred.addErrback(report_connection_error)
        deferred.addCallback(create_host, components, Loader)

        deferred.addCallback(initialize_services)
        deferred.addCallback(add_local_state)
        deferred.addCallback(initialize_artefacts)
        deferred.addErrback(yadtshell.twisted.report_error, logger.error)
        deferreds.append(deferred)

    reactor.callLater(10, show_still_pending, deferreds)

    dl = defer.DeferredList(deferreds)
    dl.addCallback(check_responses)
    dl.addCallback(notify_collector)
    dl.addCallback(build_unified_dependencies_tree)
    dl.addCallback(yadtshell.info, components=components)
    dl.addErrback(yadtshell.twisted.report_error,
                  logger.error, include_stacktrace=False)

    return dl
