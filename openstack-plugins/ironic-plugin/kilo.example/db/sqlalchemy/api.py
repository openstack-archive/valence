# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""SQLAlchemy storage backend."""

import collections
import datetime

from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log
from oslo_utils import strutils
from oslo_utils import timeutils
from oslo_utils import uuidutils
from sqlalchemy.orm.exc import NoResultFound
from ironic.common import exception
from ironic.common.i18n import _
from ironic.common.i18n import _LW
from ironic.common import states
from ironic.common import utils
from ironic.db import api
from ironic.db.sqlalchemy import models
from sqlalchemy.sql import func

CONF = cfg.CONF
CONF.import_opt('heartbeat_timeout',
                'ironic.conductor.manager', group='conductor')

LOG = log.getLogger(__name__)

_FACADE = None

DRIVER_RSA_PODM_INSTANCE_TYPE = 'intel_rsa_podm'
DRIVER_XCLARITY_INSTANCE_TYPE = 'lenovo_xclarity'
RSA_NODE_TYPE_COMPOSED_SERVER = 'Logical'
RSA_CHASSIS_TYPE_RACK = "RACK"


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def add_identity_filter(query, value):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if strutils.is_int_like(value):
        return query.filter_by(id=value)
    elif uuidutils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidIdentity(identity=value)


