# Микросервисная архитектура вычисления значений технических индикаторов фондового рынка в реальном времени на основе Apache Kafka

Проектная работа по курсу "Apache Kafka"


## Структура проекта

![structure.svg](structure.svg)


## Запуск проекта

Переименовываем файл `.env.template` в `.env`

В поле `TOKEN` прописываем токен для доступа к API Т-Инвестиций (https://www.tbank.ru/profile/security/)

Запускаем `docker-compose up -d`