FROM python:3.6.2

LABEL maintainer "Javier Saez <javiersaezgallego@gmail.com>"

# Show output in logs
ENV PYTHONUNBUFFERED=1


RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    && apt-get -y install apt-utils gunicorn libpq-dev python3-dev \
    && apt-get autoremove -y \
    && apt-get clean all
ENV INSTALL_PATH /home/project/dash
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY requirements.txt .
RUN pip install --upgrade pip -r requirements.txt

COPY . .

