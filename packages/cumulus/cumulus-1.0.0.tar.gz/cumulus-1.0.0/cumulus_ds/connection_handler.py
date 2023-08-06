""" Connection handler """
import boto
import logging
from boto import cloudformation

import cumulus_ds

logger = logging.getLogger(__name__)


def connect_s3():
    """ Connect to AWS S3

    :returns: boto.s3.connection
    """
    try:
        return boto.connect_s3(
            aws_access_key_id=cumulus_ds.config.get_environment_option(
                'access-key-id'),
            aws_secret_access_key=cumulus_ds.config.get_environment_option(
                'secret-access-key'))
    except Exception as err:
        logger.error('A problem occurred connecting to AWS S3: {}'.format(err))
        raise


def connect_cloudformation():
    """ Connect to AWS CloudFormation

    :returns: boto.cloudformation.connection
    """
    try:
        return cloudformation.connect_to_region(
            cumulus_ds.config.get_environment_option('region'),
            aws_access_key_id=cumulus_ds.config.get_environment_option(
                'access-key-id'),
            aws_secret_access_key=cumulus_ds.config.get_environment_option(
                'secret-access-key'))
    except Exception as err:
        logger.error(
            'A problem occurred connecting to AWS CloudFormation: {}'.format(
                err))
        raise
