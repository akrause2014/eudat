#!/bin/bash

cd /tmp

echo "Installing GSI authentication plugin"
wget ftp://ftp.renci.org/pub/irods/plugins/irods_auth_plugin_gsi/1.2/irods-auth-plugin-gsi-1.2-ubuntu14-x86_64.deb
yes $IRODS_PASS | sudo -S dpkg -i irods-auth-plugin-gsi-1.2-ubuntu14-x86_64.deb

echo "Adding new user 'newuser' to iRODS"
iadmin mkuser newuser rodsuser
iadmin aua newuser '/O=Grid/OU=GlobusTest/OU=simpleCA-62744a2b1a07/OU=Globus Simple CA/CN=-e'

echo 'Use "irods_authentication_scheme": "gsi" in iRODS environment when logging in'
