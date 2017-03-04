import pika
import json

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
  rabbitmq_host = os.environ.get("RABBITMQ_SERVICE_SERVICE_HOST")
  connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
  channel = connection.channel()

  for message in messages:
    channel.basic_publish(exchange='',
                          routing_key='font_repo_queue',
                          body=json.dumps(message),
                          properties=pika.BasicProperties(
                           delivery_mode = 2, # make message persistent
                          ))

main()

