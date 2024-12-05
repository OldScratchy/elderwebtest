FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg2 \
    lsb-release \
    python3 \
    python3-pip \
    bash \
    && pip3 install azure-storage-blob elasticsearch \
    && apt-get clean

RUN wget -qO - https://packages.fluentbit.io/fluentbit.key | apt-key add -
RUN echo "deb https://packages.fluentbit.io/debian/$(lsb_release -cs) $(lsb_release -cs) main" > /etc/apt/sources.list.d/fluent-bit.list

RUN mkdir -p /fluent-bit/etc /fluent-bit/python-scripts
RUN mkdir -p /fluent-bit/logs
RUN mkdir -p /fluent-bit/temp

RUN apt-get update && apt-get install -y fluent-bit

COPY fluent-bit.conf /fluent-bit/etc/fluent-bit.conf
COPY parsers.conf /fluent-bit/etc/parsers.conf
COPY elder_web_test.py /fluent-bit/python-scripts/elder_web_test.py

RUN pip install httpx elasticsearch

COPY elder_web_test.py /fluent-bit/elder_web_test.py

COPY fluent-bit.conf /fluent-bit/etc/fluent-bit.conf

CMD ["/opt/fluent-bit/bin/fluent-bit", "-c", "/fluent-bit/etc/fluent-bit.conf"]
