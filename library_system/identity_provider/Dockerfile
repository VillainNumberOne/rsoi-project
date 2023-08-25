FROM python:3
WORKDIR /code
COPY . /code/

RUN pip install -r requirements.txt

EXPOSE 8000
ENV PORT=8000

CMD ["sh", "./entrypoint.sh"]