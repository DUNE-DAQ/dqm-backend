FROM docker.io/library/almalinux:9

LABEL "com.example.vendor"="ACME Incorporated"
LABEL com.example.label-with-value="foo"
LABEL org.opencontainers.image.authors="SOMEADDRESS@example.com"
LABEL version="XXXXXXXXXXXXXXX"
LABEL description="This text illustrates \
that label-values can span multiple lines."

EXPOSE 8000

USER root

RUN dnf clean expire-cache ; dnf -y install git python3-pip python3-pip-wheel; dnf clean all

WORKDIR /src
RUN git clone https://github.com/DUNE-DAQ/dqm-backend.git

RUN pip3 install -r /src/dqm-backend/dqm/dqm/requirements.txt

RUN ["chmod", "+x", "/src/dqm-backend/pkg/oci/consumer.sh", "/src/dqm-backend/pkg/oci/web_application.sh"]
RUN ["ln", "-s", "/src/dqm-backend/pkg/oci/consumer.sh", "/src/dqm-backend/pkg/oci/web_application.sh", "/"]

WORKDIR /src/dqm-backend/dqm
ENTRYPOINT /web_application.sh