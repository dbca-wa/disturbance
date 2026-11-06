# syntax = docker/dockerfile:1

ARG IMAGE_TAG
ARG IMAGE_NAME

# Prepare the base environment.
FROM ghcr.io/dbca-wa/docker-apps-dev:ubuntu_2604_base_python_node26 AS builder_base_das

LABEL maintainer="asi@dbca.wa.gov.au"
LABEL org.opencontainers.image.source="https://github.com/dbca-wa/disturbance"

ARG IMAGE_TAG
ARG IMAGE_NAME

RUN echo "Building version: $IMAGE_TAG for $IMAGE_NAME"

ENV CONTAINER_IMAGE_TAG=${IMAGE_TAG} \
    CONTAINER_IMAGE_NAME=${IMAGE_NAME} \
    DEBIAN_FRONTEND=noninteractive \
    DEBUG=True \
    TZ=Australia/Perth \
    EMAIL_HOST="smtp.corporateict.domain" \
    DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au' \
    NOTIFICATION_EMAIL='' \
    NON_PROD_EMAIL='' \
    PRODUCTION_EMAIL=True \
    EMAIL_INSTANCE='DEV' \
    SECRET_KEY="ThisisNotRealKey" \
    SITE_PREFIX='das-apiary' \
    SITE_DOMAIN='localhost' \
    OSCAR_SHOP_NAME='Parks & Wildlife' \
    BPAY_ALLOWED=False \
    APIARY_SUPPORT_EMAIL="apiary@dbca.wa.gov.au" \
    SUPPORT_EMAIL="das@dbca.wa.gov.au" \
    SYSTEM_NAME_SHORT="apiary" \
    APIARY_URL="['apiary-uat-internal.dbca.wa.gov.au', 'apiary-uat.dbca.wa.gov.au', 'localhost:8071']" \
    SYSTEM_NAME="Disturbance Assessment System" \
    APIARY_SYSTEM_NAME="Apiary System" \
    PAYMENT_OFFICERS_GROUP="Apiary Payments Officers" \
    VIRTUAL_ENV=/app/venv

ENV PATH=$VIRTUAL_ENV/bin:$PATH

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends run-one imagemagick libspatialindex-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN update-ca-certificates

COPY startup.sh /
COPY ./timezone /etc/timezone
RUN chmod 755 /startup.sh && \
    chmod +s /startup.sh && \
    groupadd -g 5000 oim && \
    useradd -g 5000 -u 5000 oim -s /bin/bash -d /app && \
    mkdir /app /container-config/ && \
    chown -R oim:oim /app /container-config/ && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    touch /app/rand_hash

# Install Python libs from requirements.txt.
FROM builder_base_das AS python_libs_das
WORKDIR /app
USER oim
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH=/app/venv/bin:$PATH
RUN git config --global --add safe.directory /app
COPY --chown=oim:oim requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_das
COPY --chown=oim:oim gunicorn.ini.py manage_ds.py ./
RUN touch /app/.env
COPY --chown=oim:oim .git ./.git
COPY --chown=oim:oim python-cron python-cron
COPY --chown=oim:oim disturbance ./disturbance
COPY --chown=oim:oim ledger ./ledger
RUN mkdir -p /app/disturbance/static/disturbance_vue/static && \
    ls -al /app/disturbance/frontend/disturbance && \
    cd /app/disturbance/frontend/disturbance && npm ci && npm run build
RUN python manage_ds.py collectstatic --noinput && \
    mkdir /app/tmp/ && \
    chmod 777 /app/tmp/

# Cleanup
USER root
RUN apt-get update && apt-get install -y --no-install-recommends libnetcdf-dev && apt-mark manual libnetcdf-dev
RUN wget -q https://raw.githubusercontent.com/dbca-wa/wagov_utils/refs/heads/main/wagov_utils/bin/package_cleanup_2604.sh -O /tmp/package_cleanup_2604.sh || true && \
    chmod 755 /tmp/package_cleanup_2604.sh || true && \
    /tmp/package_cleanup_2604.sh || true
USER oim

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]