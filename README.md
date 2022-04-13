# event_management_api
Event management api using DRF, PostgreSQL

### TO RUN the project
Start Docker 
```shell
docker-compose up --build
```
The above command will start the project after build. 
Base URL is http://localhost:8080

To access project shell
```shell
docker exec -it  event_app bash
```
You can run python command in project shell above
```shell

List of APIs
- `accounts/token` - Fetch token for user
- `accounts/signup` - Register user
- `events` - create event and get list of events
- `events/<pk>` - event details/ update
- `events/tickets` - Ticket booking and get list of tickets
- `events/tickets/<pk>` - ticket details by id
- `events/<pk>/summary` - summary of event










