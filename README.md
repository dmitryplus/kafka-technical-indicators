# Микросервисная архитектура вычисления значений технических индикаторов фондового рынка в реальном времени на основе Apache Kafka

Проектная работа по курсу "Apache Kafka" от компании OTUS


## Структура проекта

![structure.svg](structure.svg)


## Запуск проекта

Переименовываем файл `.env.template` в `.env`

В поле `TOKEN` прописываем токен для доступа к API Т-Инвестиций (https://www.tbank.ru/profile/security/)

Запускаем `docker-compose up -d`

## Описание контейнеров

### kafka-init-topics

Сервис создания топиков kafka. Запускается однократно после запуска kafka. Создает структуру топиков с нужными настройками партиций и репликации.

Топики значений индикаторов пересоздаются каждый раз, остальные по необходимости (если отсутствуют)

```YML
  kafka-init-topics:
    image: confluentinc/cp-kafka:7.0.9
    container_name: kafka-init-topics-terminal-helper
    depends_on:
      - kafka1
    command: bash -c 'echo "Waiting for Kafka to be ready..." &&
      cub kafka-ready -b ${KAFKA_CONNECT} 1 30 &&
      echo "Create config topic..." &&
      kafka-topics --create --topic ${TOPIC_CONFIG} --partitions 1 --replication-factor 1 --config cleanup.policy=compact --config delete.retention.ms=10 --config min.cleanable.dirty.ratio=0.1 --config min.compaction.lag.ms=10 --config max.compaction.lag.ms=100 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      echo "Create candles topics..." &&
      kafka-topics --create --topic "candles-1-min" --partitions 10 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "candles-5-min" --partitions 10 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "candles-15-min" --partitions 10 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "candles-30-min" --partitions 10 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "candles-1-hour" --partitions 10 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "candles-4-hour" --partitions 10 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "candles-1-day" --partitions 10 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      echo "Create candle gaps topics..." &&
      kafka-topics --create --topic "gaps" --partitions 12 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      echo "Create candle history-action topics..." &&
      kafka-topics --delete --topic "history-action" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "history-action" --partitions 12 --replication-factor 1 --if-not-exists --bootstrap-server ${KAFKA_CONNECT} &&
      echo "Create indicator values topics..." &&
      kafka-topics --delete --topic "macd-values-1-min" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "macd-values-1-min" --partitions 10 --replication-factor 1 --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --delete --topic "macd-values-5-min" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "macd-values-5-min" --partitions 10 --replication-factor 1 --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --delete --topic "macd-values-15-min" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "macd-values-15-min" --partitions 10 --replication-factor 1 --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --delete --topic "macd-values-30-min" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "macd-values-30-min" --partitions 10 --replication-factor 1 --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --delete --topic "macd-values-1-hour" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "macd-values-1-hour" --partitions 10 --replication-factor 1 --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --delete --topic "macd-values-4-hour" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "macd-values-4-hour" --partitions 10 --replication-factor 1 --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --delete --topic "macd-values-1-day" --if-exists --bootstrap-server ${KAFKA_CONNECT} &&
      kafka-topics --create --topic "macd-values-1-day" --partitions 10 --replication-factor 1 --bootstrap-server ${KAFKA_CONNECT} &&
      exit 0'

    network_mode: host
```