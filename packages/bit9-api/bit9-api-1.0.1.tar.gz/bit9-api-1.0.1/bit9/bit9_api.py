#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__version__ = '1.0.1'
__license__ = 'GPLv3'

import re

import requests


class Bit9Api():
    """
    The Bit9 Cyber Forensics Service can be used to access information in the Bit9 Global Software
    Registry (GSR) to help identify, validate, and assign reputation to unknown software. The GSR
    provides identification, authentication, and metadata for over 5 billion file records. It pulls
    data from a combination of distribution partners, web crawlers, honeypots, and Bit9's own
    organic community, adding software files and metadata to the database. Software in the GSR is
    also screened by multiple anti-malware tools and cross-referenced against third- party
    vulnerability databases.

    The Cyber Forensics Service is commonly used to find more information about files for which you
    have hash values (MD5, SHA1 or SHA256). This information includes identifying malware and
    filtering known good software to accelerate investigations and isolate advanced threats and
    suspect files.

    This document describes the Web Services Interface for the Cyber Forensics Service, including
    the query methods you can use to look up information about files and the data the service
    returns. The information returned in lookup results can be custom-tuned for your purposes.
    """

    def __init__(self, user=None, password=None, data_format='json', proxies=None):
        self.baseurl = "https://services.bit9.com/CyberForensicsService/"
        self.user = user
        self.password = password
        self.flag = {'THREAT_TRUST': 1,
                     'FILE_INFO': 2,
                     'PE_HEADER_METADATA': 4,
                     'CERTIFICATE': 8,
                     'BASE_ALL': 15,
                     'CERTIFICATE_EX': 128,
                     'CATEGORY': 256}
        self.data_format = data_format
        self.proxies = proxies
        self.version = '1'
        self.tool = "pythonapi"
        if user is None or password is None:
            raise BadCreds("You must supply a valid user name and password")
        if data_format != 'json' and data_format != 'xml':
            raise BadDataFormat(" Data format must be 'json' or 'xml' ")

    @property
    def lookup_usageinfos(self):
        """ CFS Usage Information: Queries with the Usageinfos Object

        A query using the usageinfos object type provides you with information about your usage of
        the Cyber Forensics API. If you have defined “data” and “tool” arguments, you can use them
        in a usageinfos query to track how many CFS queries each of your customers has made and what
        tools they have used to make the queries. Usageinfos queries return only information for API
        calls made using your Cyber Forensics Service username and password.

        Note: The query counts for usageinfo are updated periodically, not in real time. Bit9
        recommends that usageinfo queries have an end date (the todateutc argument) no later than
        one day prior to the current date.

        :return: Usage results
        """
        url = self.baseurl + self.version + "/usageinfos/lookup." + self.data_format
        values = dict(username=self.user, password=self.password, tool=self.tool)

        try:
            response = requests.post(url, values, proxies=self.proxies)
        except requests.RequestException as e:
            return dict(error=e)

        if response.status_code == requests.codes.ok:
            if self.data_format == 'json':
                return response.json()
            else:
                return response.content
        else:
            return dict(response_code=response.status_code)

    def lookup_hashinfo(self, hash_list, flag=15):
        """ Single and Batch Hash Queries: Hashinfo and Hashinfos Objects

        :param hash_list: a single or list of hashes (md5, sha1 or sha256)
        :param flag: The amount of detail you want in the response.
        :return: Query results in the format specified (json or xml)
        """
        hash_type, hash_list = vaildate_input(hash_list)
        if hash_list:
            if isinstance(hash_list, basestring):
                url = self.baseurl + self.version + "/hashinfo/lookup." + self.data_format
            else:
                if len(hash_list) > 1000:
                    return dict(error='Malformed Input - Can only query 1000 hashes at a time.',
                                response_code=400)
                else:
                    url = self.baseurl + self.version + "/hashinfos/lookup." + self.data_format
            values = dict(username=self.user, password=self.password, flags=flag, tool=self.tool,
                          proxies=self.proxies)
            values[hash_type] = hash_list
            try:
                response = requests.post(url, values, proxies=self.proxies)
            except requests.RequestException as e:
                return dict(error=e)

            if response.status_code == requests.codes.ok:
                if self.data_format == 'json':
                    return response.json()
                else:
                    return response.content
            elif response.status_code == 404:
                return dict(error='Not Found.', response_code=response.status_code)
            elif response.status_code == 401:
                return dict(error='Unauthorized - bad creds or requested more information than licensed to receive.',
                            response_code=response.status_code)
            else:
                return dict(response_code=response.status_code)
        else:
            if hash_type == 'none':
                return dict(error='Malformed Input - needs to be a md5, sha1 or sha256 hash.', response_code=400)
            if hash_type == 'mixed':
                return dict(response_code=400,
                            error='Malformed Input - needs to be all the same type of md5/sha1/sha256 hash.')

    def __lookup_extended(self, this_hash, lookup_type):
        """ Perform a single hash query using the Extended View API Functionality

        :param this_hash: Single hash (md5, sha1 or sha256)
        :param lookup_type: Extended View API endpoint type
        :return: Query results in the format specified (json or xml)
        """
        hash_type, this_hash = vaildate_input(this_hash)
        if isinstance(this_hash, basestring):
            url = self.baseurl + self.version + lookup_type + "/lookup." + self.data_format
            values = dict(username=self.user, password=self.password, tool=self.tool)
            values[hash_type] = this_hash
            try:
                response = requests.post(url, values, proxies=self.proxies)
            except requests.RequestException as e:
                return dict(error=e)

            if response.status_code == requests.codes.ok:
                if self.data_format == 'json':
                    return response.json()
                else:
                    return response.content
            elif response.status_code == 404:
                return dict(error='Not Found.', response_code=response.status_code)
            elif response.status_code == 401:
                return dict(error='Unauthorized - bad creds or requested more information than licensed to receive.',
                            response_code=response.status_code)
            else:
                return dict(response_code=response.status_code)
        else:
            return dict(error='Malformed Input - needs to be a single md5/sha1/sha256 hash.', response_code=400)

    def lookup_certificates(self, this_hash):
        """ Lookups Using the Certificates Object Type.

        A query using the certificates object type provides certificate information for the
        specified hash.

        Note: This API for this object type is available only to users licensed for the Extended View.

        :param this_hash: Single hash (md5, sha1 or sha256)
        :return: Query results in the format specified (json or xml)
        """
        return self.__lookup_extended(this_hash, "/certificates")

    def lookup_files(self, this_hash):
        """ Lookups Using the Files Object Type.

        A query using the files object type provides file information such as the file type, the
        file parent and the file package for the specified hash.

        Note: This API for this object type is available only to users licensed for the Extended View.

        :param this_hash: Single hash (md5, sha1 or sha256)
        :return: Query results in the format specified (json or xml)
        """
        return self.__lookup_extended(this_hash, "/files")

    def lookup_packages(self, this_hash):
        """ Lookups Using the Packages Object Type.

        A query using the packages object type provides package information for the specified hash,
        including the operating system, company and source, number of files in the package, and
        packages title.

        Note: This API for this object type is available only to users licensed for the Extended View.

        :param this_hash: Single hash (md5, sha1 or sha256)
        :return: Query results in the format specified (json or xml)
        """
        return self.__lookup_extended(this_hash, "/packages")

    def lookup_scanresults(self, this_hash):
        """ Lookups Using the Scanresults Object Type.

        A query using the scanresults object type provides the results of AV scans, if any,
        performed on the file represented by the specified hash.

        Note: This API for this object type is available only to users licensed for the Extended View.

        :param this_hash: Single hash (md5, sha1 or sha256)
        :return: Query results in the format specified (json or xml)
        """
        return self.__lookup_extended(this_hash, "/scanresults")


