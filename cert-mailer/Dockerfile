FROM python:3.6-alpine as base

FROM base as builder

RUN apk add zlib-dev jpeg-dev build-base

RUN mkdir /install
WORKDIR /install

COPY requirements.txt ./
RUN pip install --install-option="--prefix=/install" -r requirements.txt

FROM base

COPY --from=builder /install /usr/local
RUN apk add busybox libjpeg-turbo

WORKDIR /app
COPY . .

CMD [ "ash" ]
