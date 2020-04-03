FROM alpine:latest

RUN apk update
RUN apk add nginx
RUN mkdir /mnt/applications
RUN rm /etc/nginx/conf.d/default.conf
COPY app_registry.conf /etc/nginx/conf.d/app_registry.conf
RUN mkdir -p /run/nginx
CMD ["nginx", "-g", "daemon off;"]
