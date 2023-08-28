FROM python:3
WORKDIR /code
COPY . /code/

RUN pip install -r requirements.txt

EXPOSE 8020
ENV PORT=8020

CMD ["sh", "./entrypoint.sh"]