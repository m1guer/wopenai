from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
import json
import requests
import os
import openai

from openai_prompt.models import ChatHistory, OpenaiModel


class OpenAiViewSet(viewsets.ViewSet):
    def _init_(self):
        self.message_responses = {}

    def start_prompt(self, message):
        openai.api_key = os.getenv("OPEN_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=message,
            max_tokens=3800,
            stop=None,
            temperature=0.7
        )
        print(message)
        for choice in response.choices:
            if "message" in choice and "content" in choice.message:
                return choice.message.content
        message = ""
        return response.choices[0].message.content

    def clear_responses(self):
        self.message_responses = {}

    def sent_message(self, numero, message):
        url = "https://graph.facebook.com/v16.0/102030192918232/messages"
        headers = {
            "Authorization": "Bearer EAAQvHeAZBZA4MBAJEVzTMiIMKjlT5YO5hGPxEre7357ENmFBIE3dqxOKo4B0KFJyRzYtTL2eU97NAGcV0PgiISH7UmGdECsXr7woLONkg061gIMznUyjWbWZCHrGycr7rNoMOl9GePXrbLLZCd99rCuzzvu0EH0HPoa9DuPh1A7ZAMx7qhBYix64XPIpg0qEcVZBSmq0gFdwZDZD",
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
        data_json = request.data
        conversation_id = data_json["entry"][0]["id"]

        message_log = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        openaiModel = OpenaiModel()
        if request.method == 'GET':
            hub_challenge = request.query_params.get('hub.challenge')
            data = json.loads(hub_challenge)
            return Response(data)
        if request.method == 'POST':
            if 'contacts' in data_json['entry'][0]['changes'][0]['value']:
                message_id = data_json['entry'][0]['changes'][0]['value']['messages'][0]['id']
                queryset = OpenaiModel.objects.filter(
                    conversation_id=conversation_id)
                if queryset.exists():
                    numero = data_json['entry'][0]['changes'][0]['value']['contacts'][0]["wa_id"]
                    prompt = data_json['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                    message_id = data_json['entry'][0]['changes'][0]['value']['messages'][0]['id']
                    message_queryset = OpenaiModel.objects.filter(
                        waid=message_id)
                    if message_queryset.exists():
                        return Response({'sent': 'message already sent'})
                    else:
                        message_log.append(
                            {"role": "user", "content": prompt})
                        print("AAAAAAAAAAAAAAAAA")
                        queryset_chat_infos = OpenaiModel.objects.get(
                            conversation_id=conversation_id)

                        chat_history = ChatHistory()
                        for message in message_log:
                            chat_history.conversation = queryset_chat_infos
                            chat_history.role = message["role"]
                            chat_history.content = message["content"]
                            chat_history.save()
                        message_logs_query = ChatHistory.objects.filter(
                            conversation_id=queryset_chat_infos)
                        new_messages_log = []
                        for chat_messages in message_logs_query:
                            role = chat_messages.role
                            content = chat_messages.content
                            new_messages_log.append(
                                {"role": role, "content": content})
                        message = self.start_prompt(message=new_messages_log)
                        new_messages_log.append(
                            {"role": "assistant", "content": message})
                        chat_history.conversation = queryset_chat_infos
                        chat_history.role = "assistant"
                        chat_history.content = message
                        chat_history.save()
                        self.sent_message(numero, message)
                        return Response("OK")
                else:
                    numero = data_json['entry'][0]['changes'][0]['value']['contacts'][0]["wa_id"]
                    prompt = data_json['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                    if queryset.exists():
                        return Response({"message already send."})
                    elif queryset.none:
                        message_log.append(
                            {"role": "user", "content": prompt})
                        message = self.start_prompt(message=message_log)
                        message_log.append(
                            {"role": "assistant", "content": message})
                        self.sent_message(numero, message)
                        openaiModel.waid = message_id
                        openaiModel.conversation_id = conversation_id
                        openaiModel.save()

                        queryset_chat_infos = OpenaiModel.objects.get(
                            waid=message_id)

                        for message in message_log:
                            chat_history = ChatHistory()
                            chat_history.conversation = queryset_chat_infos
                            chat_history.role = message["role"]
                            chat_history.content = message["content"]
                            chat_history.save()

                        return Response("ok")
                    else:
                        content = {'messages update': 'message update status'}
                        return Response(content, status=status.HTTP_200_OK)
            else:
                return Response("OK")
