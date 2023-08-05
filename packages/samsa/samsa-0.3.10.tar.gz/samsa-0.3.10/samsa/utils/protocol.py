import collections
import itertools
import struct

from samsa.responses import (
    MetadataResponse, BrokerMetadata, TopicMetadata, PartitionMetadata
)

## API KEYS

PRODUCE_KEY = 0
FETCH_KEY = 1
OFFSET_KEY = 2
METADATA_KEY = 3

# Coming soon, in 0.8.1
#OFFSET_COMMIT = 6
#OFFSET_FETCH = 7


## All version numbers are currently 0

CORRELATION_ID = 0 # we don't need this
CLIENT_ID = 'samsa'
HEADER_LEN= 19

def _unpack(fmt_list, buff, offset, count=1):
    items = []
    for i in xrange(count):
        item = []
        for fmt in fmt_list:
            if type(fmt) == list:
                count = struct.unpack_from('!i', buff, offset)[0]
                offset += 4
                subitems,offset = _unpack(fmt, buff, offset, count=count)
                item.append(subitems)
            else:
                for ch in fmt:
                    if ch == 's':
                        ch = '%ds' % struct.unpack_from('!h', buff, offset)
                        offset += 2
                    unpacked = struct.unpack_from('!'+ch, buff, offset)
                    offset += struct.calcsize(ch)
                    item.append(unpacked[0])
        if len(item) == 1:
            items.append(item[0])
        else:
            items.append(tuple(item))
    return items,offset

def _write_header(api_key, msg_bytes, api_version=0):
    struct.pack_into(
        '!ihhih5s',
        msg_bytes, 0,
        len(msg_bytes) - 4, api_key, api_version,
        CORRELATION_ID, 5, CLIENT_ID
    )


# Metadata API

def pack_metadata_request(topics=None):
    """Pack a metadata request to be sent to the server

    MetadataRequest => [TopicName]
      TopicName => string
    """
    topics = [] if topics is None else topics
    topics_len = [len(t) for t in topics] # we use this a couple times
    msg_len = 4 + sum(topics_len) + 2*len(topics)
    output = bytearray(HEADER_LEN + msg_len)

    # Write the header
    _write_header(METADATA_KEY, output)

    # Write the message data
    fmt = '!i' + ''.join('h%ds' % lt for lt in topics_len)
    struct.pack_into(fmt, output, HEADER_LEN,
                     len(topics), *itertools.chain(*zip(topics_len, topics)))
    return output

def unpack_metadata_response(buff):
    """Unpck a metadata request response

    MetadataResponse => [Broker][TopicMetadata]
      Broker => NodeId Host Port
      NodeId => int32
      Host => string
      Port => int32
      TopicMetadata => TopicErrorCode TopicName [PartitionMetadata]
      TopicErrorCode => int16
      PartitionMetadata => PartitionErrorCode PartitionId Leader Replicas Isr
      PartitionErrorCode => int16
      PartitionId => int32
      Leader => int32
      Replicas => [int32]
      Isr => [int32]
    """
    fmt = [['isi'], ['hs', ['hii', ['i'], ['i']]]]
    response,offset = _unpack(fmt, buff, 0)
    broker_info, topic_info = response[0]

    brokers = {}
    for (id, host, port) in broker_info:
        brokers[id] = BrokerMetadata(id, host, port)

    topics = {}
    for err, name, part_meta in topic_info:
        topics[name] = TopicMetadata(name, {}, err)
        for p_err, p_id, p_ldr, p_reps, p_isr in part_meta:
            topics[name].partitions[p_id] = PartitionMetadata(
                p_id, p_ldr, p_reps, p_isr, p_err
            )
    return MetadataResponse(brokers, topics)


# Produce API

def pack_produce_request(data, acks=1, timeout=1000):
    """Pack a produce request to be sent to the server

    ProduceRequest => RequiredAcks Timeout [TopicName [Partition MessageSetSize MessageSet]]
      RequiredAcks => int16
      Timeout => int32
      Partition => int32
      MessageSetSize => int32
    """
    pass



def unpack_produce_response(buff):
    """Unpack a produce response from the server

    ProduceResponse => [TopicName [Partition ErrorCode Offset]]
      TopicName => string
      Partition => int32
      ErrorCode => int16
      Offset => int64
    """
    pass


# Fetch API

def pack_fetch_request():
    """Pack a fetch request to be sent to the server

    FetchRequest => ReplicaId MaxWaitTime MinBytes [TopicName [Partition FetchOffset MaxBytes]]
      ReplicaId => int32
      MaxWaitTime => int32
      MinBytes => int32
      TopicName => string
      Partition => int32
      FetchOffset => int64
      MaxBytes => int32
    """
    pass

def unpack_fetch_response(buff):
    """Unpack a fetch response from the server

    FetchResponse => [TopicName [Partition ErrorCode HighwaterMarkOffset MessageSetSize MessageSet]]
      TopicName => string
      Partition => int32
      ErrorCode => int16
      HighwaterMarkOffset => int64
      MessageSetSize => int32
    """
    pass


# Offset API

def pack_offset_request():
    """Pack an offset request to be sent to the server

    OffsetRequest => ReplicaId [TopicName [Partition Time MaxNumberOfOffsets]]
      ReplicaId => int32
      TopicName => string
      Partition => int32
      Time => int64
      MaxNumberOfOffsets => int32
    """
    pass

def unpack_offset_response():
    """Unpack an offser response from the server

    OffsetResponse => [TopicName [PartitionOffsets]]
      PartitionOffsets => Partition ErrorCode [Offset]
      Partition => int32
      ErrorCode => int16
      Offset => int64
    """
    pass
