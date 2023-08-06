#!/usr/bin/python
#-*- coding: utf-8 -*-
#
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

"""
Generic publish-subscribe backend.

This module implements a generic publish-subscribe backend service with
business logic as per
U{XEP-0060<http://www.xmpp.org/extensions/xep-0060.html>} that interacts with
a given storage facility. It also provides an adapter from the XMPP
publish-subscribe protocol.
"""

import uuid

from zope.interface import implements

from twisted.application import service
from twisted.python import components, log
from twisted.internet import defer, reactor
from twisted.words.protocols.jabber.error import StanzaError
from twisted.words.protocols.jabber.jid import JID, InvalidFormat
from twisted.words.xish import utility

from wokkel import disco, data_form
from wokkel.iwokkel import IPubSubResource
from wokkel.pubsub import PubSubResource, PubSubError, Subscription

from sat_pubsub import error, iidavoll, const
from sat_pubsub.iidavoll import IBackendService, ILeafNode

from copy import deepcopy

def _getAffiliation(node, entity):
    d = node.getAffiliation(entity)
    d.addCallback(lambda affiliation: (node, affiliation))
    return d



class BackendService(service.Service, utility.EventDispatcher):
    """
    Generic publish-subscribe backend service.

    @cvar nodeOptions: Node configuration form as a mapping from the field
                       name to a dictionary that holds the field's type, label
                       and possible options to choose from.
    @type nodeOptions: C{dict}.
    @cvar defaultConfig: The default node configuration.
    """

    implements(iidavoll.IBackendService)

    nodeOptions = {
            "pubsub#persist_items":
                {"type": "boolean",
                 "label": "Persist items to storage"},
            "pubsub#deliver_payloads":
                {"type": "boolean",
                 "label": "Deliver payloads with event notifications"},
            "pubsub#send_last_published_item":
                {"type": "list-single",
                 "label": "When to send the last published item",
                 "options": {
                     "never": "Never",
                     "on_sub": "When a new subscription is processed"}
                },
            const.OPT_ACCESS_MODEL:
                {"type": "list-single",
                 "label": "Who can subscribe to this node",
                 "options": {
                     const.VAL_AMODEL_OPEN: "Public node",
                     const.VAL_AMODEL_ROSTER: "Node restricted to some roster groups",
                     const.VAL_AMODEL_JID: "Node restricted to some jids",
                     }
                },
            const.OPT_ROSTER_GROUPS_ALLOWED:
                {"type": "list-multi",
                 "label": "Groups of the roster allowed to access the node",
                },
            const.OPT_PUBLISH_MODEL:
                {"type": "list-single",
                 "label": "Who can publish to this node",
                 "options": {
                     const.VAL_PMODEL_OPEN: "Everybody can publish",
                     const.VAL_PMODEL_PUBLISHERS: "Only owner and publishers can publish",
                     const.VAL_PMODEL_SUBSCRIBERS: "Everybody which subscribed to the node",
                     }
                },
            }

    subscriptionOptions = {
            "pubsub#subscription_type":
                {"type": "list-single",
                 "options": {
                     "items": "Receive notification of new items only",
                     "nodes": "Receive notification of new nodes only"}
                },
            "pubsub#subscription_depth":
                {"type": "list-single",
                 "options": {
                     "1": "Receive notification from direct child nodes only",
                     "all": "Receive notification from all descendent nodes"}
                },
            }

    def __init__(self, storage):
        utility.EventDispatcher.__init__(self)
        self.storage = storage
        self._callbackList = []


    def supportsPublisherAffiliation(self):
        return True


    def supportsGroupBlog(self):
        return True


    def supportsOutcastAffiliation(self):
        return True


    def supportsPersistentItems(self):
        return True


    def supportsPublishModel(self):
        return True


    def getNodeType(self, nodeIdentifier):
        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(lambda node: node.getType())
        return d


    def getNodes(self):
        return self.storage.getNodeIds()


    def getNodeMetaData(self, nodeIdentifier):
        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(lambda node: node.getMetaData())
        d.addCallback(self._makeMetaData)
        return d


    def _makeMetaData(self, metaData):
        options = []
        for key, value in metaData.iteritems():
            if key in self.nodeOptions:
                option = {"var": key}
                option.update(self.nodeOptions[key])
                option["value"] = value
                options.append(option)

        return options


    def _checkAuth(self, node, requestor):
        """ Check authorisation of publishing in node for requestor """

        def check(affiliation):
            d = defer.succeed(node)
            configuration = node.getConfiguration()
            publish_model = configuration[const.OPT_PUBLISH_MODEL]

            if (publish_model == const.VAL_PMODEL_PUBLISHERS):
                if affiliation not in ['owner', 'publisher']:
                    raise error.Forbidden()
            elif (publish_model == const.VAL_PMODEL_SUBSCRIBERS):
                if affiliation not in ['owner', 'publisher']:
                    # we are in subscribers publish model, we must check that
                    # the requestor is a subscriber to allow him to publish

                    def checkSubscription(subscribed):
                        if not subscribed:
                            raise error.Forbidden()
                        return node

                    d.addCallback(lambda ignore: node.isSubscribed(requestor))
                    d.addCallback(checkSubscription)
            elif publish_model != const.VAL_PMODEL_OPEN:
                raise Exception('Unexpected value') # publish_model must be publishers (default), subscribers or open.

            return d

        d = node.getAffiliation(requestor)
        d.addCallback(check)
        return d

    def parseItemConfig(self, item):
        """Get and remove item configuration information
        @param item:
        """
        item_config = None
        access_model = const.VAL_AMODEL_DEFAULT
        for i in range(len(item.children)):
            elt = item.children[i]
            if not (elt.uri,elt.name)==(data_form.NS_X_DATA,'x'):
                continue
            form = data_form.Form.fromElement(elt)
            if (form.formNamespace == const.NS_ITEM_CONFIG):
                item_config = form
                del item.children[i] #we need to remove the config from item
                break

        if item_config:
            access_model = item_config.get(const.OPT_ACCESS_MODEL, const.VAL_AMODEL_DEFAULT)

        return (access_model, item_config)


    def publish(self, nodeIdentifier, items, requestor):
        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(self._checkAuth, requestor)
        #FIXME: owner and publisher are not necessarly the same. So far we use only owner to get roster.
        #FIXME: in addition, there can be several owners: that is not managed yet
        d.addCallback(self._doPublish, items, requestor)
        return d


    def _doPublish(self, node, items, requestor):
        if node.nodeType == 'collection':
            raise error.NoPublishing()

        configuration = node.getConfiguration()
        persistItems = configuration["pubsub#persist_items"]
        deliverPayloads = configuration["pubsub#deliver_payloads"]

        if items and not persistItems and not deliverPayloads:
            raise error.ItemForbidden()
        elif not items and (persistItems or deliverPayloads):
            raise error.ItemRequired()

        parsed_items = []
        for item in items:
            if persistItems or deliverPayloads:
                item.uri = None
                item.defaultUri = None
                if not item.getAttribute("id"):
                    item["id"] = str(uuid.uuid4())
            access_model, item_config = self.parseItemConfig(item)
            parsed_items.append((access_model, item_config, item)) 

        if persistItems:
            d = node.storeItems(parsed_items, requestor)
        else:
            d = defer.succeed(None)

        d.addCallback(self._doNotify, node, parsed_items,
                      deliverPayloads)
        return d


    def _doNotify(self, result, node, items, deliverPayloads):
        if items and not deliverPayloads:
            for access_model, item_config, item in items:
                item.children = []

        self.dispatch({'items': items, 'node': node},
                      '//event/pubsub/notify')


    def getNotifications(self, nodeIdentifier, items):

        def toNotifications(subscriptions, nodeIdentifier, items):
            subsBySubscriber = {}
            for subscription in subscriptions:
                if subscription.options.get('pubsub#subscription_type',
                                            'items') == 'items':
                    subs = subsBySubscriber.setdefault(subscription.subscriber,
                                                       set())
                    subs.add(subscription)

            notifications = [(subscriber, subscriptions, items)
                             for subscriber, subscriptions
                             in subsBySubscriber.iteritems()]

            return notifications

        def rootNotFound(failure):
            failure.trap(error.NodeNotFound)
            return []

        d1 = self.storage.getNode(nodeIdentifier)
        d1.addCallback(lambda node: node.getSubscriptions('subscribed'))
        d2 = self.storage.getNode('')
        d2.addCallback(lambda node: node.getSubscriptions('subscribed'))
        d2.addErrback(rootNotFound)
        d = defer.gatherResults([d1, d2])
        d.addCallback(lambda result: result[0] + result[1])
        d.addCallback(toNotifications, nodeIdentifier, items)
        return d


    def registerNotifier(self, observerfn, *args, **kwargs):
        self.addObserver('//event/pubsub/notify', observerfn, *args, **kwargs)


    def subscribe(self, nodeIdentifier, subscriber, requestor):
        subscriberEntity = subscriber.userhostJID()
        if subscriberEntity != requestor.userhostJID():
            return defer.fail(error.Forbidden())

        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(_getAffiliation, subscriberEntity)
        d.addCallback(self._doSubscribe, subscriber)
        return d


    def _doSubscribe(self, result, subscriber):
        node, affiliation = result
        #FIXME: must check node's access_model before subscribing

        if affiliation == 'outcast':
            raise error.Forbidden()

        def trapExists(failure):
            failure.trap(error.SubscriptionExists)
            return False

        def cb(sendLast):
            d = node.getSubscription(subscriber)
            if sendLast:
                d.addCallback(self._sendLastPublished, node)
            return d

        d = node.addSubscription(subscriber, 'subscribed', {})
        d.addCallbacks(lambda _: True, trapExists)
        d.addCallback(cb)
        return d


    def _sendLastPublished(self, subscription, node):

        def notifyItem(items):
            if items:
                reactor.callLater(0, self.dispatch,
                                     {'items': items,
                                      'node': node,
                                      'subscription': subscription,
                                     },
                                     '//event/pubsub/notify')

        config = node.getConfiguration()
        sendLastPublished = config.get('pubsub#send_last_published_item',
                                       'never')
        if sendLastPublished == 'on_sub' and node.nodeType == 'leaf':
            entity = subscription.subscriber.userhostJID()
            d = self.getItems(node.nodeIdentifier, entity, 1)
            d.addCallback(notifyItem)
            d.addErrback(log.err)

        return subscription


    def unsubscribe(self, nodeIdentifier, subscriber, requestor):
        if subscriber.userhostJID() != requestor.userhostJID():
            return defer.fail(error.Forbidden())

        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(lambda node: node.removeSubscription(subscriber))
        return d


    def getSubscriptions(self, entity):
        return self.storage.getSubscriptions(entity)

    def supportsAutoCreate(self):
        return True

    def supportsCreatorCheck(self):
        return True

    def supportsInstantNodes(self):
        return True


    def createNode(self, nodeIdentifier, requestor, options = None):
        if not nodeIdentifier:
            nodeIdentifier = 'generic/%s' % uuid.uuid4()

        if not options:
            options = {}

        if self.supportsCreatorCheck():
            groupblog = nodeIdentifier.startswith(const.NS_GROUPBLOG_PREFIX)
            try:
                nodeIdentifierJID = JID(nodeIdentifier[len(const.NS_GROUPBLOG_PREFIX):] if groupblog else nodeIdentifier)
            except InvalidFormat:
                is_user_jid = False
            else:
                is_user_jid = bool(nodeIdentifierJID.user)
            
            if is_user_jid and nodeIdentifierJID.userhostJID() != requestor.userhostJID():
                #we have an user jid node, but not created by the owner of this jid
                print "Wrong creator"
                raise error.Forbidden()

        nodeType = 'leaf'
        config = self.storage.getDefaultConfiguration(nodeType)
        config['pubsub#node_type'] = nodeType
        config.update(options)

        d = self.storage.createNode(nodeIdentifier, requestor, config)
        d.addCallback(lambda _: nodeIdentifier)
        return d


    def getDefaultConfiguration(self, nodeType):
        d = defer.succeed(self.storage.getDefaultConfiguration(nodeType))
        return d


    def getNodeConfiguration(self, nodeIdentifier):
        if not nodeIdentifier:
            return defer.fail(error.NoRootNode())

        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(lambda node: node.getConfiguration())

        return d


    def setNodeConfiguration(self, nodeIdentifier, options, requestor):
        if not nodeIdentifier:
            return defer.fail(error.NoRootNode())

        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doSetNodeConfiguration, options)
        return d


    def _doSetNodeConfiguration(self, result, options):
        node, affiliation = result

        if affiliation != 'owner':
            raise error.Forbidden()

        return node.setConfiguration(options)


    def getAffiliations(self, entity):
        return self.storage.getAffiliations(entity)


    def getItems(self, nodeIdentifier, requestor, maxItems=None,
                       itemIdentifiers=None):
        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doGetItems, requestor, maxItems, itemIdentifiers)
        return d

    def checkGroup(self, roster_groups, entity):
        """Check that entity is authorized and in roster
        @param roster_group: tuple which 2 items:
                        - roster: mapping of jid to RosterItem as given by self.roster.getRoster
                        - groups: list of authorized groups
        @param entity: entity which must be in group 
        @return: (True, roster) if entity is in roster and authorized
                 (False, roster) if entity is in roster but not authorized
        @raise: error.NotInRoster if entity is not in roster"""
        roster, authorized_groups = roster_groups
        _entity = entity.userhostJID()
        
        if not _entity in roster:
            raise error.NotInRoster
        return (roster[_entity].groups.intersection(authorized_groups), roster)

    def _getNodeGroups(self, roster, nodeIdentifier):
        d = self.storage.getNodeGroups(nodeIdentifier)
        d.addCallback(lambda groups: (roster, groups))
        return d

    def _doGetItems(self, result, requestor, maxItems, itemIdentifiers):
        node, affiliation = result

        def append_item_config(items_data):
            ret = []
            for data in items_data:
                item, access_model, access_list = data
                if access_model == const.VAL_AMODEL_OPEN:
                    pass
                elif access_model == const.VAL_AMODEL_ROSTER:
                    form = data_form.Form('submit', formNamespace=const.NS_ITEM_CONFIG)
                    access = data_form.Field(None, const.OPT_ACCESS_MODEL, value=const.VAL_AMODEL_ROSTER)
                    allowed = data_form.Field(None, const.OPT_ROSTER_GROUPS_ALLOWED, values=access_list)
                    form.addField(access)
                    form.addField(allowed)
                    item.addChild(form.toElement())
                elif access_model == const.VAL_AMODEL_JID:
                    #FIXME: manage jid
                    raise NotImplementedError
                else:
                    raise error.BadAccessTypeError(access_model)
                
                ret.append(item)
            return ret

        def access_checked(access_data):
            authorized, roster = access_data
            if not authorized:
                raise error.NotAuthorized()

            roster_item = roster.get(requestor.userhostJID())
            authorized_groups = tuple(roster_item.groups) if roster_item else tuple()

            if itemIdentifiers:
                return node.getItemsById(authorized_groups, affiliation == 'owner', itemIdentifiers)
            else:
                if affiliation == 'owner':
                    d = node.getItems(authorized_groups, True, maxItems)
                    return d.addCallback(append_item_config)
                else:
                    return node.getItems(authorized_groups, False, maxItems)


        if not ILeafNode.providedBy(node):
            return []

        if affiliation == 'outcast':
            raise error.Forbidden()

        access_model = node.getConfiguration()["pubsub#access_model"]
        d = node.getNodeOwner()
        d.addCallback(self.roster.getRoster)
        
        if access_model == 'open' or affiliation == 'owner':
            d.addCallback(lambda roster: (True, roster))
            d.addCallback(access_checked)
        elif access_model == 'roster':
            d.addCallback(self._getNodeGroups,node.nodeIdentifier)
            d.addCallback(self.checkGroup, requestor)
            d.addCallback(access_checked)

        return d

    def retractItem(self, nodeIdentifier, itemIdentifiers, requestor):
        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(_getAffiliation, requestor)
        if const.FLAG_RETRACT_ALLOW_PUBLISHER:
            d.addCallback(self._doRetractAllowPublisher, itemIdentifiers, requestor)
        else:
            d.addCallback(self._doRetract, itemIdentifiers)
        return d

    def _doRetractAllowPublisher(self, result, itemIdentifiers, requestor):
        """This method has been added to allow the publisher
        of an item to retract it, even if he has no affiliation
        to that item. For instance, this allows you to delete
        an item you posted in a node of "open" publish model.
        """
        node, affiliation = result
        if affiliation in ['owner', 'publisher']:
            return self._doRetract(result, itemIdentifiers)
        d = node.filterItemsWithPublisher(itemIdentifiers, requestor)
        def filterCb(filteredItems):
            if not filteredItems:
                return self._doRetract(result, itemIdentifiers)
            # XXX: fake an affiliation that does NOT exist
            return self._doRetract((node, 'publisher'), filteredItems)
        d.addCallback(filterCb)
        return d

    def _doRetract(self, result, itemIdentifiers):
        node, affiliation = result
        persistItems = node.getConfiguration()["pubsub#persist_items"]

        if affiliation not in ['owner', 'publisher']:
            raise error.Forbidden()

        if not persistItems:
            raise error.NodeNotPersistent()

        d = node.removeItems(itemIdentifiers)
        d.addCallback(self._doNotifyRetraction, node.nodeIdentifier)
        return d


    def _doNotifyRetraction(self, itemIdentifiers, nodeIdentifier):
        self.dispatch({'itemIdentifiers': itemIdentifiers,
                       'nodeIdentifier': nodeIdentifier },
                      '//event/pubsub/retract')


    def purgeNode(self, nodeIdentifier, requestor):
        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doPurge)
        return d


    def _doPurge(self, result):
        node, affiliation = result
        persistItems = node.getConfiguration()["pubsub#persist_items"]

        if affiliation != 'owner':
            raise error.Forbidden()

        if not persistItems:
            raise error.NodeNotPersistent()

        d = node.purge()
        d.addCallback(self._doNotifyPurge, node.nodeIdentifier)
        return d


    def _doNotifyPurge(self, result, nodeIdentifier):
        self.dispatch(nodeIdentifier, '//event/pubsub/purge')


    def registerPreDelete(self, preDeleteFn):
        self._callbackList.append(preDeleteFn)


    def getSubscribers(self, nodeIdentifier):
        def cb(subscriptions):
            return [subscription.subscriber for subscription in subscriptions]

        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(lambda node: node.getSubscriptions('subscribed'))
        d.addCallback(cb)
        return d


    def deleteNode(self, nodeIdentifier, requestor, redirectURI=None):
        d = self.storage.getNode(nodeIdentifier)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doPreDelete, redirectURI)
        return d


    def _doPreDelete(self, result, redirectURI):
        node, affiliation = result

        if affiliation != 'owner':
            raise error.Forbidden()

        data = {'node': node,
                'redirectURI': redirectURI}

        d = defer.DeferredList([cb(data)
                                for cb in self._callbackList],
                               consumeErrors=1)
        d.addCallback(self._doDelete, node.nodeIdentifier)


    def _doDelete(self, result, nodeIdentifier):
        dl = []
        for succeeded, r in result:
            if succeeded and r:
                dl.extend(r)

        d = self.storage.deleteNode(nodeIdentifier)
        d.addCallback(self._doNotifyDelete, dl)

        return d


    def _doNotifyDelete(self, result, dl):
        for d in dl:
            d.callback(None)



