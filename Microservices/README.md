
## Microservices

### Актуальный гайд как запускать контур: 

1) Удалить существующий стэк микросервисов. <br>
   ```docker stack rm matcher```
2) Собрать нужные образы. <br>
   ```docker-compose build```
3) Поднять стэк матчера. <br>
   ```docker stack deploy -c ./docker-compose.yaml matcher```


<hr> 

### Команда на проброс портов: <br>
    ```---```
<hr>

### Ссылки на сервисы:

http://localhost:3000/grafana - grafana

http://localhost:8081/ - ui

http://localhost:8089/ - kafka

http://localhost:8080/ - swagger backend ui

http://localhost:8080/ - swagger backend matcher

<hr>

### Полезные команды
- Туннелирование к сервисам на локальном хосте:
  ```---```
  - Пользоваветельский интерфейс будет по пути - ```localhost:8081```
  - Свагер бэкенда - ``````
- Просмотр подов стэка микросервисов: ```docker stack services matcher```
- Удаление стэка микросервисов: ```docker stack rm matcher```
- Просмотр списка network: ```docker network ls```
- Просмотр логов: ```docker service logs {microservice-name}```
- Просмотр network: ```docker network inspect matcher-network-v2```
- Cоздания локального ssh-туннеля: <br>
   ```---```
   <br> Так как у проекта 3 микросервиса, потребуется 3 ssh-туннеля для получения доступа к каждому компоненту. <br>
   **Порты**, на которых работают микросервисы на сервере:
  - Матчер: ```8083```
  - Бэкенд: ```8084```
  - Фронтенд: ```8085```
- Просмотр ресурсов контейнера: ```docker container stats {container_id}```

### Grafana 
- Ссылка на grafana: `http://localhost:3000/grafana`
- При первом входе: 
- login: `---`, password: `---`
- Для вывода метрик нужно:
- a) Добавить prometheus в data sources, url - `http://prometheus:9090`
- b) Импортировать dashboard, используя grafana_dashboard.json 
<hr>
