# Prepare the base environment.
# Based on the Dockerfile: https://github.com/dbca-wa/commercialoperator/blob/cols_fe_py3/Dockerfile
FROM ubuntu:22.04 as builder_base_cols
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBUG=True
ENV TZ=Australia/Perth
ENV EMAIL_HOST="smtp.corporateict.domain"
ENV DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au'
ENV NOTIFICATION_EMAIL='brendan.blackford@dbca.wa.gov.au'
ENV NON_PROD_EMAIL='brendan.blackford@dbca.wa.gov.au, walter.genuit@dbca.wa.gov.au, katsufumi.shibata@dbca.wa.gov.au,test_licensing@dpaw.wa.gov.au,jawaid.mushtaq@dbca.wa.gov.au,kelly.thomas@dbca.wa.gov.au,matthew.king@dbca.wa.gov.au,ashlee.russell@dbca.wa.gov.au,aaron.farr@dbca.wa.gov.au'
ENV PRODUCTION_EMAIL=False
ENV EMAIL_INSTANCE='DEV'
ENV SECRET_KEY="ThisisNotRealKey"
ENV SITE_PREFIX='das-apiary'
ENV SITE_DOMAIN='dbca.wa.gov.au'
ENV OSCAR_SHOP_NAME='Parks & Wildlife'
ENV BPAY_ALLOWED=False
ENV APIARY_SUPPORT_EMAIL="apiary@dbca.wa.gov.au"
ENV SUPPORT_EMAIL="das@dbca.wa.gov.au"
ENV SYSTEM_NAME_SHORT="apiary"
ENV SITE_DOMAIN="localhost"
ENV APIARY_URL=[u'apiary-uat-internal.dbca.wa.gov.au',u'apiary-uat.dbca.wa.gov.au',u'localhost:8071']
ENV SYSTEM_NAME="Disturbance Assessment System"
ENV APIARY_SYSTEM_NAME="Apiary System"
ENV PAYMENT_OFFICERS_GROUP="Apiary Payments Officers"

# Use Australian Mirrors
RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list
RUN mv /etc/apt/sourcesau.list /etc/apt/sources.list
# Use Australian Mirrors

#ARG build_tag=None
#ENV BUILD_TAG=$build_tag
#RUN echo "*************************************************** Build TAG = $build_tag ***************************************************"

RUN apt-get update && apt-get install -y software-properties-common

RUN apt-get clean && \
apt-get upgrade -y && \
apt-get install --no-install-recommends -y \
wget \
git \
libmagic-dev \
gcc \
binutils \
libproj-dev \
gdal-bin \
python3-setuptools \
python3-pip \
tzdata \
cron \
rsyslog \
gunicorn \
libreoffice \
libpq-dev \
patch \
postgresql-client \
mtr \
htop \
vim \
#ssh \
python3-gevent \
software-properties-common \
imagemagick \
libspatialindex-dev \
npm 

RUN add-apt-repository ppa:deadsnakes/ppa

#RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
#RUN apt-get install --no-install-recommends -y python3.7
RUN apt-get install --no-install-recommends -y python3.7 python3.7-dev python3.7-distutils 
RUN ln -s /usr/bin/python3.7 /usr/bin/python && \
python3.7 -m pip install --upgrade pip==21.3.1 && \
apt-get install -yq vim

# Install Python libs from requirements.txt.
FROM builder_base_cols as python_libs_cols
WORKDIR /app
COPY requirements.txt ./
RUN python3.7 -m pip install --no-cache-dir -r requirements.txt \
  # Update the Django <1.11 bug in django/contrib/gis/geos/libgeos.py
  # Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
  # && sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python2.7/dist-packages/django/contrib/gis/geos/libgeos.py \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

COPY libgeos.py.patch /app/
RUN patch /usr/local/lib/python3.7/dist-packages/django/contrib/gis/geos/libgeos.py /app/libgeos.py.patch && \
rm /app/libgeos.py.patch

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_cols
COPY gunicorn.ini manage_ds.py ./
#COPY timezone /etc/timezone
ENV TZ=Australia/Perth
RUN echo "Australia/Perth" > /etc/timezone && \
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
echo $TZ > /etc/timezone && \
touch /app/.env
COPY .git ./.git
COPY disturbance ./disturbance
RUN mkdir -p /app/disturbance/static/disturbance_vue/static
RUN cd /app/disturbance/frontend/disturbance; npm install
RUN cd /app/disturbance/frontend/disturbance; npm run build
RUN python manage_ds.py collectstatic --noinput && \
mkdir /app/tmp/ && \
chmod 777 /app/tmp/

COPY cron /etc/cron.d/dockercron
COPY startup.sh /
# Cron start
#RUN service rsyslog start
RUN chmod 0644 /etc/cron.d/dockercron
RUN crontab /etc/cron.d/dockercron
RUN touch /var/log/cron.log
RUN service cron start
RUN chmod 755 /startup.sh
# cron end

# IPYTHONDIR - Will allow shell_plus (in Docker) to remember history between sessions
# 1. will create dir, if it does not already exist
# 2. will create profile, if it does not already exist
RUN mkdir /app/logs/.ipython
RUN export IPYTHONDIR=/app/logs/.ipython/
#RUN python profile create


EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
#CMD ["gunicorn", "commercialoperator.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]
