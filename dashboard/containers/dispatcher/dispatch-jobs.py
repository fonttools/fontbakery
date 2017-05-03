#!/usr/bin/env python
from __future__ import print_function
import pika
import sys
import json
import time
import os
from fontprojects import git_repos

local_devel = (os.environ.get("FONTBAKERY_LOCAL_DEVEL" == 1)
local_families_selection = [
  "Roboto",
  "Roboto Condensed",
  "Ubuntu",
  "Merriweather",
  "Lobster",
  "Exo",
  "Overpass Mono",
  "Sarala"]

def main():
  # We'll retry until we get a connection and deliver the messages
  while True:
    try:
      msgqueue_host = os.environ.get("RABBITMQ_SERVICE_SERVICE_HOST", os.environ.get("BROKER"))
      connection = pika.BlockingConnection(pika.ConnectionParameters(host=msgqueue_host))
      channel = connection.channel()

      print ("Dispatching messages...", file=sys.stderr)
      for i, entry in enumerate(git_repos):
        if i<=1:
          # Skip the first couple lines in the list
          # because they are purely informative statements
          continue

        if local_devel and entry[1] not in local_families_selection:
          # when deploying the cluster locally during development,
          # we restrict the list of families to a smaller selection
          continue

        message = {
          "MSG_INDEX": i,
          "STATUS": entry[0],
          "FAMILYNAME": entry[1],
          "GIT_REPO_URL": entry[2],
          "FONTFILE_PREFIX": entry[3]
        }

        print ("Adding to queue: {}".format(message), file=sys.stderr)
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

