FROM pdonorio/pyservs
MAINTAINER "Amy Krause <a.krause@epcc.ed.ac.uk>"


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