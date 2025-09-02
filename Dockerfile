FROM docker.sunet.se/drive/nextcloud-custom:30.0.14.2-3

RUN apt update && apt install -y \
    python3-pip
RUN mkdir -p /var/www/python /var/www/.local && \
    chown -R www-data:www-data /var/www/python /var/www/.local
USER www-data
WORKDIR /var/www/python
COPY src/main.py main.py
COPY src/requirements.txt requirements.txt
RUN pip install --break-system-packages -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["/var/www/.local/bin/fastapi", "run", "./main.py"]