class ApiError(Exception):
    pass


class BadCreds(ApiError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BadDataFormat(ApiError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def vaildate_input(user_input):
    """ Validate File Hash Input.

    :param user_input: Input string or list
    :return:[str,<str,list>] Hash Type, Hash list or single hash string
    """
    #: Check that input is a string
    if not isinstance(user_input, basestring):
        #: If not, make it a string
        user_input = __list_to_string(user_input)
    #: Check that it is at least as long as a md5 hash
    if len(user_input) >= 32:
        found_md5s = __extract_md5_from_hash_list(user_input)
        found_sha1s = __extract_sha1_from_hash_list(user_input)
        found_sha256 = __extract_sha256_from_hash_list(user_input)
        #: Check that hash list is not empty or mixed
        if found_md5s and not found_sha1s and not found_sha256:
            return 'md5', found_md5s
        elif found_sha1s and not found_md5s and not found_sha256:
            return 'sha1', found_sha1s
        elif found_sha256 and not found_sha1s and not found_md5s:
            return 'sha256', found_sha256
        elif not found_md5s and not found_sha1s and not found_sha256:
            return 'none', False
        else:
            return 'mixed', False
    return 'none', False


def __extract_md5_from_hash_list(data):
    """ Extract all md5 hashes from a string.

    :param data: Input string
    :return: List of md5 hashes or single md5 hash
    """
    found_md5_hashes = re.findall(r'(?i)(?<![a-zA-Z0-9])[a-fA-F0-9]{32}(?![a-zA-Z0-9])', data)
    hash_list = list(set(found_md5_hashes))
    if len(hash_list) == 1:
        return hash_list[0]
    else:
        return hash_list


def __extract_sha1_from_hash_list(data):
    """ Extract all sha1 hashes from a string.

    :param data: Input string
    :return: List of sha1 hashes or single sha1 hash
    """
    found_sha1_hashes = re.findall(r'(?i)(?<![a-zA-Z0-9])[a-fA-F0-9]{40}(?![a-zA-Z0-9])', data)
    hash_list = list(set(found_sha1_hashes))
    if len(hash_list) == 1:
        return hash_list[0]
    else:
        return hash_list


def __extract_sha256_from_hash_list(data):
    """ Extract all sha256 hashes from a string.

    :param data: Input string
    :return: List of sha256 hashes or single sha256 hash
    """
    found_sha256_hashes = re.findall(r'(?i)(?<![a-zA-Z0-9])[a-fA-F0-9]{64}(?![a-zA-Z0-9])', data)
    hash_list = list(set(found_sha256_hashes))
    if len(hash_list) == 1:
        return hash_list[0]
    else:
        return hash_list


def __list_to_string(this_list):
    """ Convert list to string.

    :param this_list: Hash list
    :return: List converted to string
    """
    return ','.join(map(str, this_list))
