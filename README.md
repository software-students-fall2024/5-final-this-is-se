[![log github events](https://github.com/software-students-fall2024/5-final-this-is-se/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-this-is-se/actions/workflows/event-logger.yml)
[![Web Application CI](https://github.com/software-students-fall2024/5-final-this-is-se/actions/workflows/web-app.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-this-is-se/actions/workflows/web-app.yml)

# Final Exercise
## Introduction

"Pet Circle" is a containerized, cloud-enabled web application that functions as a pet-centric version of Instagram. It allows users to register, log in, and share their pet stories by uploading images for others to view, like, and comment on. Users can explore diverse profiles, follow the accounts they find appealing, and build a personalized feed showcasing only the posts from those they follow. Additionally, a built-in chat feature encourages direct interaction between users. For personalization, the platform lets users easily update their usernames whenever they wish. In short, Pet Circle is an engaging, community-driven space dedicated to celebrating beloved pets and the people who care for them.

## Deploy Site
http://138.197.92.147:5002

## Team

- [Ziqiu (Edison) Wang](https://github.com/ziqiu-wang)
- [Thomas Chen](https://github.com/ThomasChen0717)
- [An Hai](https://github.com/AnHaii)
- [Annabella Lee](https://github.com/annabellalee0113)
- [Kevin Zhang](https://github.com/yz7669)

## Installation

__Prerequisite__: 
Before running this application, ensure that you have the following installed:

- Docker: [Installation Guide](https://docs.docker.com/get-docker/)
- Docker Compose: [Installation Guide](https://docs.docker.com/compose/install/)
- Python 3.9 or higher (for local testing)

__ToDo__:

1.  Access
- docker-compose up --build
- Go to http://localhost:5002 
- Stop: docker-compose down

2. test
- cd app
- pip install -r requirements.txt
- pip install pytest
- pytest
