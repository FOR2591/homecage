FROM node:16.13.0 AS frontend
RUN apt update && apt install protobuf-compiler -y 

WORKDIR /opt/homecage/frontend

# Install frontend source dependancies
COPY ./frontend/*.json ./
RUN npm install

# Build frontend
COPY ./frontend/src ./src
COPY ./protocol ../protocol

RUN npm run proto:generate
RUN npm run build


FROM node:16.13.0 as server
EXPOSE 3100

RUN apt update && apt install protobuf-compiler -y 

WORKDIR /opt/homecage/server

# Install backend source dependancies
COPY ./backend/*.json ./
RUN npm install

# Build backend
COPY ./backend/src ./src
COPY ./protocol ../protocol

RUN npm run proto:generate
RUN npm run build

COPY --from=frontend /opt/homecage/frontend/dist/homecage-frontend/ ./dist/webapp

COPY ./run.sh ./
RUN chmod +x run.sh

CMD ["./run.sh"]
