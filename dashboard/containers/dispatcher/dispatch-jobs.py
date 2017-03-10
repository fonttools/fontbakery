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
   "FONTFILE_PREFIX": "fonts/VarelaRound-"},
  {"GIT_REPO_URL":"https://github.com/10four/Bhavuka.git",
   "FONTFILE_PREFIX": "Bhavuka-"},
  {"GIT_REPO_URL":"https://github.com/alexeiva/poiretone.git",
   "FONTFILE_PREFIX": "fonts/ttf/PoiretOne-"},
  {"GIT_REPO_URL":"https://github.com/huertatipografica/sarala.git",
   "FONTFILE_PREFIX": "font/Sarala-"},
  {"GIT_REPO_URL":"https://github.com/anexasajoop/cambay.git",
   "FONTFILE_PREFIX": "cambay/Font files/Unhinted/"},
  {"GIT_REPO_URL":"https://github.com/cadsondemak/itim.git",
   "FONTFILE_PREFIX": "fonts/Itim-"},
  {"GIT_REPO_URL":"https://github.com/cadsondemak/kanit.git",
   "FONTFILE_PREFIX": "font/Kanit-"},
  {"GIT_REPO_URL":"https://github.com/cadsondemak/sriracha.git",
   "FONTFILE_PREFIX": "fonts/Sriracha-"},
  {"GIT_REPO_URL":"https://github.com/huertatipografica/sura.git",
   "FONTFILE_PREFIX": "fonts/Sura-"},
  {"GIT_REPO_URL":"https://github.com/CatharsisFonts/Cormorant.git",
   "FONTFILE_PREFIX": "1. TrueType Font Files/Cormorant-"},
  {"GIT_REPO_URL":"https://github.com/christiannaths/Redacted-Font.git",
   "FONTFILE_PREFIX": "src/Redacted-"},
  {"GIT_REPO_URL":"https://github.com/clauseggers/Inknut-Antiqua.git",
   "FONTFILE_PREFIX": "TTF-OTF/InknutAntiqua-"},
  {"GIT_REPO_URL":"https://github.com/cyrealtype/Adamina.git",
   "FONTFILE_PREFIX": "fonts/Adamina-"},
  {"GIT_REPO_URL":"https://github.com/cyrealtype/Alike.git",
   "FONTFILE_PREFIX": "Alike-"},
  {"GIT_REPO_URL":"https://github.com/cyrealtype/Federant.git",
   "FONTFILE_PREFIX": "Federant-"},
  {"GIT_REPO_URL":"https://github.com/cyrealtype/Sumana.git",
   "FONTFILE_PREFIX": "Sumana-"},
  {"GIT_REPO_URL":"https://github.com/DunwichType/RhodiumLibre.git",
   "FONTFILE_PREFIX": "RhodiumLibre-"},
  {"GIT_REPO_URL":"https://github.com/EbenSorkin/Asar.git",
   "FONTFILE_PREFIX": "Asar-"},
  {"GIT_REPO_URL":"https://github.com/EbenSorkin/Atomic-Age.git",
   "FONTFILE_PREFIX": "fonts/ttf/AtomicAge-"},
  {"GIT_REPO_URL":"https://github.com/EbenSorkin/Basic.git",
   "FONTFILE_PREFIX": "Basic-"},
  {"GIT_REPO_URL":"https://github.com/EbenSorkin/Dekko.git",
   "FONTFILE_PREFIX": "Dekko-"},
  {"GIT_REPO_URL":"https://github.com/EbenSorkin/Kavoon.git",
   "FONTFILE_PREFIX": "Kavoon-"},
  {"GIT_REPO_URL":"https://github.com/EbenSorkin/Varta.git",
   "FONTFILE_PREFIX": "Varta-"},
  {"GIT_REPO_URL":"https://github.com/erinmclaughlin/Khula.git",
   "FONTFILE_PREFIX": "ttf_hinted/Khula-"},
  {"GIT_REPO_URL":"https://github.com/etunni/Amita.git",
   "FONTFILE_PREFIX": "TTF/Amita-"},
  {"GIT_REPO_URL":"https://github.com/etunni/Arya.git",
   "FONTFILE_PREFIX": "TTF/Arya-"},
  {"GIT_REPO_URL":"https://github.com/etunni/glegoo.git",
   "FONTFILE_PREFIX": "Glegoo-"},
  {"GIT_REPO_URL":"https://github.com/etunni/kurale.git",
   "FONTFILE_PREFIX": "fonts/Kurale-"},
  {"GIT_REPO_URL":"https://github.com/googlefonts/Homenaje.git",
   "FONTFILE_PREFIX": "fonts/Homenaje-"},
  {"GIT_REPO_URL":"https://github.com/googlefonts/LatoGFVersion.git",
   "FONTFILE_PREFIX": "fonts/Lato-"},
  {"GIT_REPO_URL":"https://github.com/impallari/Raleway.git",
   "FONTFILE_PREFIX": "fonts/v3.000 Fontlab/TTF/Raleway-"}
]

def main():
  # We'll retry until we get a connection and deliver the messages
  while True:
    try:
      msgqueue_host = os.environ.get("RABBITMQ_SERVICE_SERVICE_HOST", os.environ.get("BROKER"))
      connection = pika.BlockingConnection(pika.ConnectionParameters(host=msgqueue_host))
      channel = connection.channel()

      print ("Dispatching {} messages...".format(len(messages)), file=sys.stderr)
      for message in messages:
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

