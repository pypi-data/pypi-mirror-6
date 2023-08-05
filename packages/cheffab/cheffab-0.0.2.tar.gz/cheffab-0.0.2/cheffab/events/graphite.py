import json
import logging
import requests

from cheffab.events.base import BaseChefFabEvent


class GraphiteEvent(BaseChefFabEvent):
    def __init__(self,graphite_endpoint):
        self.graphite_endpoint = graphite_endpoint

    def post(self,event_payload):
        headers = {'content-type': 'application/json'}

        try:
            res = requests.post(self.graphite_endpoint,
                                data=json.dumps(event_payload),
                                headers=headers)
            
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.error("Failed to send graphite event for %s" % event_payload.get('what',"Unknown Event"))
