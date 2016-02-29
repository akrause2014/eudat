FROM pdonorio/py3api
MAINTAINER "Amy Krause <a.krause@epcc.ed.ac.uk>"

# Install dependencies
RUN apt-get update && apt-get install -y \
    libfuse2 \
    && apt-get clean


###############################
# IRODS

# Environments
ENV IRODSVERSION 4.1.8
ENV IRODSFTP "ftp://ftp.renci.org/pub/irods/releases/$IRODSVERSION/ubuntu14"
ENV IRODSPKG "icommands"
ENV IRODSDEB $IRODSFTP/irods-${IRODSPKG}-${IRODSVERSION}-ubuntu14-x86_64.deb

# Icommands
WORKDIR /tmp

RUN wget -q $IRODSDEB \
    && dpkg -i irods*.deb \
    && rm *.deb

ENV GLOBUSGSIDEB http://toolkit.globus.org/ftppub/gt6/installers/repo/globus-toolkit-repo_latest_all.deb


RUN wget -q $GLOBUSGSIDEB \
    && dpkg -i globus-toolkit-repo_latest_all.deb \
    && apt-get update \
    && yes | apt-get -f install \
    && yes | apt-get install globus-gsi

# remove the certificates so they can't be used by mistake
RUN rm -rf /etc/grid-security/*

RUN mkdir /root/.irods
ADD irods_environment.json /root/.irods/irods_environment.json
ADD client.py /root/client.py