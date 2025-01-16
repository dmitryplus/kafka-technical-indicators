# Микросервисная архитектура вычисления значений технических индикаторов фондового рынка в реальном времени на основе Apache Kafka

Проектная работа по курсу "Apache Kafka" от компании OTUS


## Описание

Проект реализует систему микросервисов со следующими возможностями:
* получение рыночных данных в реальном времени
* получение исторических данных по определенным интервалам
* сохранение очищенных данных по свечам в kafka
* расчет показателей индикатора MACD по данным из kafka
* вывод данных в вебсокет

Для получения рыночных данных используется [API Т-Инвестиций](https://tinkoff.github.io/investAPI/).


Микросервисы написаны на **python** с использованием библиотек [tinkoff-investments](https://github.com/Tinkoff/invest-python), [kafka-python-ng](https://kafka-python.readthedocs.io/en/master/index.html), ta-lib

## Структура проекта

![structure.svg](structure.svg)

## Запуск

Переименовываем файл `.env.template` в `.env`

В поле `TOKEN` прописываем токен для доступа к API Т-Инвестиций (https://www.tbank.ru/profile/security/)

Запускаем `docker-compose up -d`


## Описание микросервисов

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

### config-app

Сервис хранения настроек системы. Управляет списком инструментов по которым происходит забор данных.

Файл `not_need_tickers.txt` содержит черный список инструментов. 
Файл `need_tickers.txt` содержит список нужных инструментов, если он пустой - берутся данные по всем инструментам, кроме `not_need_tickers.txt`.

Код контейнера лежит в папке - `/images/config`

```YML
  config-app:
    container_name: config-container
    build: images/config
    image: terminal_helper/config:latest
    env_file:
      - .env
    volumes:
      - type: bind
        source: ./src/infrastructure
        target: /infrastructure
        read_only: true
      - type: bind
        source: ./need_tickers.txt
        target: /need_tickers.txt
        read_only: true
      - type: bind
        source: ./not_need_tickers.txt
        target: /not_need_tickers.txt
        read_only: true
    depends_on:
      - kafka1
    network_mode: host
```

### candle-1-min

Cервисы получения данных в реальном времени (по 1 на интервал). Подключаются к API Т-Инвестиций в потоковом режиме, конвертируют полученные данные и складывают результат в соответсвующий топик (`candles-1-min`).

Код контейнера лежит в папке - `/images/candles`

```YML
  candle-1-min:
    container_name: candle-1-min
    build: images/candles
    image: terminal_helper/candles:latest
    env_file:
      - .env
    environment:
      INTERVAL: "${INTERVAL_ONE_MIN}"
    volumes:
      - type: bind
        source: ./src/infrastructure
        target: /infrastructure
        read_only: true
    depends_on:
      - "kafka1"
    network_mode: host
```

### history

Cервис работы с историческими данными из API Т-Инвестиций.

Запускается в 4х экземплярах.

Слушает топик `history-action`, получает данные по инструменту и временному интервалу. Запрашивает исторические данные рынка. Результат кладет в топики по соответствующему интервалу (`candle-1-min`).

Код контейнера лежит в папке - `/images/history`

```YML
  history:
    deploy:
      mode: replicated
      replicas: 4
    build: images/history
    image: terminal_helper/history:latest
    env_file:
      - .env
    volumes:
      - type: bind
        source: ./src/infrastructure
        target: /infrastructure
        read_only: true
      - type: bind
        source: ./images/history/src/market_data_cache
        target: /market_data_cache
        read_only: false
    depends_on:
      - kafka1
    network_mode: host
```


### lack

Сервис отвечает за полноту данных, организует добор недостающих свечей до количества, указанного в env переменной (по умолчанию - 200 для каждого интервала)

Подсчитывает количество свечей в каждом интервале, если меньше необходимого значения для расчета индикатора, то отправляет задание `history` контейнеру в топик `history-action`.

Код контейнера лежит в папке - `/images/lack`

```YML
  lack:
    container_name: lack-container
    build: images/lack
    image: terminal_helper/lack:latest
    env_file:
      - .env
    volumes:
      - type: bind
        source: ./src/infrastructure
        target: /infrastructure
        read_only: true
    depends_on:
      - kafka1
    network_mode: host
```


### gaps-1-min

Cервис поиска пропусков в потоке данных (по 1 на интервал). Ищет возможные сбои в потоке данных (`candles-1-min`) результат складывает в топик `gaps`

Код контейнера лежит в папке - `/images/gaps`

```YML
  gaps-1-min:
    container_name: gaps-container-1-min
    build: images/gaps
    image: terminal_helper/gaps:latest
    env_file:
      - .env
    environment:
      INTERVAL: "${INTERVAL_ONE_MIN}"
    volumes:
      - type: bind
        source: ./src/infrastructure
        target: /infrastructure
        read_only: true
    depends_on:
      - kafka1
    network_mode: host
```

### indicator-macd-1-min

Cервис расчета значений индикатора MACD (по 1 на интервал). Слушает топик `candles-1-min`, расчитывает индикатор, результат складывает в топик `macd-values-1-min`.

Код контейнера лежит в папке - `/images/macd`

```YML
  indicator-macd-1-min:
    container_name: macd-value-container-1-min
    build: images/macd
    image: terminal_helper/macd:latest
    env_file:
      - .env
    environment:
      INTERVAL: "${INTERVAL_ONE_MIN}"
    volumes:
      - type: bind
        source: ./src/infrastructure
        target: /infrastructure
        read_only: true
    depends_on:
      - kafka1
    network_mode: host
```

### websocket-macd-1-min-SBER

Сервисы для трансляции данных из kafka, в данном случае вебсокеты. В настройках необходимо указать топик, инструмент и порт вывода.

Код контейнера лежит в папке - `/images/websocket`

```YML
  websocket-macd-1-min-SBER:
    build: images/websocket
    image: terminal_helper/websocket:latest
    env_file:
      - .env
    environment:
      TOPIC: "macd-values-1-min"
      FIGI: "BBG004730N88"
      PORT: "8001"
    volumes:
      - type: bind
        source: ./src/infrastructure
        target: /infrastructure
        read_only: true
    depends_on:
      - kafka1
    network_mode: host
```