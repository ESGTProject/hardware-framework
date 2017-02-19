FROM python:2.7-alpine

# Install dependencies for psycopg2
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
        apk add postgresql-dev

# Add current directory into /code directory in image
ADD . /code

# Change directory in image to /code
WORKDIR /code

# Add requirements
RUN pip install -r requirements.txt

# Set default command
CMD ["python", "app.py"]

