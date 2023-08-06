#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Copyright (c) 2003-2011 Ralph Meijer
Copyright (c) 2012, 2013 Jérôme Poisson


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
--

This program is based on Idavoll (http://idavoll.ik.nu/),
originaly written by Ralph Meijer (http://ralphm.net/blog/)
It is sublicensed under AGPL v3 (or any later version) as allowed by the original
license.

--

Here is a copy of the original license:

Copyright (c) 2003-2011 Ralph Meijer

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import copy, logging

from zope.interface import implements

from twisted.internet import defer
from twisted.words.protocols.jabber import jid

from wokkel.generic import parseXml, stripNamespace
from wokkel.pubsub import Subscription

from sat_pubsub import error, iidavoll, const
import psycopg2

class Storage:

    implements(iidavoll.IStorage)

    defaultConfig = {
            'leaf': {
                "pubsub#persist_items": True,
                "pubsub#deliver_payloads": True,
                "pubsub#send_last_published_item": 'on_sub',
                const.OPT_ACCESS_MODEL: const.VAL_AMODEL_DEFAULT,
                const.OPT_PUBLISH_MODEL: const.VAL_PMODEL_DEFAULT,
            },
            'collection': {
                "pubsub#deliver_payloads": True,
                "pubsub#send_last_published_item": 'on_sub',
                const.OPT_ACCESS_MODEL: const.VAL_AMODEL_DEFAULT,
                const.OPT_PUBLISH_MODEL: const.VAL_PMODEL_DEFAULT,
            }
    }

    def __init__(self, dbpool):
        self.dbpool = dbpool


    def getNode(self, nodeIdentifier):
        return self.dbpool.runInteraction(self._getNode, nodeIdentifier)

    def _getNode(self, cursor, nodeIdentifier):
        configuration = {}
        cursor.execute("""SELECT node_type,
                                 persist_items,
                                 deliver_payloads,
                                 send_last_published_item,
                                 access_model,
                                 publish_model
                          FROM nodes
                          WHERE node=%s""",
                       (nodeIdentifier,))
        row = cursor.fetchone()

        if not row:
            raise error.NodeNotFound()

        if row[0] == 'leaf':
            configuration = {
                    'pubsub#persist_items': row[1],
                    'pubsub#deliver_payloads': row[2],
                    'pubsub#send_last_published_item': row[3],
                    const.OPT_ACCESS_MODEL:row[4],
                    const.OPT_PUBLISH_MODEL:row[5],
                    }
            node = LeafNode(nodeIdentifier, configuration)
            node.dbpool = self.dbpool
            return node
        elif row[0] == 'collection':
            configuration = {
                    'pubsub#deliver_payloads': row[2],
                    'pubsub#send_last_published_item': row[3],
                    const.OPT_ACCESS_MODEL: row[4],
                    const.OPT_PUBLISH_MODEL:row[5],
                    }
            node = CollectionNode(nodeIdentifier, configuration)
            node.dbpool = self.dbpool
            return node



    def getNodeIds(self):
        d = self.dbpool.runQuery("""SELECT node from nodes""")
        d.addCallback(lambda results: [r[0] for r in results])
        return d


    def createNode(self, nodeIdentifier, owner, config):
        return self.dbpool.runInteraction(self._createNode, nodeIdentifier,
                                           owner, config)


    def _createNode(self, cursor, nodeIdentifier, owner, config):
        if config['pubsub#node_type'] != 'leaf':
            raise error.NoCollections()

        owner = owner.userhost()
        try:
            cursor.execute("""INSERT INTO nodes
                              (node, node_type, persist_items,
                               deliver_payloads, send_last_published_item, access_model, publish_model)
                              VALUES
                              (%s, 'leaf', %s, %s, %s, %s, %s)""",
                           (nodeIdentifier,
                            config['pubsub#persist_items'],
                            config['pubsub#deliver_payloads'],
                            config['pubsub#send_last_published_item'],
                            config[const.OPT_ACCESS_MODEL],
                            config[const.OPT_PUBLISH_MODEL],
                            )
                           )
        except cursor._pool.dbapi.IntegrityError:
            raise error.NodeExists()

        cursor.execute("""SELECT node_id FROM nodes WHERE node=%s""", (nodeIdentifier,));
        node_id = cursor.fetchone()[0]

        cursor.execute("""SELECT 1 from entities where jid=%s""",
                       (owner,))

        if not cursor.fetchone():
            # XXX: we can NOT rely on the previous query! Commit is needed now because
            # if the entry exists the next query will leave the database in a corrupted
            # state: the solution is to rollback. I tried with other methods like
            # "WHERE NOT EXISTS" but none of them worked, so the following solution
            # looks like the sole - unless you have auto-commit on. More info
            # about this issue: http://cssmay.com/question/tag/tag-psycopg2
            cursor._connection.commit()
            try:
                cursor.execute("""INSERT INTO entities (jid) VALUES (%s)""",
                               (owner,))
            except psycopg2.IntegrityError as e:
                cursor._connection.rollback()
                logging.warning("during node creation: %s" % e.message)

        cursor.execute("""INSERT INTO affiliations
                          (node_id, entity_id, affiliation)
                          SELECT %s, entity_id, 'owner' FROM
                          (SELECT entity_id FROM entities
                                            WHERE jid=%s) as e""",
                       (node_id, owner))

        #TODO: manage JID access
        if config[const.OPT_ACCESS_MODEL] == const.VAL_AMODEL_ROSTER:
            if const.OPT_ROSTER_GROUPS_ALLOWED in config:
                allowed_groups = config[const.OPT_ROSTER_GROUPS_ALLOWED]
            else:
                allowed_groups = []
            for group in allowed_groups:
                #TODO: check that group are actually in roster
                cursor.execute("""INSERT INTO node_groups_authorized (node_id, groupname)
                                  VALUES (%s,%s)""" , (node_id, group))


    def deleteNode(self, nodeIdentifier):
        return self.dbpool.runInteraction(self._deleteNode, nodeIdentifier)


    def _deleteNode(self, cursor, nodeIdentifier):
        cursor.execute("""DELETE FROM nodes WHERE node=%s""",
                       (nodeIdentifier,))

        if cursor.rowcount != 1:
            raise error.NodeNotFound()

    def getNodeGroups(self, nodeIdentifier):
        return self.dbpool.runInteraction(self._getNodeGroups, nodeIdentifier)

    def _getNodeGroups(self, cursor, nodeIdentifier):
        cursor.execute("SELECT groupname FROM node_groups_authorized NATURAL JOIN nodes WHERE node=%s",
                       (nodeIdentifier,))
        rows = cursor.fetchall()

        return [row[0] for row in rows]

    def getAffiliations(self, entity):
        d = self.dbpool.runQuery("""SELECT node, affiliation FROM entities
                                        NATURAL JOIN affiliations
                                        NATURAL JOIN nodes
                                        WHERE jid=%s""",
                                     (entity.userhost(),))
        d.addCallback(lambda results: [tuple(r) for r in results])
        return d


    def getSubscriptions(self, entity):
        def toSubscriptions(rows):
            subscriptions = []
            for row in rows:
                subscriber = jid.internJID('%s/%s' % (row[1],
                                                      row[2]))
                subscription = Subscription(row[0], subscriber, row[3])
                subscriptions.append(subscription)
            return subscriptions

        d = self.dbpool.runQuery("""SELECT node, jid, resource, state
                                     FROM entities
                                     NATURAL JOIN subscriptions
                                     NATURAL JOIN nodes
                                     WHERE jid=%s""",
                                  (entity.userhost(),))
        d.addCallback(toSubscriptions)
        return d


    def getDefaultConfiguration(self, nodeType):
        return self.defaultConfig[nodeType]



class Node:

    implements(iidavoll.INode)

    def __init__(self, nodeIdentifier, config):
        self.nodeIdentifier = nodeIdentifier
        self._config = config
        self.owner = None;


    def _checkNodeExists(self, cursor):
        cursor.execute("""SELECT node_id FROM nodes WHERE node=%s""",
                       (self.nodeIdentifier,))
        if not cursor.fetchone():
            raise error.NodeNotFound()


    def getType(self):
        return self.nodeType

    def getNodeOwner(self):
        if self.owner:
            return defer.succeed(self.owner)
        d = self.dbpool.runQuery("""SELECT jid FROM nodes NATURAL JOIN affiliations NATURAL JOIN entities WHERE node=%s""", (self.nodeIdentifier,))
        d.addCallback(lambda result: jid.JID(result[0][0]))
        return d


    def getConfiguration(self):
        return self._config


    def setConfiguration(self, options):
        config = copy.copy(self._config)

        for option in options:
            if option in config:
                config[option] = options[option]

        d = self.dbpool.runInteraction(self._setConfiguration, config)
        d.addCallback(self._setCachedConfiguration, config)
        return d


    def _setConfiguration(self, cursor, config):
        self._checkNodeExists(cursor)
        cursor.execute("""UPDATE nodes SET persist_items=%s,
                                           deliver_payloads=%s,
                                           send_last_published_item=%s
                          WHERE node=%s""",
                       (config["pubsub#persist_items"],
                        config["pubsub#deliver_payloads"],
                        config["pubsub#send_last_published_item"],
                        self.nodeIdentifier))


    def _setCachedConfiguration(self, void, config):
        self._config = config


    def getMetaData(self):
        config = copy.copy(self._config)
        config["pubsub#node_type"] = self.nodeType
        return config


    def getAffiliation(self, entity):
        return self.dbpool.runInteraction(self._getAffiliation, entity)


    def _getAffiliation(self, cursor, entity):
        self._checkNodeExists(cursor)
        cursor.execute("""SELECT affiliation FROM affiliations
                          NATURAL JOIN nodes
                          NATURAL JOIN entities
                          WHERE node=%s AND jid=%s""",
                       (self.nodeIdentifier,
                        entity.userhost()))

        try:
            return cursor.fetchone()[0]
        except TypeError:
            return None

    def getAccessModel(self):
        return self.dbpool.runInteraction(self._getAccessModel)

    def _getAccessModel(self, cursor, entity):
        self._checkNodeExists(cursor)
        cursor.execute("""SELECT access_model FROM nodes
                          WHERE node=%s""",
                       (self.nodeIdentifier,))

        try:
            return cursor.fetchone()[0]
        except TypeError:
            return None


    def getSubscription(self, subscriber):
        return self.dbpool.runInteraction(self._getSubscription, subscriber)


    def _getSubscription(self, cursor, subscriber):
        self._checkNodeExists(cursor)

        userhost = subscriber.userhost()
        resource = subscriber.resource or ''

        cursor.execute("""SELECT state FROM subscriptions
                          NATURAL JOIN nodes
                          NATURAL JOIN entities
                          WHERE node=%s AND jid=%s AND resource=%s""",
                       (self.nodeIdentifier,
                        userhost,
                        resource))
        row = cursor.fetchone()
        if not row:
            return None
        else:
            return Subscription(self.nodeIdentifier, subscriber, row[0])


    def getSubscriptions(self, state=None):
        return self.dbpool.runInteraction(self._getSubscriptions, state)


    def _getSubscriptions(self, cursor, state):
        self._checkNodeExists(cursor)

        query = """SELECT jid, resource, state,
                          subscription_type, subscription_depth
                   FROM subscriptions
                   NATURAL JOIN nodes
                   NATURAL JOIN entities
                   WHERE node=%s""";
        values = [self.nodeIdentifier]

        if state:
            query += " AND state=%s"
            values.append(state)

        cursor.execute(query, values);
        rows = cursor.fetchall()

        subscriptions = []
        for row in rows:
            subscriber = jid.JID('%s/%s' % (row[0], row[1]))

            options = {}
            if row[3]:
                options['pubsub#subscription_type'] = row[3];
            if row[4]:
                options['pubsub#subscription_depth'] = row[4];

            subscriptions.append(Subscription(self.nodeIdentifier, subscriber,
                                              row[2], options))

        return subscriptions


    def addSubscription(self, subscriber, state, config):
        return self.dbpool.runInteraction(self._addSubscription, subscriber,
                                          state, config)


    def _addSubscription(self, cursor, subscriber, state, config):
        self._checkNodeExists(cursor)

        userhost = subscriber.userhost()
        resource = subscriber.resource or ''

        subscription_type = config.get('pubsub#subscription_type')
        subscription_depth = config.get('pubsub#subscription_depth')

        try:
            cursor.execute("""INSERT INTO entities (jid) VALUES (%s)""",
                           (userhost,))
        except cursor._pool.dbapi.IntegrityError:
            cursor._connection.rollback()

        try:
            cursor.execute("""INSERT INTO subscriptions
                              (node_id, entity_id, resource, state,
                               subscription_type, subscription_depth)
                              SELECT node_id, entity_id, %s, %s, %s, %s FROM
                              (SELECT node_id FROM nodes
                                              WHERE node=%s) as n
                              CROSS JOIN
                              (SELECT entity_id FROM entities
                                                WHERE jid=%s) as e""",
                           (resource,
                            state,
                            subscription_type,
                            subscription_depth,
                            self.nodeIdentifier,
                            userhost))
        except cursor._pool.dbapi.IntegrityError:
            raise error.SubscriptionExists()


    def removeSubscription(self, subscriber):
        return self.dbpool.runInteraction(self._removeSubscription,
                                           subscriber)


    def _removeSubscription(self, cursor, subscriber):
        self._checkNodeExists(cursor)

        userhost = subscriber.userhost()
        resource = subscriber.resource or ''

        cursor.execute("""DELETE FROM subscriptions WHERE
                          node_id=(SELECT node_id FROM nodes
                                                  WHERE node=%s) AND
                          entity_id=(SELECT entity_id FROM entities
                                                      WHERE jid=%s) AND
                          resource=%s""",
                       (self.nodeIdentifier,
                        userhost,
                        resource))
        if cursor.rowcount != 1:
            raise error.NotSubscribed()

        return None


    def isSubscribed(self, entity):
        return self.dbpool.runInteraction(self._isSubscribed, entity)


    def _isSubscribed(self, cursor, entity):
        self._checkNodeExists(cursor)

        cursor.execute("""SELECT 1 FROM entities
                          NATURAL JOIN subscriptions
                          NATURAL JOIN nodes
                          WHERE entities.jid=%s
                          AND node=%s AND state='subscribed'""",
                       (entity.userhost(),
                       self.nodeIdentifier))

        return cursor.fetchone() is not None


    def getAffiliations(self):
        return self.dbpool.runInteraction(self._getAffiliations)


    def _getAffiliations(self, cursor):
        self._checkNodeExists(cursor)

        cursor.execute("""SELECT jid, affiliation FROM nodes
                          NATURAL JOIN affiliations
                          NATURAL JOIN entities
                          WHERE node=%s""",
                       (self.nodeIdentifier,))
        result = cursor.fetchall()

        return [(jid.internJID(r[0]), r[1]) for r in result]



class LeafNode(Node):

    implements(iidavoll.ILeafNode)

    nodeType = 'leaf'

    def storeItems(self, item_data, publisher):
        return self.dbpool.runInteraction(self._storeItems, item_data, publisher)


    def _storeItems(self, cursor, item_data, publisher):
        self._checkNodeExists(cursor)
        for item_datum in item_data:
            self._storeItem(cursor, item_datum, publisher)


    def _storeItem(self, cursor, item_datum, publisher):
        access_model, item_config, item = item_datum
        data = item.toXml()

        cursor.execute("""UPDATE items SET date=now(), publisher=%s, data=%s
                          FROM nodes
                          WHERE nodes.node_id = items.node_id AND
                                nodes.node = %s and items.item=%s""",
                       (publisher.full(),
                        data,
                        self.nodeIdentifier,
                        item["id"]))
        if cursor.rowcount == 1:
            return

        cursor.execute("""INSERT INTO items (node_id, item, publisher, data, access_model)
                          SELECT node_id, %s, %s, %s, %s FROM nodes
                                                     WHERE node=%s
                                                     RETURNING item_id""",
                       (item["id"],
                        publisher.full(),
                        data,
                        access_model,
                        self.nodeIdentifier))

        if access_model == const.VAL_AMODEL_ROSTER:
            item_id = cursor.fetchone()[0];
            if const.OPT_ROSTER_GROUPS_ALLOWED in item_config:
                item_config.fields[const.OPT_ROSTER_GROUPS_ALLOWED].fieldType='list-multi' #XXX: needed to force list if there is only one value
                allowed_groups = item_config[const.OPT_ROSTER_GROUPS_ALLOWED]
            else:
                allowed_groups = []
            for group in allowed_groups:
                #TODO: check that group are actually in roster
                cursor.execute("""INSERT INTO item_groups_authorized (item_id, groupname)
                                  VALUES (%s,%s)""" , (item_id, group))


    def removeItems(self, itemIdentifiers):
        return self.dbpool.runInteraction(self._removeItems, itemIdentifiers)


    def _removeItems(self, cursor, itemIdentifiers):
        self._checkNodeExists(cursor)

        deleted = []

        for itemIdentifier in itemIdentifiers:
            cursor.execute("""DELETE FROM items WHERE
                              node_id=(SELECT node_id FROM nodes
                                                      WHERE node=%s) AND
                              item=%s""",
                           (self.nodeIdentifier,
                            itemIdentifier))

            if cursor.rowcount:
                deleted.append(itemIdentifier)

        return deleted


    def getItems(self, authorized_groups, unrestricted, maxItems=None):
        """ Get all authorised items
        @param authorized_groups: we want to get items that these groups can access
        @param unrestricted: if true, don't check permissions (i.e.: get all items)
        @param maxItems: nb of items we want to tget
        @return: list of (item, access_model, id) if unrestricted is True, else list of items
        """
        return self.dbpool.runInteraction(self._getItems, authorized_groups, unrestricted, maxItems)


    def _getItems(self, cursor, authorized_groups, unrestricted, maxItems):
        self._checkNodeExists(cursor)
        if unrestricted:
            query = ["""SELECT data,items.access_model,item_id FROM nodes
                       INNER JOIN items USING (node_id)
                       WHERE node=%s ORDER BY date DESC"""]
            args = [self.nodeIdentifier]
        else:
            query = ["""SELECT data FROM nodes
                       INNER  JOIN items USING (node_id)
                       LEFT JOIN item_groups_authorized USING (item_id)
                       WHERE node=%s AND
                       (items.access_model='open' """ +
                       ("or (items.access_model='roster' and groupname in %s)" if authorized_groups else '') +
                       """)
                       ORDER BY date DESC"""]
            args = [self.nodeIdentifier]
            if authorized_groups:
                args.append(authorized_groups)

        if maxItems:
            query.append("LIMIT %s")
            args.append(maxItems)

        cursor.execute(' '.join(query), args)

        result = cursor.fetchall()
        if unrestricted:
            ret = []
            for data in result:
                item = stripNamespace(parseXml(data[0]))
                access_model = data[1]
                item_id = data[2]
                if access_model == 'roster': #TODO: jid access_model
                    cursor.execute('SELECT groupname FROM item_groups_authorized WHERE item_id=%s', (item_id,))
                    access_list = [r[0] for r in cursor.fetchall()]
                else:
                    access_list = None

                ret.append((item, access_model, access_list))
            return ret
        items = [stripNamespace(parseXml(r[0])) for r in result]
        return items


    def getItemsById(self, authorized_groups, unrestricted, itemIdentifiers):
        """ Get items which are in the given list
        @param authorized_groups: we want to get items that these groups can access
        @param unrestricted: if true, don't check permissions
        @param itemIdentifiers: list of ids of the items we want to get
        @return: list of (item, access_model, access_model) if unrestricted is True, else list of items
        """
        return self.dbpool.runInteraction(self._getItemsById, authorized_groups, unrestricted, itemIdentifiers)


    def _getItemsById(self, cursor, authorized_groups, unrestricted, itemIdentifiers):
        self._checkNodeExists(cursor)
        ret = []
        if unrestricted: #we get everything without checking permissions
            for itemIdentifier in itemIdentifiers:
                cursor.execute("""SELECT data,items.access_model,item_id FROM nodes
                                  INNER JOIN items USING (node_id)
                                  WHERE node=%s AND item=%s""",
                               (self.nodeIdentifier,
                                itemIdentifier))
                result = cursor.fetchone()
                if result:
                    for data in result:
                        item = stripNamespace(parseXml(data[0]))
                        access_model = data[1]
                        item_id = data[2]
                        if access_model == 'roster': #TODO: jid access_model
                            cursor.execute('SELECT groupname FROM item_groups_authorized WHERE item_id=%s', (item_id,))
                            access_list = [r[0] for r in cursor.fetchall()]
                        else:
                            access_list = None

                        ret.append((item, access_model, access_list))
        else: #we check permission before returning items
            for itemIdentifier in itemIdentifiers:
                args = [self.nodeIdentifier, itemIdentifier]
                if authorized_groups:
                    args.append(authorized_groups)
                cursor.execute("""SELECT data FROM nodes
                           INNER  JOIN items USING (node_id)
                           LEFT JOIN item_groups_authorized USING (item_id)
                           WHERE node=%s AND item=%s AND
                           (items.access_model='open' """ +
                           ("or (items.access_model='roster' and groupname in %s)" if authorized_groups else '') + ")",
                           args)

                result = cursor.fetchone()
                if result:
                    ret.append(parseXml(result[0]))

        return ret

    def purge(self):
        return self.dbpool.runInteraction(self._purge)


    def _purge(self, cursor):
        self._checkNodeExists(cursor)

        cursor.execute("""DELETE FROM items WHERE
                          node_id=(SELECT node_id FROM nodes WHERE node=%s)""",
                       (self.nodeIdentifier,))


    def filterItemsWithPublisher(self, itemIdentifiers, requestor):
        return self.dbpool.runInteraction(self._filterItemsWithPublisher, itemIdentifiers, requestor)

    def _filterItemsWithPublisher(self, cursor, itemIdentifiers, requestor):
        self._checkNodeExists(cursor)
        ret = []
        for itemIdentifier in itemIdentifiers:
            args = ["%s/%%" % requestor.userhost(), itemIdentifier]
            cursor.execute("""SELECT item FROM items WHERE publisher LIKE %s AND item=%s""", args)
            result = cursor.fetchone()
            if result:
                ret.append(result[0])
        return ret

class CollectionNode(Node):

    nodeType = 'collection'



class GatewayStorage(object):
    """
    Memory based storage facility for the XMPP-HTTP gateway.
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool


    def _countCallbacks(self, cursor, service, nodeIdentifier):
        """
        Count number of callbacks registered for a node.
        """
        cursor.execute("""SELECT count(*) FROM callbacks
                          WHERE service=%s and node=%s""",
                       service.full(),
                       nodeIdentifier)
        results = cursor.fetchall()
        return results[0][0]


    def addCallback(self, service, nodeIdentifier, callback):
        def interaction(cursor):
            cursor.execute("""SELECT 1 FROM callbacks
                              WHERE service=%s and node=%s and uri=%s""",
                           service.full(),
                           nodeIdentifier,
                           callback)
            if cursor.fetchall():
                return

            cursor.execute("""INSERT INTO callbacks
                              (service, node, uri) VALUES
                              (%s, %s, %s)""",
                           service.full(),
                           nodeIdentifier,
                           callback)

        return self.dbpool.runInteraction(interaction)


    def removeCallback(self, service, nodeIdentifier, callback):
        def interaction(cursor):
            cursor.execute("""DELETE FROM callbacks
                              WHERE service=%s and node=%s and uri=%s""",
                           service.full(),
                           nodeIdentifier,
                           callback)

            if cursor.rowcount != 1:
                raise error.NotSubscribed()

            last = not self._countCallbacks(cursor, service, nodeIdentifier)
            return last

        return self.dbpool.runInteraction(interaction)

    def getCallbacks(self, service, nodeIdentifier):
        def interaction(cursor):
            cursor.execute("""SELECT uri FROM callbacks
                              WHERE service=%s and node=%s""",
                           service.full(),
                           nodeIdentifier)
            results = cursor.fetchall()

            if not results:
                raise error.NoCallbacks()

            return [result[0] for result in results]

        return self.dbpool.runInteraction(interaction)


    def hasCallbacks(self, service, nodeIdentifier):
        def interaction(cursor):
            return bool(self._countCallbacks(cursor, service, nodeIdentifier))

        return self.dbpool.runInteraction(interaction)
