FROM registry.access.redhat.com/ubi9/ubi-minimal

LABEL "com.example.vendor"="ACME Incorporated"
LABEL com.example.label-with-value="foo"
LABEL org.opencontainers.image.authors="SOMEADDRESS@example.com"
LABEL version="XXXXXXXXXXXXXXX"
LABEL description="This text illustrates \
that label-values can span multiple lines."

EXPOSE 8000

USER root

# installing deps (ubi-minimal has microdnf only)
RUN microdnf clean expire-cache ; microdnf -y install git python3-pip python3-wheel; microdnf clean all

WORKDIR /src
RUN git clone https://github.com/DUNE-DAQ/dqm-backend.git

RUN pip3 install -r /src/dqm-backend/dqm/dqm/requirements.txt

RUN ["chmod", "+x", "/src/dqm-backend/pkg/oci/consumer.sh", "/src/dqm-backend/pkg/oci/web_application.sh"]
RUN ["ln", "-s", "/src/dqm-backend/pkg/oci/consumer.sh", "/src/dqm-backend/pkg/oci/web_application.sh", "/"]

WORKDIR /src/dqm-backend/dqm
ENTRYPOINT /web_application.sh
