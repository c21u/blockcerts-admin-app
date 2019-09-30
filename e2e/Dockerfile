FROM cypress/base:10
WORKDIR /app

ENV CI=1

COPY package.json .
COPY yarn.lock .

RUN yarn install
RUN npx cypress verify