__license__ = """
Copyright 2012 DISQUS
Copyright 2013 Parse.ly, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import collections
import functools
import itertools
import logging

from kazoo.recipe.watchers import ChildrenWatch, DataWatch

from samsa.client import OFFSET_EARLIEST, OFFSET_LATEST
from samsa.exceptions import OffsetOutOfRangeError
from samsa.utils import attribute_repr
from samsa.utils.delayedconfig import (DelayedConfiguration,
    requires_configuration)


logger = logging.getLogger(__name__)

class PartitionMap(object):
    """
    Manages the partitions associated with a topic on a per-broker basis.

    :param cluster: The cluster that this partition map is associated with.
    :type cluster: :class:`samsa.cluster.Cluster`
    :param topic: The topic that this partition map is associated with.
    :type topic: :class:`samsa.topics.Topic`
    """
    def __init__(self, cluster, topic):
        self.cluster = cluster
        self.topic = topic

        self.__brokers = {}

        self.topic_path = '/brokers/topics/%s' % self.topic.name
        self._topic_watcher = DataWatch(
            self.cluster.zookeeper, self.topic_path,
            self._topic_changed, allow_missing_node=True
        )

    __repr__ = attribute_repr('topic')

    def _topic_changed(self, data, stat):
        if stat:
            self._topic_child_watcher = ChildrenWatch(
                self.cluster.zookeeper, self.topic_path,
                self._configure
            )

    def _configure(self, broker_ids):
        logger.info('Looking up brokers for %s...', self)

        brokers = map(self.cluster.brokers.get, map(int, broker_ids))

        # Add any broker IDs that are not already present in the mapping.
        for broker in brokers:
            if broker not in self.__brokers:
                partitionset = PartitionSet(self.cluster, self.topic, broker)
                logger.info('Discovered new partition set: %s', partitionset)
                self.__brokers[broker] = partitionset

        # Remove any brokers that are no longer present in the mapping.
        dead = set(self.__brokers.keys()) - set(brokers)
        for broker in dead:
            logger.info('Removing broker %s from %s', broker, self)
            del self.__brokers[broker]

    def __len__(self):
        """
        Returns the total number of partitions for this partition map,
        including virtual partitions.
        """
        partitions = list(iter(self))
        return len(partitions)

    def __iter__(self):
        """
        Returns an iterator containing every known partition for this topic.

        This includes "virtual" partitions for brokers that are present in the
        cluster, but have not yet registered their topic/partitions with the
        ZooKeeper cluster.
        """
        return itertools.chain(self.actual, self.virtual)

    @property
    def _partition_sets(self):
        """
        Returns a list of :class:`samsa.partitions.PartitionSet`.

        """
        return self.__brokers.values()

    @property
    def actual(self):
        """
        Returns an iterator containing all of the partitions for this topic
        that have been registered by a broker in ZooKeeper.
        """
        return itertools.chain.from_iterable(itertools.imap(iter,
            self.__brokers.values()))

    @property
    def virtual(self):
        """
        Returns an iterator containing "virtual" partitions for this topic.

        Virtual partitions are placeholder partitions for brokers that are
        known to be alive but are not aware of a topic. Since these brokers
        haven't seen the topic yet, they will not have published the number of
        partitions that they're serving. Every broker should be able to accept
        writes on the 0th partition for each topic, however, so the virtual
        partitions provide a partition objects for those partitions that have
        not yet been registered but are assumed to exist.
        """
        uninitialized_brokers = set(self.cluster.brokers.values()) - \
            set(self.__brokers.keys())
        create_virtual_partitionset = functools.partial(PartitionSet,
            cluster=self.cluster, topic=self.topic, virtual=True)
        virtual_iterator = lambda broker: \
            iter(create_virtual_partitionset(broker=broker))
        return itertools.chain.from_iterable(itertools.imap(virtual_iterator,
            uninitialized_brokers))


class PartitionSet(object):
    """
    Manages the partitions for a topic on a single broker.

    :param cluster: The cluster that this partition set is associated with.
    :type cluster: :class:`samsa.cluster.Cluster`
    :param topic: The topic that this partion set is associated with.
    :type topic: :class:`samsa.topics.Topic`
    :param broker: The broker this partition set is associated with.
    :type broker: :class:`samsa.brokers.Broker`
    :param virtual: Whether this is a "virtual" partition set or not. Virtual
        partition sets are used when a broker does not have any data associated
        with a specific topic.
    :type virtual: bool
    """
    def __init__(self, cluster, topic, broker, virtual=False):
        self.cluster = cluster
        self.topic = topic
        self.broker = broker
        self.virtual = virtual

        # TODO: At some point it might be wise to enable a "hint" size for
        # virtual partitions -- this way if brokers are serving a large number
        # of partitions, we can still maintain a reasonably even distribution
        # in a predictable environment. This might cause some problems in more
        # dynamic/less homogenous environments, however, since there's no good
        # way to track down a failure on a produce request to an invalid
        # partition.
        self.__count = 1

        path = '/brokers/topics/%s/%s' % (self.topic.name, self.broker.id)
        if not self.virtual:
            self._partition_watcher = DataWatch(
                self.cluster.zookeeper, path,
                self._configure, allow_missing_node=True
            )

    __repr__ = attribute_repr('topic', 'broker', 'virtual')

    def _configure(self, data, stat):

        # If the node does not exist, this means this broker has not gotten
        # any writes for this partition yet. We can assume that the broker
        # is handling at least one partition for this topic, and update
        # when we have more information by setting an exists watch on the
        # node path.
        if data:
            count = int(data)
            logger.info('Found %s partitions for %s', count, self)
        else:
            count = 1
            logger.info('%s is not registered in ZooKeeper, falling back '
                'to %s virtual partition(s)', self, count)

        self.__count = count

    def __len__(self):
        """
        Returns the total number of partitions available within this partition
        set.
        """
        return self.__count

    def __iter__(self):
        """
        Returns an iterator of :class:`samsa.topics.Partition` instances for
        this partition set.
        """
        for i in xrange(0, len(self)):
            yield Partition(self.cluster, self.topic, self.broker, i)


class Partition(object):
    def __init__(self, cluster, topic, broker, number):
        self.cluster = cluster
        self.topic = topic
        self.broker = broker
        self.number = int(number)

    __repr__ = attribute_repr('topic', 'broker', 'number')

    def earliest_offset(self):
        return self.broker.client.offsets(
            self.topic.name, self.number, OFFSET_EARLIEST, 1
        )[0]

    def latest_offset(self):
        return self.broker.client.offsets(
            self.topic.name, self.number, OFFSET_LATEST, 1
        )[0]

    def publish(self, data):
        """
        Publishes one or more messages to this partition.
        """
        if isinstance(data, basestring):
            messages = [data]
        elif isinstance(data, collections.Sequence):
            messages = data
        else:
            raise TypeError

        return self.broker.client.produce(self.topic.name, self.number,
            messages)

    def fetch(self, offset, size):
        return self.broker.client.fetch(
            self.topic.name, self.number, offset, size
        )

    def __hash__(self):
        return hash((self.topic, self.broker.id, self.number))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other
