from python:3

WORKDIR /usr/src/app

COPY helloworld.py ./
CMD [ "python", "./test.py" ]
