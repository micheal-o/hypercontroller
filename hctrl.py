"""
  Hypercontroller is used for running multiple instances of pox to manage different
  segments of the same network, which is not originally supported by openflow or pox.
  Check README file for configuration details.
"""

__author__ = 'Babatunde Micheal Okutubo'
__version__ = '1.0.1'

from pox.core import core
from pox.lib.util import dpid_to_str, str_to_dpid
import time

from kafka import KafkaProducer
from kafka import KafkaConsumer
import threading

log = core.getLogger()

class hctrl (object):
  """
  Hypercontroller class uses publisher/subscriber model to share connection event info
  between multiple controllers.
  """
  class __conn (object):
    def __init__(self, dpid):
      self.dpid = dpid
      self.description = 'hctrl' # to identify hctrl switches/connections
      self.ports = {}
      self.connect_time = time.time() # used by spanning tree

  def __init__ (self, stream):
    core.openflow.addListeners(self)
    self.bootstrap_servers = stream
    self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)

  def _handle_ConnectionUp (self, event):
    """
    Acts as a publisher, monitors connection up events and publish to kafka stream.
    """
    message = 'add#' + dpid_to_str(event.dpid)
    message.encode(encoding='utf-8')
    future = self.producer.send("of_connections", message)
    future.get(timeout=60)
    log.info("publisher: published {} connection up to stream".format(dpid_to_str(event.dpid)))

  def _handle_ConnectionDown (self, event):
    """
    Acts as a publisher, monitors connection down events and publish to kafka stream.
    """
    message = 'delete#' + dpid_to_str(event.dpid)
    message.encode(encoding='utf-8')
    future = self.producer.send("of_connections", message)
    future.get(timeout=60)
    log.info("publisher: published {} connection down to stream".format(dpid_to_str(event.dpid)))

  @staticmethod
  def subscribe (stream):
    """
    Runs as a separate thread, and listen to connection up/down messages published on kafka.
    :param stream: ip address and port of kafka or zookeeper host e.g 192.168.56.1:9092
    """
    consumer = KafkaConsumer('of_connections', bootstrap_servers=stream)
    for msg in consumer:
      msg = msg.value
      action, dpid = msg.split('#')
      if action == 'add':
        dpid = str_to_dpid(dpid)
        if dpid not in core.openflow.connections:
          # new connection
          con = hctrl.__conn(dpid)
          core.openflow._connect(con)
          log.info("subscriber: new connection from {}".format(dpid_to_str(con.dpid)))
      else:
        # delete connection
        core.openflow._disconnect(dpid)
        log.info("subscriber: connection down from {}".format(dpid))
    log.info("subscriber: shutting down...")

def launch (stream):
  """
  Initialize and launch hctrl
  :param stream : ip address and port of kafka or zookeeper host e.g 192.168.56.1:9092
  """
  # create subscriber thread to listen to connection event messages published on kafka
  sub_thread = threading.Thread(target=hctrl.subscribe, name='sub_of_conn', args=[stream])
  sub_thread.start()
  core.registerNew(hctrl, stream)
