FROM python:3
WORKDIR /code
COPY . /code/

RUN pip install -r requirements.txt

EXPOSE 8010
ENV PORT=8010

CMD ["sh", "./entrypoint.sh"]