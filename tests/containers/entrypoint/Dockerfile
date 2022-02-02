ARG EL=7

FROM centos:centos$EL

# "ARG EL" needs to be here again because the previous instance has gone out of scope.
ARG EL=7
ARG CONDOR_SERIES=9.0

RUN groupadd -o -g 9619 testuser && \
    useradd -m -u 9619 -g 9619 -s /bin/bash testuser

WORKDIR /src

# Install dependencies
RUN \
    if  [[ $EL == 7 ]]; then \
       YUM_PKG_NAME="yum-plugin-priorities"; \
       yum-config-manager \
         --setopt=skip_missing_names_on_install=False \
         --setopt=skip_missing_names_on_update=False \
         --save > /dev/null; \
    else \
       YUM_PKG_NAME="yum-utils"; \
    fi && \
    yum update -y && \
    yum install -y https://research.cs.wisc.edu/htcondor/repo/${CONDOR_SERIES}/htcondor-release-current.el${EL}.noarch.rpm \
                   $YUM_PKG_NAME && \
    if [[ $OS_VERSION != 7 ]]; then \
       yum-config-manager --enable powertools; \
    fi && \
    yum install -y git \
                   make \
                   supervisor \
                   htcondor-ce \
                   htcondor-ce-view && \

    # Install the CA generator tool
    git clone https://github.com/opensciencegrid/osg-ca-generator && \
    cd osg-ca-generator && \
    make install DESTDIR=/ && \
    mkdir -p /etc/condor-ce/image-{cleanup,init}.d

# Container-specific config
COPY tests/containers/entrypoint/renew-demo-token.py      /usr/local/bin/
COPY tests/containers/entrypoint/supervisord_startup.sh   /usr/local/sbin/
COPY tests/containers/entrypoint/supervisord.conf         /etc/
COPY tests/containers/entrypoint/10-personal-condor.conf  /etc/condor/config.d/
COPY tests/containers/entrypoint/10-ce.conf               /etc/condor-ce/config.d/
COPY tests/containers/entrypoint/10-token-creds.sh        /etc/condor-ce/image-init.d/
COPY tests/containers/entrypoint/10-x509-creds.sh         /etc/condor-ce/image-init.d/
COPY tests/containers/entrypoint/10-hostname.sh           /etc/condor-ce/image-init.d/

# Install the relevant bits from source
COPY . /src/htcondor-ce
RUN cd htcondor-ce/ && \
    make entrypoint DESTDIR=/ 

CMD ["/usr/local/sbin/supervisord_startup.sh"]
