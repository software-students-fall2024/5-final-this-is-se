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



## How To Test
1. Install pipenv (Suppose you have python. If not, download python first)
    ```
    pip install pipenv
    ```


2. Install Project Dependencies with Pipenv
    ```
    pipenv install --dev
    ```


3. Run Virtual Environment
    ```
    pipenv shell
    ```
4. Enter Editor Mode
    ```
    pip install -e .
    ```

5. Run pytest/python files
    ```
    pytest
    ```




## Contributing
1. Fork the Repository:
- [Our Project](https://github.com/software-students-fall2024/5-final-this-is-se.git)
- Open our package and click "fork" to save files in your own repository


2. Clone the Repository:<br>
In your own repository, use<br>
    ```
    git clone <repository-url>
    ```


3. Navigate into the Project Directory<br>
    ```
    cd <project-repo>
    ```


4. Create a New Branch for Your Changes:<br>
    ``` 
    git checkout -b feature/my-new-feature
    ```


5. Install Dependencies<br>
    see __How To Test/Run__


6. Make Changes or Add Features


7. Stage Your Changes<br>
    ```
    git add <file-name>
    ```


8. Commit Your Changes<br>
    ```
    git commit -m "your commit"
    ```


9. Push Your Branch to Your Fork<br>
    ```
    git push origin feature/my-new-feature
    ```


10. Create a Pull Request <br>
In the PR, describe the changes you made and their purpose