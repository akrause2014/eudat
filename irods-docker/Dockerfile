##########################################################################
ENV IRODSVERSION 4.1.8
FROM cineca:icat
MAINTAINER "Amy Krause <a.krause@epcc.ed.ac.uk>"

ENV DEBIAN_FRONTEND "noninteractive"
RUN apt-get update && apt-get upgrade -y

## install Globus GSI and simple CA
ENV IRODS_NEWUSER newuser
ENV GSI_NEWUSER_NAME "Test User"
ENV GSI_NEWUSER_PASS test

RUN wget http://toolkit.globus.org/ftppub/gt6/installers/repo/globus-toolkit-repo_latest_all.deb
ADD install_gsi.sh /tmp/install_gsi.sh
CMD /tmp/install_gsi.sh

WORKDIR /tmp
RUN wget ftp://ftp.renci.org/pub/irods/plugins/irods_auth_plugin_gsi/1.2/irods-auth-plugin-gsi-1.2-ubuntu14-x86_64.deb
RUN dpkg -i irods-auth-plugin-gsi-1.2-ubuntu14-x86_64.deb
