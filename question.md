Create a docker-compose.yaml file with the following services
- Authsvc
- adminsvc
- agendasvc

Each service shall have its own Dockerfile and deployed in different containers
All the applications will share a common environment file named:
- odontocare.env

The "odontocare.env" has a variable named SECRET_KEY that has a random value passed by the OS, and different each time the compose is initialized
