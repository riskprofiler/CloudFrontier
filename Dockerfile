FROM nikolaik/python-nodejs:python3.8-nodejs14-alpine

WORKDIR /cloud-frontier

COPY package.json package.json
RUN npm i --save-dev && npm cache clean --force
ENV PATH /cloud-frontier/node_modules/.bin:$PATH

COPY . .

ENTRYPOINT [ "./deploy.sh" ]
