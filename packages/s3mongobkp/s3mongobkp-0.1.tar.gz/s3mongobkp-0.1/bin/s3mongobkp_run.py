#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script starts the process of creating a backup copy of the database
# and load it to the server Amazon S3, according to the settings in /etc/s3mongobkp.conf

from s3mongobkp import S3MongoBkp

CONFIG_FILE = "/etc/s3mongobkp.conf"

# Init S3MongoBkp class
s3bkp = S3MongoBkp(CONFIG_FILE)

# Run backup
s3bkp.run_backup()
