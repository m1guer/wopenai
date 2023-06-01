from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import json
import requests
import os
import openai


class OpenAiViewSet(viewsets.ViewSet):
    def _init_(self):
        self.message_responses = {}

    def start_prompt(self, message):
        openai.api_key = os.getenv("OPEN_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[message],
            max_tokens=3800,
            stop=None,
            temperature=0.7
        )
        for choice in response.choices:
            if "message" in choice and "content" in choice.message:
                return choice.message.content
        return response.choices[0].message.content

    def clear_responses(self):
        self.message_responses = {}

    def sent_message(self, numero, message):
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
                "body": message
            }
        }

        r = requests.post(url, headers=headers, data=json.dumps(body))
        return r

    @action(detail=False, methods=['get', 'post'])
    def webhook(self, request, *args, **kwargs):
        message_status = False  # if ==True message was read.
        data_json = request.data
        if request.method == 'GET':
            hub_challenge = request.query_params.get('hub.challenge')
            data = json.loads(hub_challenge)
            return Response(data)
        if request.method == 'POST':
            while message_status == False:
                if 'contacts' in data_json['entry'][0]['changes'][0]['value']:
                    numero = data_json['entry'][0]['changes'][0]['value']['contacts'][0]["wa_id"]
                    prompt = data_json['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                    array_message = {"role": "user", "content": prompt}
                    message = self.start_prompt(message=array_message)
                    self.sent_message(numero, message)
                    array_message = ""
                    return Response("ok")
                else:
                    content = {'messages update': 'message update status'}
                    return Response(content, status=status.HTTP_200_OK)
