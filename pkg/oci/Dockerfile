FROM docker.io/library/almalinux:9

LABEL "com.example.vendor"="ACME Incorporated"
LABEL com.example.label-with-value="foo"
LABEL org.opencontainers.image.authors="SOMEADDRESS@example.com"
LABEL version="XXXXXXXXXXXXXXX"
LABEL description="This text illustrates \
that label-values can span multiple lines."

EXPOSE 8000

RUN dnf clean expire-cache ; dnf -y install git python3-pip python3-pip-wheel; dnf clean all
RUN python3 -m pip install wheel ; python3 -m pip cache remove '*'

WORKDIR /src
RUN git clone https://github.com/DUNE-DAQ/dqm-backend.git

RUN python3 -m pip install -r /src/dqm-backend/dqm/dqm/requirements.txt ; python3 -m pip cache remove '*'
RUN chmod 1770 /src/dqm-backend/dqm/dqm

RUN chmod +x /src/dqm-backend/pkg/oci/consumer.sh /src/dqm-backend/pkg/oci/web_application.sh \
    && ln -s /src/dqm-backend/pkg/oci/consumer.sh /src/dqm-backend/pkg/oci/web_application.sh /

RUN mkdir -p /src/dqm-backend/dqm/dqm/display/migrations && chmod 1770 /src/dqm-backend/dqm/dqm/display/migrations
RUN mkdir -p /src/dqm-backend/dqm/dqm/staticfiles && chmod 1770 /src/dqm-backend/dqm/dqm/staticfiles

# preserve root GID following common practices for dynamic container IDs
USER nobody:root
WORKDIR /src/dqm-backend/dqm
ENV TZ=UTC
ENTRYPOINT /web_application.sh
