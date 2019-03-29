FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install -e git+https://github.com/blockchain-certificates/cert-tools#egg=cert-tools
ADD . /code/
WORKDIR /code
CMD ["sh", "run.sh"]
