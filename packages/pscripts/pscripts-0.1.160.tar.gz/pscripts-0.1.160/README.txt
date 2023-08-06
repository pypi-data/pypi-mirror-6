* External IP Address Updater

** Overview

Configuration files will be created at:

    /etc/external_ip_updater
    |-- config.conf
    `-- urls.yaml

Put your domain and DDNS (Dynamic DNS) update urls in 'urls.yaml'.
You can also set the refresh period to check for external ip address
changes.  If there is a change, a call is made to the DDNS update url
provided. 

** Logging

Log file is specified in:

    /etc/external_ip_updater/config.conf

You can adjust the log levels between 'debug','info', and 'warn.
Typically when all is running well, just leave it at 'info' only.

** Start/Stop test

    % sudo update_external_ip --start
    % sudo update_external_ip --stop

** Systemd

    % sudo systemctl enable update_external_ip.service
    % sudo systemctl start update_external_ip.service
