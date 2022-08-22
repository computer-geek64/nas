# Dockerfile
FROM ubuntu:latest
WORKDIR /code

ENTRYPOINT ["smbd"]
CMD ["-F", "--no-process-group"]

COPY healthcheck.sh /
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD /healthcheck.sh

RUN apt-get update --fix-missing
RUN apt-get install -y samba

COPY src .
RUN cp smb.conf /etc/samba/smb.conf
RUN mkdir -p /data

RUN useradd -ms /bin/false ashish
RUN useradd -ms /bin/false melvin
RUN useradd -ms /bin/false joy
