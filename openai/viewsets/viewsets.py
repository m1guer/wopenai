from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import json
import requests
import os


class OpenAiViewSet(viewsets.ViewSet):
    def sent_message(self, numero, nome):
        url = "https://graph.facebook.com/v16.0/121601520926198/messages"
        headers = {
            "Authorization": "Bearer EAAQvHeAZBZA4MBAM1LTSewCVZAbgiIAaHzdbuvVqBcA40gFml6rBMdnwd2ZBDy7lWwQV8kgqT67MXg40A76bZBbCZCAG0V2NirVxupqJr8pqweOs7kCvhP2MDbgWyQgZCYzGB8oHNIgOR6r8TbZCy070W5Jds0zBOYlWfb4YC1FJ785HIdWnlbY99vy0ixdRjJWFOQktGVLohwZDZD",
            "Content-Type": "application/json",
        }
        body = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {
                "body": "Olá " + nome
            }
        }

        r = requests.post(url, headers=headers, data=json.dumps(body))
        return r

    @action(detail=False, methods=['get', 'post'])
    def webhook(self, request, *args, **kwargs):
        data_json = request.data
        if request.method == 'GET':
            hub_challenge = request.query_params.get('hub.challenge')
            data = json.loads(hub_challenge)
            return Response(data)
        if request.method == 'POST':
            print(data_json)
            if 'contacts' in data_json['entry'][0]['changes'][0]['value']:
                name = data_json['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
                numero = data_json['entry'][0]['changes'][0]['value']['contacts'][0]["wa_id"]
                self.sent_message(numero, name)
                return Response("ok")
            else:
                print("erro")
                return Response("error")
