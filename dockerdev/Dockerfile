# Prepare the base environment.
FROM ghcr.io/dbca-wa/disturbance:latest_seg AS builder_base_disturbancedev
USER root

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    g++ \
    git \
    libpq-dev \
    screen && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 -subj "/C=AU/ST=Western Australia/L=Perth/O=Development Environment/OU=IT Department/CN=example.com" -keyout /etc/ssl/private/selfsignedssl.key -out /etc/ssl/private/selfsignedssl.crt

RUN echo 'if ! [ -n "${SUDO_USER}" -a -n "${SUDO_PS1}" ]; then' >> /etc/bash.bashrc && \
    echo "export PS1='\[\e[;31m\]dev:\[\e[m\] \[\e[;32m\]\u@\h:\w \$ \[\e[m\]'" >> /etc/bash.bashrc && \
    echo "fi" >> /etc/bash.bashrc

# For Linux
RUN groupadd -g 20000 container && \
    useradd -g 20000 -u 200000 container -s /bin/bash && \
    mkdir /home/container && \
    chown container:container /home/container && \
    cp /root/.bashrc /home/container && \
    cp /root/.profile /home/container && \
    chown container:container /home/container/.bashrc /home/container/.profile

USER container
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]