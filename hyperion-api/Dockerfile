FROM python:3.6

ADD . /code 
RUN apt-get update
RUN pip install -r /code/pip-requirements.txt

WORKDIR /code
ENV PYTHONPATH '/code/'

EXPOSE 80
EXPOSE 8000

CMD ["python" , "/code/collector.py"]