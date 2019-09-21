# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с логами.
import logging

# Импортируем модуль для работы с API Алисы
from alice_sdk import AliceRequest, AliceResponse

# Импортируем модуль с логикой игры
from main_function import *

# Импортируем модуль работы с базами данных
import postgresql_database

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)

import pymorphy2


# Хранилище данных о сессиях.
session_storage = {}

logging.basicConfig(level=logging.DEBUG)


def init_database(host, user, password, dbname):
    """
    =================================================================
    Значения по умолчанию подавать по следующему шаблону:
    'column_name': "type DEFAULT value", где value в зависомости от
    типа ДОЛЖНО принимать следующие значения:
    INTEGER -> 0; REAL -> 0.00; TEXT -> 'text here'; BOOLEAN -> True;
    list -> '[entry1#&% запись2 #&% "3"]'
    =================================================================
    """
    psdb = postgresql_database.DatabaseManager(host, user, password, dbname)
    psdb.create_table("users_info",
                      {'user_id': "serial primary", "request_id": "str NOT NULL UNIQUE",
                       "mode": "str DEFAULT 'null'", "Name": "str DEFAULT 'null'", "Named": "bool DEFAULT False",
                       "eng_words": "str DEFAULT ''", "rus_words": "str DEFAULT ''",
                       "learned_eng_words": "str DEFAULT ''", "learned_rus_words": "str DEFAULT ''",
                       "training_score": "str DEFAULT ''", "q_count": "int DEFAULT 0", "q_true": "int DEFAULT 0",
                       "q": "str DEFAULT ''", "word_sets": "str DEFAULT ''"
                       })
    return psdb


@app.route("/life_simulation/ping")
def mainn():
    return "pong"


# Задаем параметры приложения Flask.
@app.route("/alice_hackaton/", methods=['POST'])
def main():
    database = init_database(host='localhost', user='postgres3', password='1488',
                             dbname='programmer_simulator')

    # Функция получает тело запроса и возвращает ответ.
    alice_request = AliceRequest(request.json)
    logging.info('Request: {}'.format(alice_request))
    morph = pymorphy2.MorphAnalyzer()
    alice_response = AliceResponse(alice_request)

    user_id = alice_request.user_id
    print(user_id)
    print(session_storage.get(user_id))
    print(len(session_storage))
    alice_response, session_storage[user_id] = handle_dialog(
        alice_request, alice_response, session_storage.get(user_id), database, morph
    )

    logging.info('Response: {}'.format(alice_response))
    print()

    return alice_response.dumps()


if __name__ == '__main__':
    app.run()