class PubSubResourceFromBackend(PubSubResource):
    """
    Adapts a backend to an xmpp publish-subscribe service.
    """

    features = [
        "config-node",
        "create-nodes",
        "delete-any",
        "delete-nodes",
        "item-ids",
        "meta-data",
        "publish",
        "purge-nodes",
        "retract-items",
        "retrieve-affiliations",
        "retrieve-default",
        "retrieve-items",
        "retrieve-subscriptions",
        "subscribe",
    ]

    discoIdentity = disco.DiscoIdentity('pubsub',
                                        'service',
                                        u'Salut à Toi pubsub service')

    pubsubService = None

    _errorMap = {
        error.NodeNotFound: ('item-not-found', None, None),
        error.NodeExists: ('conflict', None, None),
        error.Forbidden: ('forbidden', None, None),
        error.NotAuthorized: ('not-authorized', None, None),
        error.NotInRoster: ('not-authorized', 'not-in-roster-group', None),
        error.ItemForbidden: ('bad-request', 'item-forbidden', None),
        error.ItemRequired: ('bad-request', 'item-required', None),
        error.NoInstantNodes: ('not-acceptable',
                               'unsupported',
                               'instant-nodes'),
        error.NotSubscribed: ('unexpected-request', 'not-subscribed', None),
        error.InvalidConfigurationOption: ('not-acceptable', None, None),
        error.InvalidConfigurationValue: ('not-acceptable', None, None),
        error.NodeNotPersistent: ('feature-not-implemented',
                                  'unsupported',
                                  'persistent-node'),
        error.NoRootNode: ('bad-request', None, None),
        error.NoCollections: ('feature-not-implemented',
                              'unsupported',
                              'collections'),
        error.NoPublishing: ('feature-not-implemented',
                             'unsupported',
                             'publish'),
    }

    def __init__(self, backend):
        PubSubResource.__init__(self)

        self.backend = backend
        self.hideNodes = False

        self.backend.registerNotifier(self._notify)
        self.backend.registerPreDelete(self._preDelete)
        
        if self.backend.supportsCreatorCheck():
            self.features.append("creator-jid-check")  #SàT custom feature: Check that a node (which correspond to
                                                       #                    a jid in this server) is created by the right jid

        if self.backend.supportsAutoCreate():
            self.features.append("auto-create")

        if self.backend.supportsInstantNodes():
            self.features.append("instant-nodes")

        if self.backend.supportsOutcastAffiliation():
            self.features.append("outcast-affiliation")

        if self.backend.supportsPersistentItems():
            self.features.append("persistent-items")

        if self.backend.supportsPublisherAffiliation():
            self.features.append("publisher-affiliation")

        if self.backend.supportsGroupBlog():
            self.features.append("groupblog")

        # if self.backend.supportsPublishModel():       #XXX: this feature is not really described in XEP-0060, we just can see it in examples
        #     self.features.append("publish_model")     #     but it's necessary for microblogging comments (see XEP-0277)

    def _notify(self, data):
        items = data['items']
        node = data['node']
        
        def _notifyAllowed(result):
            """Check access of subscriber for each item,
            and notify only allowed ones"""
            notifications, (owner_jid,roster) = result
            
            #we filter items not allowed for the subscribers
            notifications_filtered = []

            for subscriber, subscriptions, _items in notifications:
                allowed_items = [] #we keep only item which subscriber can access

                for access_model, item_config, item in _items:
                    if access_model == 'open':
                        allowed_items.append(item)
                    elif access_model == 'roster':
                        _subscriber = subscriber.userhostJID()
                        if not _subscriber in roster:
                            continue
                        #the subscriber is known, is he in the right group ?
                        authorized_groups = item_config[const.OPT_ROSTER_GROUPS_ALLOWED]
                        if roster[_subscriber].groups.intersection(authorized_groups):
                            allowed_items.append(item)
                            
                    else: #unknown access_model
                        raise NotImplementedError

                if allowed_items:
                    notifications_filtered.append((subscriber, subscriptions, allowed_items))
            
            #we notify the owner
            #FIXME: check if this comply with XEP-0060 (option needed ?)
            #TODO: item's access model have to be sent back to owner
            #TODO: same thing for getItems
            
            def getFullItem(item_data):
                """ Attach item configuration to this item
                Used to give item configuration back to node's owner (and *only* to owner)
                """
                #TODO: a test should check that only the owner get the item configuration back
                
                access_model, item_config, item = item_data
                new_item = deepcopy(item)
                if item_config:
                    new_item.addChild(item_config.toElement())
                return new_item

            notifications_filtered.append((owner_jid,
                                           set([Subscription(node.nodeIdentifier, 
                                                            owner_jid,
                                                            'subscribed')]),
                                           [getFullItem(item_data) for item_data in items])) 

            return self.pubsubService.notifyPublish(
                                                self.serviceJID,
                                                node.nodeIdentifier,
                                                notifications_filtered)

        
        if 'subscription' not in data:
            d1 = self.backend.getNotifications(node.nodeIdentifier, items)
        else:
            subscription = data['subscription']
            d1 = defer.succeed([(subscription.subscriber, [subscription],
                                items)])
       
        def _got_owner(owner_jid):
            #return a tuple with owner_jid and roster
            d = self.backend.roster.getRoster(owner_jid)
            return d.addCallback(lambda roster: (owner_jid,roster))

        d2 = node.getNodeOwner()
        d2.addCallback(_got_owner)

        d = defer.gatherResults([d1, d2])
        d.addCallback(_notifyAllowed)


    def _preDelete(self, data):
        nodeIdentifier = data['node'].nodeIdentifier
        redirectURI = data.get('redirectURI', None)
        d = self.backend.getSubscribers(nodeIdentifier)
        d.addCallback(lambda subscribers: self.pubsubService.notifyDelete(
                                                self.serviceJID,
                                                nodeIdentifier,
                                                subscribers,
                                                redirectURI))
        return d


    def _mapErrors(self, failure):
        e = failure.trap(*self._errorMap.keys())

        condition, pubsubCondition, feature = self._errorMap[e]
        msg = failure.value.msg

        if pubsubCondition:
            exc = PubSubError(condition, pubsubCondition, feature, msg)
        else:
            exc = StanzaError(condition, text=msg)

        raise exc

    def getInfo(self, requestor, service, nodeIdentifier):
        info = {}

        def saveType(result):
            info['type'] = result
            return nodeIdentifier

        def saveMetaData(result):
            info['meta-data'] = result
            return info

        def trapNotFound(failure):
            failure.trap(error.NodeNotFound)
            return info

        d = defer.succeed(nodeIdentifier)
        d.addCallback(self.backend.getNodeType)
        d.addCallback(saveType)
        d.addCallback(self.backend.getNodeMetaData)
        d.addCallback(saveMetaData)
        d.addErrback(trapNotFound)
        d.addErrback(self._mapErrors)
        return d


    def getNodes(self, requestor, service, nodeIdentifier):
        if service.resource:
            return defer.succeed([])
        d = self.backend.getNodes()
        return d.addErrback(self._mapErrors)


    def getConfigurationOptions(self):
        return self.backend.nodeOptions

    def _publish_errb(self, failure, request):
        if failure.type == error.NodeNotFound and self.backend.supportsAutoCreate():
            print "Auto-creating node %s" % (request.nodeIdentifier,)
            d = self.backend.createNode(request.nodeIdentifier,
                                        request.sender)
            d.addCallback(lambda ignore,
                                 request: self.backend.publish(request.nodeIdentifier,
                                                               request.items,
                                                               request.sender),
                          request)
            return d

        return failure

    def publish(self, request):
        d = self.backend.publish(request.nodeIdentifier,
                                 request.items,
                                 request.sender)
        d.addErrback(self._publish_errb, request)
        return d.addErrback(self._mapErrors)


    def subscribe(self, request):
        d = self.backend.subscribe(request.nodeIdentifier,
                                   request.subscriber,
                                   request.sender)
        return d.addErrback(self._mapErrors)


    def unsubscribe(self, request):
        d = self.backend.unsubscribe(request.nodeIdentifier,
                                     request.subscriber,
                                     request.sender)
        return d.addErrback(self._mapErrors)


    def subscriptions(self, request):
        d = self.backend.getSubscriptions(request.sender)
        return d.addErrback(self._mapErrors)


    def affiliations(self, request):
        d = self.backend.getAffiliations(request.sender)
        return d.addErrback(self._mapErrors)


    def create(self, request):
        d = self.backend.createNode(request.nodeIdentifier,
                                    request.sender, request.options)
        return d.addErrback(self._mapErrors)


    def default(self, request):
        d = self.backend.getDefaultConfiguration(request.nodeType)
        return d.addErrback(self._mapErrors)


    def configureGet(self, request):
        d = self.backend.getNodeConfiguration(request.nodeIdentifier)
        return d.addErrback(self._mapErrors)


    def configureSet(self, request):
        d = self.backend.setNodeConfiguration(request.nodeIdentifier,
                                              request.options,
                                              request.sender)
        return d.addErrback(self._mapErrors)


    def items(self, request):
        d = self.backend.getItems(request.nodeIdentifier,
                                  request.sender,
                                  request.maxItems,
                                  request.itemIdentifiers)
        return d.addErrback(self._mapErrors)


    def retract(self, request):
        d = self.backend.retractItem(request.nodeIdentifier,
                                     request.itemIdentifiers,
                                     request.sender)
        return d.addErrback(self._mapErrors)


    def purge(self, request):
        d = self.backend.purgeNode(request.nodeIdentifier,
                                   request.sender)
        return d.addErrback(self._mapErrors)


    def delete(self, request):
        d = self.backend.deleteNode(request.nodeIdentifier,
                                    request.sender)
        return d.addErrback(self._mapErrors)

components.registerAdapter(PubSubResourceFromBackend,
                           IBackendService,
                           IPubSubResource)
