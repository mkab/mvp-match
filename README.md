# Vending Machine Documentation

## Requirements
- Python >= 3.9.7
- Poetry >= 1.1.12 

## Installation

1. ```poetry init``` (inititalise poetry virtual environment)
2. ```poetry install``` (installs dependencies)
3. Go to the vending-machine directory and run: \
 ```python manage.py makemigrations && python manage.py migrate```
4. Run the django server: ```python manage.py runserver```
5. The server will be running on your localhost at http://127.0.0.1:8000/
6. Play with the requests in the Postman collection


# User token
Authentication is done using Django REST Framework's TokenAuthentication. \
Most of the endpoints need the user to be authenticated. \
When a user (buyer or seller) is created, a token is automatically assigned to the user. To get the token make a POST request to the ```api-token-auth``` endpoint. \
You can find it in the Postman collection.
