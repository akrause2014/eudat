#!/bin/bash
yes $IRODS_PASS | sudo dpkg -i globus-toolkit-repo_latest_all.deb
sudo apt-get update
sudo apt-get -f install globus-gsi
sudo apt-get install globus-simple-ca

echo -e "$GSI_NEWUSER_NAME\n$GSI_NEWUSER_PASS\n" grid-cert-request
grid-ca-sign -in /IRODS_USER/.globus/usercert_request.pem -out /IRODS_USER/.globus/usercert.pem