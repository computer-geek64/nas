# Dockerfile
FROM nginx:latest
WORKDIR /code

COPY src .
RUN cp nginx.conf /etc/nginx/nginx.conf

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
