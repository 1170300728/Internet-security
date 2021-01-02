#!/usr/bin/env python
# encoding: utf-8

import socket
from hashlib import sha1
from random import randint
from struct import unpack
from socket import inet_ntoa
from threading import Thread, Timer
from time import sleep
from collections import deque
from bencode import bencode, bdecode
from database import mydatabase
import os
import sys  
sys.setrecursionlimit(10000)  

BOOTSTRAP_NODES = (
    "udp://tracker.open-internet.nl:6969/announce",
    "udp://tracker.coppersurfer.tk:6969/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://tracker.internetwarriors.net:1337/announce",
    "udp://9.rarbg.to:2710/announce",
    "udp://public.popcorn-tracker.org:6969/announce",
    "udp://tracker.vanitycore.co:6969/announce",
    "https://1.track.ga:443/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://tracker.cypherpunks.ru:6969/announce",
    "udp://thetracker.org:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://retracker.lanta-net.ru:2710/announce",
    "udp://bt.xxx-tracker.com:2710/announce",
    "http://retracker.telecom.by:80/announce",
    "http://retracker.mgts.by:80/announce",
    "http://0d.kebhana.mx:443/announce",
    "udp://torr.ws:2710/announce",
    "udp://open.stealth.si:80/announce",
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881),
)
TID_LENGTH = 2
RE_JOIN_DHT_INTERVAL = 3
TOKEN_LENGTH = 2
WAIT_TIME = 10


def entropy(length):
  return "".join(chr(randint(0, 255)) for _ in range(length))


def random_id(num):
  return os.urandom(num)


def decode_nodes(nodes):
  n = []
  length = len(nodes)
  if (length % 26) != 0:
    return n

  for i in range(0, length, 26):
    nid = nodes[i:i+20]
    ip = inet_ntoa(nodes[i+20:i+24])
    port = unpack("!H", nodes[i+24:i+26])[0]
    n.append((nid, ip, port))

  return n

def get_neighbor(target, nid, end=14):
  return target[:end]+nid[end:]


class KNode(object):

  def __init__(self, nid, ip, port):
    self.nid = nid
    self.ip = ip
    self.port = port


class DHT:
  def __init__(self, bind_ip, bind_port, max_node_qsize):
    self.max_node_qsize = max_node_qsize
    self.nid = random_id(20)
    self.nodes = deque(maxlen=max_node_qsize)
    self.outflag = False
    self.bind_ip = bind_ip
    self.bind_port = bind_port
    self.database = mydatabase()

    self.process_request_actions = {
      b"get_peers": self.on_get_peers_request,
      b"announce_peer": self.on_announce_peer_request,
    }

    self.ufd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    self.ufd.bind((self.bind_ip, self.bind_port))

  def send_krpc(self, msg, address):
    try:
      self.ufd.sendto(bencode(msg), address)
    except:
      pass

  def send_find_node(self, address, nid=None):
    nid = get_neighbor(nid, random_id(20)) if nid else self.nid
    tid = random_id(2)
    msg = {
      "t": tid,
      "y": "q",
      "q": "find_node",
      "a": {
        "id": nid,
        "target": random_id(20)
      }
    }
    self.send_krpc(msg, address)


  def join_DHT(self):
    for address in BOOTSTRAP_NODES:
      self.send_find_node(address)

  def re_join_DHT(self):
    if len(self.nodes) == 0:
      self.join_DHT()
    sleep(WAIT_TIME)

  def send_loop(self):
    wait = 1.0 / self.max_node_qsize
    sleep(2)
    print("send_loop start")
    self.outcount = self.max_node_qsize * 0.5
    while True:
      if len(self.nodes) > self.outcount: 
        self.outflag = True
        self.ufd.close()
        self.database.myclose()
        print(len(self.nodes))
        break
      try:
        node = self.nodes.popleft()
        self.send_find_node((node.ip, node.port), node.nid)
        self.nodes.append(node)
      except IndexError:
        sleep(WAIT_TIME)
        self.re_join_DHT()
      sleep(wait)

  def process_find_node_response(self, msg, address):
    nodes = decode_nodes(msg[b"r"][b"nodes"])
    for node in nodes:
      (nid, ip, port) = node
      if len(nid) != 20: continue
      if ip == self.bind_ip: continue
      if port < 1 or port > 65535: continue
      n = KNode(nid, ip, port)
      self.database.myinsert(nid, ip, port)
      print(n, end = "")
      print(len(self.nodes))
      self.nodes.append(n)


  def recv_loop(self):
    self.join_DHT()
    print("recv_loop start")
    while True:
      if self.outflag: break
      try:
        data, address = self.ufd.recvfrom(65535)
        msg = bdecode(data)
        self.on_message(msg, address)
      except Exception as e:
        print(e)

  def on_message(self, msg, address):
    try:
      if msg[b"y"] == b"r":
        if b"nodes" in msg[b"r"]:
          self.process_find_node_response(msg, address)
      elif msg[b"y"] == b"q":
        try:
          self.process_request_actions[msg[b"q"]](msg, address)
        except KeyError:
          self.play_dead(msg, address)
    except KeyError:
      pass

  def on_get_peers_request(self, msg, address):
    try:
      infohash = msg[b"a"][b"info_hash"]
      tid = msg[b"t"]
      nid = msg[b"a"][b"id"]
      token = infohash[:TOKEN_LENGTH]
      msg = {
        "t": tid,
        "y": "r",
        "r": {
          "id": get_neighbor(infohash, self.nid),
          "nodes": "",
          "token": token
        }
      }
      self.send_krpc(msg, address)
    except KeyError:
      pass

  def on_announce_peer_request(self, msg, address):
    try:
      infohash = msg[b"a"][b"info_hash"]
      #print msg["a"]
      tname = msg[b"a"][b"name"]
      token = msg[b"a"][b"token"]
      nid = msg[b"a"][b"id"]
      tid = msg[b"t"]

      if infohash[:TOKEN_LENGTH] == token:
        if b"implied_port" in msg[b"a"] and msg[b"a"][b"implied_port"] != 0:
          port = address[1]
        else:
          port = msg[b"a"][b"port"]
          if port < 1 or port > 65535: return
    except Exception:
      pass
    finally:
      self.ok(msg, address)

  def play_dead(self, msg, address):
    try:
      tid = bytes.decode(msg[b"t"])
      msg = {
        "t": tid,
        "y": "e",
        "e": [202, "Server Error"]
      }
      self.send_krpc(msg, address)
    except KeyError:
      pass

  def ok(self, msg, address):
    try:
      tid = msg[b"t"]
      nid = msg[b"a"][b"id"]
      msg = {
        "t": tid,
        "y": "r",
        "r": {
          "id": get_neighbor(nid, self.nid)
        }
      }
      self.send_krpc(msg, address)
    except KeyError:
      pass


# using example
if __name__ == "__main__":
  # max_node_qsize bigger, bandwith bigger, speed higher
  dht = DHT("0.0.0.0", 9090, max_node_qsize=2000)
  Thread(target=dht.recv_loop).start()
  Thread(target=dht.send_loop).start()

