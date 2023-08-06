# -*- coding: utf-8 -*-
"""Module backup MongoDB dump and send to the server Amazon S3."""

import os
import shutil
import tarfile
import logging
import tempfile
import subprocess
import ConfigParser
from datetime import datetime
from exceptions import Exception
from boto.s3.connection import Location
from boto.s3.connection import S3Connection


class S3MongoBkp():

    def __init__(self, config_path):
        self.config_path = config_path

    def run_backup(self):
        self.backup_datetime = datetime.now().strftime('%F.%T')
        self.config = self._read_config(self.config_path)
        self.s3_conn = self._s3_connect_init()
        self._create_bucket()
        self._create_backups()
        self._upload_backups_to_s3()
        self._remove_tmp_file()
        self._remove_old_backups_from_s3()

    def _read_config(self, config_path):
        """Check s3mongobkp configuration file"""

        if not os.path.isfile(config_path):
            raise IOError("Config file {} does not exist".format(config_path))

        config = ConfigParser.RawConfigParser()
        config.read(config_path)
        return config

    def _s3_connect_init(self):
        return S3Connection(
            self.config.get('amazon', 'access_key'),
            self.config.get('amazon', 'secret_key')
        )

    def _create_bucket(self):
        try:
            self.s3_conn.create_bucket(self.config.get('amazon', 'bucket_name'),
                                       location=Location.USWest)
            logging.info("Bucket {} created".format(self.config.get('amazon', 'bucket_name')))
        except Exception, error_description:
            if error_description.status != 409:
                raise error_description

    def _create_backups(self):
        # Create tar archive
        tar = tarfile.open(os.path.join(self.config.get('backup', 'tmp_dir'),
                                        "{}.tar.gz".format(self.backup_datetime)), "w|gz")
        temp = tempfile.mkdtemp()
        command = 'mongodump --host {} -db {} -o {}'.format(self.config.get('mongo', 'hostname'),
                                                            self.config.get('mongo', 'database'),
                                                            temp)

        try:
            if self.config.get('mongo', 'username') and self.config.get('mongo', 'password'):
                command += ' -u {} -p {}'.format(self.config.get('mongo', 'username'),
                                                 self.config.get('mongo', 'password'))
        except ConfigParser.NoOptionError:
            logging.info('Not option username and password')

        result = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        _ = result.stdout.readlines().pop()
        tar.add(temp, arcname='backup')
        # Close tar archive
        tar.close()
        shutil.rmtree(temp)
        logging.info("Backup %s created" % self.backup_datetime)

    def _upload_backups_to_s3(self):
        bucket = self.s3_conn.get_bucket(self.config.get('amazon', 'bucket_name'))
        key = bucket.new_key("%s.tar.gz" % self.backup_datetime)
        key.set_contents_from_filename(os.path.join(self.config.get('backup', 'tmp_dir'),
                                                    "{}.tar.gz".format(self.backup_datetime)))
        key.set_acl('private')

    def _remove_tmp_file(self):
        os.unlink(os.path.join(self.config.get('backup', 'tmp_dir'),
                               "{}.tar.gz".format(self.backup_datetime)))

    def _remove_old_backups_from_s3(self):
        bucket = self.s3_conn.lookup(self.config.get('amazon', 'bucket_name'))
        for key in bucket:
            last_modified = datetime.strptime(key.last_modified, '%Y-%m-%dT%H:%M:%S.000Z')
            difference_time = datetime.now() - last_modified
            if difference_time.days > self.config.getint("backup", "max_lifetime_backup"):
                bucket.delete_key(key.name)
