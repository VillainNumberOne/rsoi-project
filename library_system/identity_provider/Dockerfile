FROM python:3
WORKDIR /code
COPY . /code/

RUN pip install -r requirements.txt

ENV PORT=8000
EXPOSE $PORT

CMD ["sh", "./entrypoint.sh"]