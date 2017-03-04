#!/usr/bin/env python
from __future__ import print_function
import pika
import sys
import json
import time
import os

messages = [
  {"GIT_REPO_URL":"https://github.com/andrew-paglinawan/QuicksandFamily.git",
   "FONTFILE_PREFIX": "fonts/Quicksand-"},
  {"GIT_REPO_URL":"https://github.com/impallari/Cabin.git",
   "FONTFILE_PREFIX": "fonts/TTF/Cabin-"},
  {"GIT_REPO_URL":"https://github.com/cadsondemak/chonburi.git",
   "FONTFILE_PREFIX": "fonts/Chonburi-"},
  {"GIT_REPO_URL":"https://github.com/alefalefalef/Varela-Round-Hebrew.git",
   "FONTFILE_PREFIX": "fonts/VarelaRound-"}
]

def main():
  # We'll retry until we get a connection and deliver the messages
  while True:
    try:
      msgqueue_host = os.environ.get("BROKER")
      connection = pika.BlockingConnection(pika.ConnectionParameters(host=msgqueue_host))
      channel = connection.channel()

      for message in messages:
        channel.basic_publish(exchange='',
                              routing_key='font_repo_queue',
                              body=json.dumps(message),
                              properties=pika.BasicProperties(
                               delivery_mode = 2, # make message persistent
                              ))
      sys.exit(0)
    except pika.exceptions.ConnectionClosed:
      print ("RabbitMQ not ready yet.", file=sys.stderr)
      time.sleep(1)
      pass

main()

