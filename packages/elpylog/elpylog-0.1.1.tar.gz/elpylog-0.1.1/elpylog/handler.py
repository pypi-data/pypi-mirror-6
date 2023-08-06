import json
import socket
import time
import datetime

from logging.handlers import DatagramHandler

SKIP_EXTRA_FIELDS = set(['args', 'asctime', 'created', 'exc_info',  'exc_text',
                         'filename', 'funcName', 'id', 'levelname', 'levelno',
                         'lineno', 'module', 'msecs', 'msecs', 'message',
                         'msg', 'name', 'pathname', 'process', 'processName',
                         'relativeCreated', 'thread', 'threadName'])


class BulkUdp(DatagramHandler):
    """Elasticsearch Bulk Udp handler

    implements the bulk UDP for a message:
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/docs-bulk-udp.html

    :param host: The host of the elasticsearch server.
    :param port: The port of the graylog server (default 9700).
    :param max_packet_size: Maximum message size. Fields will be dropped not to
                            exceed this size.
    :param debugging_fields: Send debug fields if true.
    :param extra_fields: Send extra fields on the log record to graylog
                         if true (the default).
    :param fqdn: Use fully qualified domain name of localhost as source
                 host (socket.getfqdn()).
    :param localname: Use specified hostname as source host.
    :param index: The elasticsearch index in which to record the log message.
    :param type: The type for log messages
    """

    def __init__(self, host, port=9700, max_packet_size=64*1024,
                 debugging_fields=False, extra_fields=True, fqdn=False,
                 localname=None, index="logstash-%Y.%m.%d", type="logs"):
        self.debugging_fields = debugging_fields
        self.extra_fields = extra_fields
        self.max_packet_size = max_packet_size
        self.fqdn = fqdn
        self.localname = localname
        self.index = index
        self.type = type
        DatagramHandler.__init__(self, host, port)

    def emit(self, record):
        """
        Emit a record.

        Pickles the record and writes it to the socket in binary format.
        If there is an error with the socket, silently drop the packet.
        If there was a problem with the socket, re-establishes the
        socket.
        """

        try:
            index = time.strftime(self.index, time.gmtime(record.created))

            packet = json.dumps({"index": {"_id": None,
                                           "_index": index,
                                           "_type": self.type}})
            packet += "\n{"
            first_field = True

            for key, value in self._generate_fields(record):
                bytes_left = self.max_packet_size - len(packet)
                value_json = json.dumps(value, default=str)

                # There's 5 overhead characters: 2 quotes around the key, the
                # : separator and the kvp separator or terminating bracket.
                if (len(value_json) + len(key) + 5) < bytes_left:
                    if not first_field:
                        packet += ",\"%s\":%s" % (key, value_json)
                    else:
                        packet += "\"%s\":%s" % (key, value_json)
                        first_field = False
                elif bytes_left < 16:
                    break

            packet += "}\n"

            self.send(packet)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def _generate_fields(self, record):
        yield "@version", "1"
        yield "message", record.getMessage()

        if self.fqdn:
            yield "logsource", socket.getfqdn()
        elif self.localname:
            yield "logsource", socket.localname
        else:
            yield "logsource", socket.gethostname()

        yield "severity", record.levelno

        dt = datetime.datetime.utcfromtimestamp(record.created)
        yield '@timestamp', dt.isoformat() + "Z"
        yield 'level', record.levelname
        yield 'name', record.name

        if self.debugging_fields:
            yield 'file', record.pathname
            yield 'line', record.lineno
            yield '_function', record.funcName
            yield '_pid', record.process
            yield '_thread_name', record.threadName
            # record.processName was added in Python 2.6.2
            pn = getattr(record, 'processName', None)
            if pn is not None:
                yield '_process_name', pn

        if self.extra_fields:
            for key, value in record.__dict__.items():
                if key not in SKIP_EXTRA_FIELDS and not key.startswith('_'):
                    yield '_%s' % key, value

        # TODO: callstack?


# {"message":"pam_unix(cron:session): session closed for user root",
# "@version":"1",
# "@timestamp":"2014-04-04T12:05:01.000Z",
# "host":"10.42.255.54",
# "priority":86,
# "timestamp":"Apr  4 14:05:01",
# "logsource":"faraday",
# "program":"CRON",
# "pid":"16530",
# "severity":6,
# "facility":10,
# "facility_label":"security/authorization",
# "severity_label":"Informational"}
