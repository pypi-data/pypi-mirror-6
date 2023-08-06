#!/usr/bin/env python
# encoding: utf-8

from ec2stack import errors
from ec2stack.providers import cloudstack


def get_disk_offering(disk_name):
    """

    @param disk_name:
    @return:
    """
    args = {'name': disk_name, 'command': 'listDiskOfferings'}
    response = cloudstack.describe_item_request(
        args, 'diskoffering', errors.invalid_disk_offering_name
    )

    return response
