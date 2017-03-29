#!/usr/bin/env python
from __future__ import print_function
import pika
import sys
import json
import time
import os
from fontprojects import git_repos

def main():
  # We'll retry until we get a connection and deliver the messages
  while True:
    try:
      msgqueue_host = os.environ.get("RABBITMQ_SERVICE_SERVICE_HOST", os.environ.get("BROKER"))
      connection = pika.BlockingConnection(pika.ConnectionParameters(host=msgqueue_host))
      channel = connection.channel()

      print ("Dispatching {} messages...".format(len(messages)), file=sys.stderr)
      for entry in git_repos:
        message = {
          "STATUS": entry[0]
          "FAMILY_NAME": entry[1],
          "GIT_REPO_URL": entry[2],
          "FONTFILES_PREFIX": entry[3]
        }

        if message["STATUS"] not in ["OK", "NOTE"]:
          # Skip this repo, since it is not in bad-shape to run fontbakery checks on it.
          # See the listing at fontprojects.py script to know the specific issues.
          continue

        print ("Adding {} to the queue.".format(message["GIT_REPO_URL"]), file=sys.stderr)
        channel.basic_publish(exchange='',
                              routing_key='font_repo_queue',
                              body=json.dumps(message),
                              properties=pika.BasicProperties(
                               delivery_mode = 2, # make message persistent
                              ))
      connection.close()
      print ("Done.", file=sys.stderr)
      sys.exit(0)
    except pika.exceptions.ConnectionClosed:
      print ("RabbitMQ not ready yet.", file=sys.stderr)
      time.sleep(1)
      pass

main()