def add_port_filter(query, value):
    """Adds a port-specific filter to a query.

    Filters results by address, if supplied value is a valid MAC
    address. Otherwise attempts to filter results by identity.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if utils.is_valid_mac(value):
        return query.filter_by(address=value)
    else:
        return add_identity_filter(query, value)


def add_port_filter_by_node(query, value):
    if strutils.is_int_like(value):
        return query.filter_by(node_id=value)
    else:
        query = query.join(models.Node,
                           models.Port.node_id == models.Node.id)
        return query.filter(models.Node.uuid == value)


def add_node_filter_by_chassis(query, value):
    if strutils.is_int_like(value):
        return query.filter_by(chassis_id=value)
    else:
        query = query.join(models.Chassis,
                           models.Node.chassis_id == models.Chassis.id)
        return query.filter(models.Chassis.uuid == value)


def _paginate_query(model, limit=None, marker=None,
                    sort_key=None, sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = db_utils.paginate_query(query, model, limit, sort_keys,
                                        marker=marker, sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise exception.InvalidParameterValue(_(
            'The sort_key value "%(key)s" is an invalid field for sorting')
                                              % {'key': sort_key})
    return query.all()


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def _add_xclarity_filters(self, query, filters):
        if filters is None:
            filters = []

        if 'id' in filters:
            query = query.filter_by(id=filters['id'])
        if 'ipaddress' in filters:
            query = query.filter_by(ipaddress=filters['ipaddress'])
        if 'username' in filters:
            query = query.filter_by(username=filters['username'])
        if 'state' in filters:
            query = query.filter_by(state=filters['state'])

        return query

    def _add_subscription_filters(self, query, filters):
        if filters is None:
            filters = []

        if 'id' in filters:
            query = query.filter_by(id=filters['id'])
        if 'tenant_id' in filters:
            query = query.filter_by(ipaddress=filters['tenant_id'])
        if 'tenant_name' in filters:
            query = query.filter_by(username=filters['tenant_name'])

        return query

    def _add_nodes_filters(self, query, filters):
        if filters is None:
            filters = []

        if 'chassis_uuid' in filters:
            # get_chassis_by_uuid() to raise an exception if the chassis
            # is not found
            chassis_obj = self.get_chassis_by_uuid(filters['chassis_uuid'])
            query = query.filter_by(chassis_id=chassis_obj.id)
        if 'associated' in filters:
            if filters['associated']:
                query = query.filter(models.Node.instance_uuid != None)
            else:
                query = query.filter(models.Node.instance_uuid == None)
        if 'reserved' in filters:
            if filters['reserved']:
                query = query.filter(models.Node.reservation != None)
            else:
                query = query.filter(models.Node.reservation == None)
        if 'maintenance' in filters:
            query = query.filter_by(maintenance=filters['maintenance'])
        if 'driver' in filters:
            query = query.filter_by(driver=filters['driver'])
        if 'provision_state' in filters:
            query = query.filter_by(provision_state=filters['provision_state'])
        if 'provisioned_before' in filters:
            limit = timeutils.utcnow() - \
                    datetime.timedelta(seconds=filters['provisioned_before'])
            query = query.filter(models.Node.provision_updated_at < limit)
        if 'inspection_started_before' in filters:
            limit = ((timeutils.utcnow()) -
                     (datetime.timedelta(
                         seconds=filters['inspection_started_before'])))
            query = query.filter(models.Node.inspection_started_at < limit)

        return query

    """
    node db api functions
    """

    def get_nodeinfo_list(self, columns=None, filters=None, limit=None,
                          marker=None, sort_key=None, sort_dir=None):
        # list-ify columns default values because it is bad form
        # to include a mutable list in function definitions.
        if columns is None:
            columns = [models.Node.id]
        else:
            columns = [getattr(models.Node, c) for c in columns]

        query = model_query(*columns, base_model=models.Node)
        query = self._add_nodes_filters(query, filters)
        return _paginate_query(models.Node, limit, marker,
                               sort_key, sort_dir, query)

    def get_node_list(self, filters=None, limit=None, marker=None,
                      sort_key=None, sort_dir=None):
        query = model_query(models.Node)
        query = self._add_nodes_filters(query, filters)
        return _paginate_query(models.Node, limit, marker,
                               sort_key, sort_dir, query)

    def reserve_node(self, tag, node_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Node, session=session)
            query = add_identity_filter(query, node_id)
            # be optimistic and assume we usually create a reservation
            count = query.filter_by(reservation=None).update(
                {'reservation': tag}, synchronize_session=False)
            try:
                node = query.one()
                if count != 1:
                    # Nothing updated and node exists. Must already be
                    # locked.
                    raise exception.NodeLocked(node=node_id,
                                               host=node['reservation'])
                return node
            except NoResultFound:
                raise exception.NodeNotFound(node_id)

    def release_node(self, tag, node_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Node, session=session)
            query = add_identity_filter(query, node_id)
            # be optimistic and assume we usually release a reservation
            count = query.filter_by(reservation=tag).update(
                {'reservation': None}, synchronize_session=False)
            try:
                if count != 1:
                    node = query.one()
                    if node['reservation'] is None:
                        raise exception.NodeNotLocked(node=node_id)
                    else:
                        raise exception.NodeLocked(node=node_id,
                                                   host=node['reservation'])
            except NoResultFound:
                raise exception.NodeNotFound(node_id)

    def create_node(self, values):
        # ensure defaults are present for new nodes
        if 'uuid' not in values:
            values['uuid'] = uuidutils.generate_uuid()
        if 'power_state' not in values:
            values['power_state'] = states.NOSTATE
        if 'provision_state' not in values:
            # TODO(deva): change this to ENROLL
            values['provision_state'] = states.AVAILABLE

        node = models.Node()
        node.update(values)
        try:
            node.save()
        except db_exc.DBDuplicateEntry as exc:
            if 'name' in exc.columns:
                raise exception.DuplicateName(name=values['name'])
            elif 'instance_uuid' in exc.columns:
                raise exception.InstanceAssociated(
                    instance_uuid=values['instance_uuid'],
                    node=values['uuid'])
            raise exception.NodeAlreadyExists(uuid=values['uuid'])
        return node

    def get_node_by_id(self, node_id):
        query = model_query(models.Node).filter_by(id=node_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.NodeNotFound(node=node_id)

    def get_node_by_uuid(self, node_uuid):
        query = model_query(models.Node).filter_by(uuid=node_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.NodeNotFound(node=node_uuid)

    def get_node_by_name(self, node_name):
        query = model_query(models.Node).filter_by(name=node_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.NodeNotFound(node=node_name)

    def get_node_by_instance(self, instance):
        if not uuidutils.is_uuid_like(instance):
            raise exception.InvalidUUID(uuid=instance)

        query = (model_query(models.Node)
                 .filter_by(instance_uuid=instance))

        try:
            result = query.one()
        except NoResultFound:
            raise exception.InstanceNotFound(instance=instance)

        return result

    def destroy_node(self, node_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Node, session=session)
            query = add_identity_filter(query, node_id)

            try:
                node_ref = query.one()
            except NoResultFound:
                raise exception.NodeNotFound(node=node_id)

            # Get node ID, if an UUID was supplied. The ID is
            # required for deleting all ports, attached to the node.
            if uuidutils.is_uuid_like(node_id):
                node_id = node_ref['id']

            port_query = model_query(models.Port, session=session)
            port_query = add_port_filter_by_node(port_query, node_id)
            port_query.delete()

            query.delete()

    def update_node(self, node_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Node.")
            raise exception.InvalidParameterValue(err=msg)

        try:
            return self._do_update_node(node_id, values)
        except db_exc.DBDuplicateEntry as e:
            if 'name' in e.columns:
                raise exception.DuplicateName(name=values['name'])
            elif 'uuid' in e.columns:
                raise exception.NodeAlreadyExists(uuid=values['uuid'])
            elif 'instance_uuid' in e.columns:
                raise exception.InstanceAssociated(
                    instance_uuid=values['instance_uuid'],
                    node=node_id)
            else:
                raise e

    def _do_update_node(self, node_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Node, session=session)
            query = add_identity_filter(query, node_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.NodeNotFound(node=node_id)

            # Prevent instance_uuid overwriting
            if values.get("instance_uuid") and ref.instance_uuid:
                raise exception.NodeAssociated(node=node_id,
                                               instance=ref.instance_uuid)

            if 'provision_state' in values:
                values['provision_updated_at'] = timeutils.utcnow()
                if values['provision_state'] == states.INSPECTING:
                    values['inspection_started_at'] = timeutils.utcnow()
                    values['inspection_finished_at'] = None
                elif (ref.provision_state == states.INSPECTING and
                              values['provision_state'] == states.MANAGEABLE):
                    values['inspection_finished_at'] = timeutils.utcnow()
                    values['inspection_started_at'] = None
                elif (ref.provision_state == states.INSPECTING and
                              values['provision_state'] == states.INSPECTFAIL):
                    values['inspection_started_at'] = None

            ref.update(values)
        return ref

    """
    port db api functions
    """

    def get_port_by_id(self, port_id):
        query = model_query(models.Port).filter_by(id=port_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PortNotFound(port=port_id)

    def get_port_by_uuid(self, port_uuid):
        query = model_query(models.Port).filter_by(uuid=port_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PortNotFound(port=port_uuid)

    def get_port_by_address(self, address):
        query = model_query(models.Port).filter_by(address=address)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PortNotFound(port=address)

    def get_port_list(self, limit=None, marker=None,
                      sort_key=None, sort_dir=None):
        return _paginate_query(models.Port, limit, marker,
                               sort_key, sort_dir)

    def get_ports_by_node_id(self, node_id, limit=None, marker=None,
                             sort_key=None, sort_dir=None):
        query = model_query(models.Port)
        query = query.filter_by(node_id=node_id)
        return _paginate_query(models.Port, limit, marker,
                               sort_key, sort_dir, query)

    def create_port(self, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()
        port = models.Port()
        port.update(values)
        try:
            port.save()
        except db_exc.DBDuplicateEntry as exc:
            if 'address' in exc.columns:
                raise exception.MACAlreadyExists(mac=values['address'])
            raise exception.PortAlreadyExists(uuid=values['uuid'])
        return port

    def update_port(self, port_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Port.")
            raise exception.InvalidParameterValue(err=msg)

        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Port, session=session)
                query = add_port_filter(query, port_id)
                ref = query.one()
                ref.update(values)
        except NoResultFound:
            raise exception.PortNotFound(port=port_id)
        except db_exc.DBDuplicateEntry:
            raise exception.MACAlreadyExists(mac=values['address'])
        return ref

    def destroy_port(self, port_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Port, session=session)
            query = add_port_filter(query, port_id)
            count = query.delete()
            if count == 0:
                raise exception.PortNotFound(port=port_id)

    """
    chassis db api functions
    """

    def get_chassis_by_id(self, chassis_id):
        query = model_query(models.Chassis).filter_by(id=chassis_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ChassisNotFound(chassis=chassis_id)

    def get_chassis_by_uuid(self, chassis_uuid):
        query = model_query(models.Chassis).filter_by(uuid=chassis_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ChassisNotFound(chassis=chassis_uuid)

    def get_chassis_list(self, limit=None, marker=None,
                         sort_key=None, sort_dir=None):
        return _paginate_query(models.Chassis, limit, marker,
                               sort_key, sort_dir)

    def create_chassis(self, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()
        chassis = models.Chassis()
        chassis.update(values)
        try:
            chassis.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ChassisAlreadyExists(uuid=values['uuid'])
        return chassis

    def update_chassis(self, chassis_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Chassis.")
            raise exception.InvalidParameterValue(err=msg)

        session = get_session()
        with session.begin():
            query = model_query(models.Chassis, session=session)
            query = add_identity_filter(query, chassis_id)

            count = query.update(values)
            if count != 1:
                raise exception.ChassisNotFound(chassis=chassis_id)
            ref = query.one()
        return ref

    def destroy_chassis(self, chassis_id):
        def chassis_not_empty(session):
            """Checks whether the chassis does not have nodes."""

            query = model_query(models.Node, session=session)
            query = add_node_filter_by_chassis(query, chassis_id)

            return query.count() != 0

        session = get_session()
        with session.begin():
            if chassis_not_empty(session):
                raise exception.ChassisNotEmpty(chassis=chassis_id)

            query = model_query(models.Chassis, session=session)
            query = add_identity_filter(query, chassis_id)

            count = query.delete()
            if count != 1:
                raise exception.ChassisNotFound(chassis=chassis_id)

    """
    conductor db api functions
    """

    def register_conductor(self, values, update_existing=False):
        session = get_session()
        with session.begin():
            query = (model_query(models.Conductor, session=session)
                     .filter_by(hostname=values['hostname']))
            try:
                ref = query.one()
                if ref.online is True and not update_existing:
                    raise exception.ConductorAlreadyRegistered(
                        conductor=values['hostname'])
            except NoResultFound:
                ref = models.Conductor()
            ref.update(values)
            # always set online and updated_at fields when registering
            # a conductor, especially when updating an existing one
            ref.update({'updated_at': timeutils.utcnow(),
                        'online': True})
            ref.save(session)
        return ref

    def get_conductor(self, hostname):
        try:
            return (model_query(models.Conductor)
                    .filter_by(hostname=hostname, online=True)
                    .one())
        except NoResultFound:
            raise exception.ConductorNotFound(conductor=hostname)

    def unregister_conductor(self, hostname):
        session = get_session()
        with session.begin():
            query = (model_query(models.Conductor, session=session)
                     .filter_by(hostname=hostname, online=True))
            count = query.update({'online': False})
            if count == 0:
                raise exception.ConductorNotFound(conductor=hostname)

    def touch_conductor(self, hostname):
        session = get_session()
        with session.begin():
            query = (model_query(models.Conductor, session=session)
                     .filter_by(hostname=hostname))
            # since we're not changing any other field,manually set updated_at
            # and since we're heartbeating, make sure that online=True
            count = query.update({'updated_at': timeutils.utcnow(),
                                  'online': True})
            if count == 0:
                raise exception.ConductorNotFound(conductor=hostname)

    def clear_node_reservations_for_conductor(self, hostname):
        session = get_session()
        nodes = []
        with session.begin():
            query = model_query(models.Node, session=session).filter_by(
                reservation=hostname)
            nodes = [node['uuid'] for node in query]
            query.update({'reservation': None})

        if nodes:
            nodes = ', '.join(nodes)
            LOG.warn(_LW('Cleared reservations held by %(hostname)s: '
                         '%(nodes)s'), {'hostname': hostname, 'nodes': nodes})

    """
    xclarity db api functions
    """

    def get_active_driver_dict(self, interval=None):
        if interval is None:
            interval = CONF.conductor.heartbeat_timeout

        limit = timeutils.utcnow() - datetime.timedelta(seconds=interval)
        result = (model_query(models.Conductor)
                  .filter_by(online=True)
                  .filter(models.Conductor.updated_at >= limit)
                  .all())

        # build mapping of drivers to the set of hosts which support them
        d2c = collections.defaultdict(set)
        for row in result:
            for driver in row['drivers']:
                d2c[driver].add(row['hostname'])
        return d2c

    def get_xclarity_by_ipaddress(self, xclarity_ipaddress):
        query = model_query(models.xClarityInstance).filter_by(
            ipaddress=xclarity_ipaddress)
        try:
            return query.one()
        except NoResultFound:
            raise exception.XClarityNotFound(xclarity=xclarity_ipaddress)

    def get_xclarity_by_id(self, xclarity_id):
        query = model_query(models.xClarityInstance).filter_by(id=xclarity_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.XClarityNotFound(xclarity=xclarity_id)

    def get_xclarity_list(self, filters=None, limit=None, marker=None,
                          sort_key=None, sort_dir=None):
        query = model_query(models.xClarityInstance)
        query = self._add_xclarity_filters(query, filters)
        return _paginate_query(models.xClarityInstance, limit, marker,
                               sort_key, sort_dir, query)

    def create_xclarity(self, values):
        xclarity = models.xClarityInstance()
        xclarity.update(values)
        try:
            xclarity.save()
        except db_exc.DBDuplicateEntry as exc:
            raise exception.XClarityAlreadyExists(
                ipaddress=values['ipaddress'])
        return xclarity

    def destroy_xclarity(self, xclarity_id):
        session = get_session()
        with session.begin():
            query = model_query(models.xClarityInstance, session=session)
            filters = {}
            filters['id'] = xclarity_id
            query = self._add_xclarity_filters(query, filters)
            count = query.delete()
            if count == 0:
                raise exception.XClarityNotFound(xclarity=xclarity_id)

    def update_xclarity(self, xclarity_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.xClarityInstance, session=session)
                filters = {}
                filters['id'] = xclarity_id
                query = self._add_xclarity_filters(query, filters)
                ref = query.one()
                ref.update(values)
        except NoResultFound:
            raise exception.XClarityNotFound(xclarity=xclarity_id)
        except db_exc.DBDuplicateEntry:
            raise exception.XClarityAlreadyExists(
                ipaddress=values['ipaddress'])
        return ref

    """
    subscription db api functions
    """

    def get_subscription_by_id(self, subscription_id):
        query = model_query(models.Subscription).filter_by(id=subscription_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.SubscriptionNotFound(subscription=subscription_id)

    def get_subscription_list(self, filters=None, limit=None, marker=None,
                              sort_key=None, sort_dir=None):
        query = model_query(models.Subscription)
        query = self._add_subscription_filters(query, filters)
        return _paginate_query(models.Subscription, limit, marker,
                               sort_key, sort_dir, query)

    def create_subscription(self, values):
        subscription = models.Subscription()
        subscription.update(values)
        try:
            subscription.save()
        except db_exc.DBDuplicateEntry as exc:
            raise exception.SubscriptionAlreadyExists(
                tenant_id=values['tenant_id'])
        return subscription

    def destroy_subscription(self, subscription_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Subscription, session=session)
            filters = {}
            filters['id'] = subscription_id
            query = self._add_subscription_filters(query, filters)
            count = query.delete()
            if count == 0:
                raise exception.SubscriptionNotFound(subscription=
                                                     subscription_id)

    def update_subscription(self, subscription_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Subscription, session=session)
                filters = {}
                filters['id'] = subscription_id
                query = self._add_subscription_filters(query, filters)
                ref = query.one()
                ref.update(values)
        except NoResultFound:
            raise exception.SubscriptionNotFound(subscription=subscription_id)
        except db_exc.DBDuplicateEntry:
            raise exception.SubscriptionAlreadyExists(tenant_id=
                                                      values['tenant_id'])
        return ref

    """
    driver_instance_server (pod_manager) db api functions
    """

    def create_pod_manager(self, values):
        pod_manager = models.PodManager()
        pod_manager.update(values)
        try:
            pod_manager.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PodManagerAlreadyExist(id=values['id'])
        return pod_manager

    def update_pod_manager(self, pod_manager_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.PodManager,
                                    session=session).filter_by(
                    id=pod_manager_id)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.PodManagerNotFound(pod_manager=pod_manager_id)
        except db_exc.DBDuplicateEntry:
            raise exception.PodManagerAlreadyExist(
                pod_manager=values['tenant_id'])
        return ref

    def destroy_pod_manager(self, pod_manager_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.PodManager).filter_by(
                    id=pod_manager_id)
                query.delete()
        except NoResultFound:
            raise exception.PodManagerNotFound(id=pod_manager_id)

    def get_pod_manager_list(self, filters=None, limit=None, marker=None,
                             sort_key=None, sort_dir=None):
        query = model_query(models.PodManager)
        if filters is not None:
            filters['type'] = DRIVER_RSA_PODM_INSTANCE_TYPE
        else:
            filters = {'type': DRIVER_RSA_PODM_INSTANCE_TYPE}
        query = self._add_xclarity_filters(query, filters)
        return _paginate_query(models.PodManager, limit, marker,
                               sort_key, sort_dir, query)

    def get_pod_manager_by_id(self, pod_manager_id):
        query = model_query(models.PodManager).filter_by(id=pod_manager_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PodManagerNotFound(pod_manager=pod_manager_id)

    def get_pod_manager_by_ip(self, pod_manager_ip):
        query = model_query(models.PodManager).filter_by(
            ipaddress=pod_manager_ip)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PodManagerNotFound(pod_manager=pod_manager_ip)

    """
    RSA chassis db api functions
    """

    def get_rsa_chassis_list_by_pod_and_type(self, pod_id, chassis_type,
                                             limit=None, marker=None,
                                             sort_key=None, sort_dir=None):
        query = model_query(models.RSAChassis).filter_by(pod_id=pod_id,
                                                         type=chassis_type)
        # query = model_query(models.RSAChassis).filter(pod_id=pod_id,
        # RSAChassis.chassis_type!='Rack')
        return _paginate_query(models.RSAChassis, limit, marker, sort_key,
                               sort_dir, query)

    def get_rsa_chassis_by_id(self, chassis_id):
        query = model_query(models.RSAChassis).filter_by(id=chassis_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.RsaChassisNotFound(rsa_chassis=chassis_id)

    def get_rsa_chassis_by_url(self, url):
        query = model_query(models.RSAChassis).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.RsaChassisNotFound(rsa_chassis=url)

    def create_rsa_chassis(self, values):
        rsa_chassis = models.RSAChassis()
        rsa_chassis.update(values)
        try:
            rsa_chassis.save()
        except db_exc.DBDuplicateEntry:
            raise exception.RsaChassisAlreadyExist(rsa_chassis=values['url'])
        return rsa_chassis

    def update_rsa_chassis(self, url, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.RSAChassis).filter_by(url=url)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.RsaChassisNotFound(rsa_chassis=url)
        return ref

    def destroy_rsa_chassis(self, pod_id, chassis_type):
        session = get_session()
        try:
            with session.begin():
                if chassis_type is not None:
                    query = model_query(models.RSAChassis) \
                        .filter_by(type=chassis_type, pod_id=pod_id)
                else:
                    query = model_query(models.RSAChassis).filter_by(
                        pod_id=pod_id)
                query.delete()
        except NoResultFound:
            raise exception.RsaChassisNotFound(rsa_chassis=chassis_type)

    def get_rack_resource(self, pod_id, rack_id):
        pod_type = model_query(models.PodManager).filter_by(
            id=pod_id).one().type
        rack_name = model_query(models.RSAChassis.name).filter_by(id=rack_id)
        # drawer resource
        drawer_query = model_query(models.RSAChassis).filter_by(type='Drawer',
                                                                pod_id=pod_id)
        drawer_sum = drawer_query.filter(
            models.RSAChassis.location.contains(rack_name)).count()
        # compuer_system resource
        if pod_type == "INTEL-COMMON":
            compuer_system_query = model_query(
                models.ComputerSystem).filter_by(pod_id=pod_id)
            compuer_system_sum = compuer_system_query.filter(
                models.ComputerSystem.location.contains(rack_name)).count()
        else:
            compuer_system_query = model_query(
                models.ComputerSystem).filter_by(pod_id=pod_id)
            compuer_system_sum = compuer_system_query.filter(
                models.ComputerSystem.location.contains(str(rack_id))).count()
        # switch resource
        switch_query = model_query(models.Switch).filter_by(pod_id=pod_id)
        switch_sum = switch_query.filter(
            models.Switch.location.contains(rack_name)).count()
        return {'drawer_sum': drawer_sum,
                'computer_system_sum': compuer_system_sum,
                'ethernet_switch_sum': switch_sum}

    def get_rack_computer_systems(self, pod_id, chassis, chassis_id):
        pod_type = model_query(models.PodManager).filter_by(
            id=pod_id).one().type
        query = model_query(models.ComputerSystem.name,
                            models.ComputerSystem.id,
                            models.ComputerSystem.location).filter_by(
            pod_id=pod_id)
        if pod_type == "INTEL-COMMON":
            computer_systems = query.filter(
                models.ComputerSystem.location.contains(chassis))
        else:
            computer_systems = query.filter(
                models.ComputerSystem.location.contains(str(chassis_id)))
        return computer_systems

    """
    rack_view db api functions
    """

    def get_rack_view_by_rack_id(self, rack_id):
        query = model_query(models.RackView).filter_by(rack_id=rack_id)
        return _paginate_query(models.RackView,
                               sort_key=models.RackView.begin_at, query=query)

    """
    cpu db api functions
    """

    def get_cpu_by_id(self, cpu_id):
        query = model_query(models.CPU).filter_by(id=cpu_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.CPUNotFound(cpu=cpu_id)

    def get_cpu_by_url(self, url):
        query = model_query(models.CPU).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.CPUNotFound(cpu=url)

    def get_node_cpu_list(self, rsa_node_id, limit=None, marker=None,
                          sort_key=None, sort_dir=None):
        query = model_query(models.CPU).filter_by(
            computer_system_id=rsa_node_id)
        return _paginate_query(models.CPU, limit, marker, sort_key, sort_dir,
                               query)

    def get_cpu_list(self, limit=None, marker=None, sort_key=None,
                     sort_dir=None):
        query = model_query(models.CPU)
        return query.all()

    def get_cpu_sum_by_systems(self, system_id_list):
        try:
            cpu_sum = model_query(models.CPU).filter(
                models.CPU.computer_system_id.in_(system_id_list)).count()
            return cpu_sum
        except NoResultFound:
            raise exception.CPUNotFound(cpu=system_id_list)

    def update_cpu(self, url, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.CPU).filter_by(url=url)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.CPUNotFound(cpu=url)
        return ref

    def create_cpu(self, values):
        cpu = models.CPU()
        cpu.update(values)
        try:
            cpu.save()
        except db_exc.DBDuplicateEntry:
            raise exception.CPUAlreadyExist(cpu=values['url'])
        return cpu

    def destroy_cpu(self, computer_system_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.CPU).filter_by(
                    computer_system_id=computer_system_id)
                query.delete()
        except NoResultFound:
            raise exception.CPUNotFound()

    """
    memory db api functions
    """

    def get_memory_by_id(self, memory_id):
        query = model_query(models.Memory).filter_by(id=memory_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.MemoryNotFound(memory=memory_id)

    def get_memory_by_url(self, url):
        query = model_query(models.Memory).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.MemoryNotFound(memory=url)

    def get_node_memory_list(self, rsa_node_id, limit=None, marker=None,
                             sort_key=None, sort_dir=None):
        query = model_query(models.Memory).filter_by(
            computer_system_id=rsa_node_id)
        return _paginate_query(models.Memory, limit, marker, sort_key,
                               sort_dir, query)

    def get_mem_list(self, limit=None, marker=None, sort_key=None,
                     sort_dir=None):
        query = model_query(models.Memory)
        return query.all()

    def get_mem_sum_by_systems(self, system_id_list):
        try:
            query = model_query(func.sum(models.Memory.capacity_mb)).filter(
                models.Memory.computer_system_id.in_(system_id_list))
            size_sum = int(query.all()[0][0])
            return size_sum / 1024
        except NoResultFound:
            raise exception.MemoryNotFound(memory=system_id_list)

    def update_memory(self, url, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Memory).filter_by(url=url)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.MemoryNotFound(memory=url)
        return ref

    def create_memory(self, values):
        memory = models.Memory()
        memory.update(values)
        try:
            memory.save()
        except db_exc.DBDuplicateEntry:
            raise exception.MemoryAlreadyExist(memory=values['url'])
        return memory

    def destroy_mem(self, computer_system_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Memory).filter_by(
                    computer_system_id=computer_system_id)
                query.delete()
        except NoResultFound:
            raise exception.MemoryNotFound()

    """
    disk db instance entrance
    """

    def get_disk_by_id(self, disk_id):
        query = model_query(models.Disk).filter_by(id=disk_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.DiskNotFound(disk=disk_id)

    def get_disk_by_url(self, url):
        query = model_query(models.Disk).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.DiskNotFound(disk=url)

    def get_node_disk_list(self, rsa_node_id, limit=None, marker=None,
                           sort_key=None, sort_dir=None):
        query = model_query(models.Disk).filter_by(
            computer_system_id=rsa_node_id)
        return _paginate_query(models.Disk, limit, marker, sort_key, sort_dir,
                               query)

    def get_disk_list(self, limit=None, marker=None, sort_key=None,
                      sort_dir=None):
        query = model_query(models.Disk)
        return query.all()

    def get_disk_sum_by_systems(self, system_id_list):
        try:
            query = model_query(func.sum(models.Disk.size_gb)).filter(
                models.Disk.computer_system_id.in_(system_id_list))
            size_sum = int(query.all()[0][0])
            return size_sum
        except NoResultFound:
            raise exception.DiskNotFound(disk=system_id_list)

    def update_disk(self, url, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Disk).filter_by(url=url)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.DiskNotFound(disk=url)
        return ref

    def create_disk(self, values):
        disk = models.Disk()
        disk.update(values)
        try:
            disk.save()
        except db_exc.DBDuplicateEntry:
            raise exception.DiskAlreadyExist(disk=values['url'])
        return disk

    def destroy_disk(self, computer_system_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Disk).filter_by(
                    computer_system_id=computer_system_id)
                query.delete()
        except NoResultFound:
            raise exception.DiskNotFound()

    """
    switch (switch) db instance entrance
    """

    def get_switch_by_id(self, switch_id):
        query = model_query(models.Switch).filter_by(id=switch_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.SwitchNotFound(switch=switch_id)

    def get_switch_by_url(self, url):
        query = model_query(models.Switch).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.SwitchNotFound(switch=url)

    def get_pod_switch_list(self, pod_id, limit=None, marker=None,
                            sort_key=None, sort_dir=None):
        query = model_query(models.Switch).filter_by(pod_id=pod_id)
        return _paginate_query(models.Switch, limit, marker, sort_key,
                               sort_dir, query)

    def update_switch(self, url, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Switch).filter_by(url=url)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.SwitchNotFound(switch=url)
        return ref

    def create_switch(self, values):
        switch = models.Switch()
        switch.update(values)
        try:
            switch.save()
        except db_exc.DBDuplicateEntry:
            raise exception.SwitchAlreadyExist(switch=values['url'])
        return switch

    def destroy_switch(self, pod_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Switch).filter_by(pod_id=pod_id)
                query.delete()
        except NoResultFound:
            raise exception.SwitchNotFound()

    """
    computer_system db instance entrance
    """

    def get_computer_system_list(self, pod_id, limit=None, marker=None,
                                 sort_key=None, sort_dir=None):
        query = model_query(models.ComputerSystem).filter_by(pod_id=pod_id)
        return _paginate_query(models.ComputerSystem, limit, marker, sort_key,
                               sort_dir, query)

    def get_computer_system_by_id(self, computer_system_id):
        query = model_query(models.ComputerSystem).filter_by(
            id=computer_system_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputerSystemNotFound(
                ComputerSystem=computer_system_id)

    def get_computer_system_by_url(self, url):
        query = model_query(models.ComputerSystem).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputerSystemNotFound(ComputerSystem=url)

    def update_computer_system(self, computer_system_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.ComputerSystem).filter_by(
                    id=computer_system_id)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.ComputerSystemNotFound(
                ComputerSystem=computer_system_id)
        return ref

    def create_computer_system(self, values):
        computer_system = models.ComputerSystem()
        computer_system.update(values)
        try:
            computer_system.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ComputerSystemAlreadyExist(
                ComputerSystem=values['url'])
        return computer_system

    def destroy_computer_system(self, pod_id):
        # delete computer system and cpus,memorys,disks also!
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.ComputerSystem).filter_by(
                    pod_id=pod_id)
                system_ids = map(lambda system: system.id, query.all())
                query.delete()
                # delete cpus
                cpus_query = model_query(models.CPU).filter(
                    models.CPU.computer_system_id.in_(system_ids))
                cpus_query.delete(synchronize_session='fetch')
                # delete memorys
                mems_query = model_query(models.Memory).filter(
                    models.Memory.computer_system_id.in_(system_ids))
                mems_query.delete(synchronize_session='fetch')
                # delete disks
                disks_query = model_query(models.Disk).filter(
                    models.Disk.computer_system_id.in_(system_ids))
                disks_query.delete(synchronize_session='fetch')
                # delete interfaces
                interfaces_query = model_query(models.Interface).filter(
                    models.Interface.computer_system_id.in_(system_ids))
                interfaces_query.delete(synchronize_session='fetch')
        except NoResultFound:
            raise exception.ComputerSystemNotFound()

    """
    composed_node db instance entrance
    """

    def get_composed_node_list(self, pod_id, limit=None, marker=None,
                               sort_key=None, sort_dir=None):
        query = model_query(models.ComposedNode).filter_by(pod_id=pod_id)
        return _paginate_query(models.ComposedNode, limit, marker, sort_key,
                               sort_dir, query)

    def get_composed_node_by_id(self, composed_node_id):
        query = model_query(models.ComposedNode).filter_by(id=composed_node_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComposedNodeNotFound(ComposedNode=composed_node_id)

    def get_by_volume_id(self, volume_id):
        composed_node = model_query(models.ComposedNode.name,
                                    models.ComposedNode.id).filter(
            models.ComposedNode.volume_id.contains(volume_id))
        return composed_node

    def get_composed_node_by_system_id(self, system_id):
        query = model_query(models.ComposedNode.name,
                            models.ComposedNode.id).filter_by(
            computer_system_id=system_id)
        try:
            return query.one()
        except NoResultFound:
            return None

    def get_composed_node_by_url(self, url):
        query = model_query(models.ComposedNode).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComposedNodeNotFound(ComposedNode=url)

    def get_system_id_list(self, pod_id):
        id_list = model_query(
            models.ComposedNode.computer_system_id).filter_by(pod_id=pod_id)
        return id_list

    def update_composed_node(self, composed_node_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.ComposedNode).filter_by(
                    id=composed_node_id)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.ComposedNodeNotFound(ComposedNode=composed_node_id)
        return ref

    def create_composed_node(self, values):
        composed_node = models.ComposedNode()
        composed_node.update(values)
        try:
            composed_node.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ComposedNodeAlreadyExist(
                ComposedNode=values['url'])
        return composed_node

    def destroy_composed_node(self, pod_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.ComposedNode).filter_by(
                    pod_id=pod_id)
                query.delete()
        except NoResultFound:
            raise exception.ComposedNodeNotFound()

    """
    volume db instance entrance
    """

    def get_volume_by_id(self, volume_id):
        query = model_query(models.Volume).filter_by(id=volume_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.VolumeNotFound(volume=volume_id)

    def get_volume_by_url(self, url):
        query = model_query(models.Volume).filter_by(url=url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.VolumeNotFound(volume=url)

    def get_pod_volume_list(self, pod_id, limit=None, marker=None,
                            sort_key=None, sort_dir=None):
        query = model_query(models.Volume).filter_by(pod_id=pod_id)
        return _paginate_query(models.Volume, limit, marker, sort_key,
                               sort_dir, query)

    def update_volume(self, url, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Volume).filter_by(url=url)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.VolumeNotFound(volume=url)
        return ref

    def create_volume(self, values):
        volume = models.Volume()
        volume.update(values)
        try:
            volume.save()
        except db_exc.DBDuplicateEntry:
            raise exception.VolumeAlreadyExist(volume=values['url'])
        return volume

    def destroy_volume(self, pod_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Volume).filter_by(pod_id=pod_id)
                query.delete()
        except NoResultFound:
            raise exception.VolumeNotFound()

    """
    interface db instance entrance
    """

    def get_interface_by_id(self, interface_id):
        query = model_query(models.Interface).filter_by(id=interface_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InterfaceNotFound(interface=interface_id)

    def get_node_interface_list(self, node_id, limit=None, marker=None,
                                sort_key=None, sort_dir=None):
        query = model_query(models.Interface).filter_by(
            computer_system_id=node_id)
        return _paginate_query(models.Interface, limit, marker, sort_key,
                               sort_dir, query)

    def update_interface(self, id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Interface).filter_by(id=id)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.InterfaceNotFound(interface=id)
        return ref

    def create_interface(self, values):
        interface = models.Interface()
        interface.update(values)
        try:
            interface.save()
        except db_exc.DBDuplicateEntry:
            raise exception.InterfaceAlreadyExist(interface=values['id'])
        return interface

    def destroy_interface(self, computer_system_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Interface).filter_by(
                    computer_system_id=computer_system_id)
                query.delete()
        except NoResultFound:
            raise exception.InterfaceNotFound()

    """
    manager db instance entrance
    """

    def get_manager_by_id(self, manager_id):
        query = model_query(models.Manager).filter_by(id=manager_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ManagerNotFound(manager=manager_id)

    def get_manager_by_url(self, manager_url):
        query = model_query(models.Manager).filter_by(url=manager_url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ManagerNotFound(manager=manager_url)

    def get_manager_list(self, pod_id, limit=None, marker=None, sort_key=None,
                         sort_dir=None):
        query = model_query(models.Manager).filter_by(pod_id=pod_id)
        return _paginate_query(models.Manager, limit, marker, sort_key,
                               sort_dir, query)

    def update_manager(self, manager_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Manager).filter_by(id=manager_id)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.ManagerNotFound(manager=manager_id)
        return ref

    def create_manager(self, values):
        manager = models.Manager()
        manager.update(values)
        try:
            manager.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ManagerAlreadyExist(manager=values['id'])
        return manager

    def destroy_manager(self, pod_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.Manager).filter_by(pod_id=pod_id)
                query.delete()
        except NoResultFound:
            raise exception.ManagerNotFound()

    """
    target db instance entrance
    """

    def get_target_by_id(self, target_id):
        query = model_query(models.RemoteTarget).filter_by(id=target_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.RemoteTargetNotFound(target=target_id)

    def get_target_by_url(self, target_url):
        query = model_query(models.RemoteTarget).filter_by(url=target_url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.RemoteTargetNotFound(target=target_url)

    def get_target_list_by_pod(self, pod_id, limit=None, marker=None,
                               sort_key=None, sort_dir=None):
        query = model_query(models.RemoteTarget).filter_by(pod_id=pod_id)
        return _paginate_query(models.RemoteTarget, limit, marker, sort_key,
                               sort_dir, query)

    def update_target(self, target_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.RemoteTarget).filter_by(
                    id=target_id)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.RemoteTargetNotFound(target=target_id)
        return ref

    def create_target(self, values):
        target = models.RemoteTarget()
        target.update(values)
        try:
            target.save()
        except db_exc.DBDuplicateEntry:
            raise exception.RemoteTargetAlreadyExist(target=values['id'])
        return target

    def destroy_target(self, pod_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.RemoteTarget).filter_by(
                    pod_id=pod_id)
                query.delete()
        except NoResultFound:
            raise exception.RemoteTargetNotFound()

    """
    pcieswitch db instance entrance
    """

    def get_pcieswitch_by_id(self, pcieswitch_id):
        query = model_query(models.PCIeSwitch).filter_by(id=pcieswitch_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PCIeSwitchNotFound(pcieswitch=pcieswitch_id)

    def get_pcieswitch_by_url(self, pcieswitch_url):
        query = model_query(models.PCIeSwitch).filter_by(url=pcieswitch_url)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PCIeSwitchNotFound(pcieswitch=pcieswitch_url)

    def get_pcieswitch_list_by_pod(self, pod_id, limit=None, marker=None,
                                   sort_key=None, sort_dir=None):
        query = model_query(models.PCIeSwitch).filter_by(pod_id=pod_id)
        return _paginate_query(models.PCIeSwitch, limit, marker, sort_key,
                               sort_dir, query)

    def update_pcieswitch(self, pcieswitch_id, values):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.PCIeSwitch).filter_by(
                    id=pcieswitch_id)
                query.update(values)
                ref = query.one()
        except NoResultFound:
            raise exception.PCIeSwitchNotFound(pcieswitch=pcieswitch_id)
        return ref

    def create_pcieswitch(self, values):
        pcieswitch = models.PCIeSwitch()
        pcieswitch.update(values)
        try:
            pcieswitch.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PCIeSwitchAlreadyExist(pcieswitch=values['id'])
        return pcieswitch

    def destroy_pcieswitch(self, pod_id):
        session = get_session()
        try:
            with session.begin():
                query = model_query(models.PCIeSwitch).filter_by(pod_id=pod_id)
                query.delete()
        except NoResultFound:
            raise exception.PCIeSwitchNotFound()
