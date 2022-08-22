# Dockerfile
FROM nextcloud:latest

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]

COPY healthcheck.sh /
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD /healthcheck.sh
