__author__ = 'mcowger'


import logging

logger = logging.getLogger(__name__)

import urls
from requests import Session
import datetime
from pprint import pformat, pprint
import hashlib
from requests_toolbelt import MultipartEncoder


class SyncplicityException(Exception):
    def __init__(self, message, Errors):
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)

        # Now for your custom code...
        self.Errors = Errors

class SyncplicitySyncPoint(object):
    def __init__(self,syncpoint_dict):
            for key in syncpoint_dict:
                setattr(self,key,syncpoint_dict[key])
            logger.debug("Syncpoint Created: %s" % self.__dict__)

    def __str__(self):
        return str(type(self)) + str(self.__dict__)

    def __repr__(self):
        return str(self)


class SyncplicityFolder(object):
    """
    Defines a syncplicity Folder
    """


    def __init__(self, id, status, virtual_path=None, name=None):
        """
        :param id: ID of the folder
        :param status: Folder status
        :param virtual_path: virtual folder path
        """
        self.id = id
        self.status = status
        self.name = name
        self.virtual_path = virtual_path
        self.files = []
        self.folders = []

    def __str__(self):
        return str(type(self)) + str(self.__dict__)

    def __repr__(self):
        return str(self)


class SyncplicityFile(object):

    def __init__(self, filename="", syncpoint_id="", folder_id=0,length=0, latest_version_id=0, last_write_time_utc=None, id=0, status=0):
        """
        :rtype : SyncplicityFile
        :param filename: filename of the object
        :param syncpoint_id: id for the parent syncpoint
        :param length: size of the file (byetes)
        :param latest_version_id: last version
        :param last_write_time_utc: last time the file was changed
        :param id: file id
        :param status: status
        
        """
        self.id = id
        self.status = status
        self.filename = filename
        self.syncpoint_id = syncpoint_id
        self.length = length
        self.latest_version_id = latest_version_id
        self.last_write_time = datetime.datetime.strptime(last_write_time_utc, '%Y-%m-%dT%H:%M:%S.%f0Z')
        self.files = []


    def __str__(self):
        return str(type(self)) + str(self.__dict__)

    def __repr__(self):
        return str(self)

class SyncplicityConn(object):
    """
    Defines a syncplicity connections
    """

    def __init__(self):
        self.id = None
        self.duration = None
        self.first_name = None
        self.last_name = None
        self.account_type = None
        self.company_id = None
        self.company_name = None
        self.starttime = datetime.datetime.now()

    @property
    def is_valid(self):

        """
        Checks if the connection is still valid

        :return: True if the connection is still valud
        """
        if self.starttime + self.duration > datetime.datetime.now():
            return true
        return false

    def __str__(self):
        return str(type(self)) + str(self.__dict__)

    def __repr__(self):
        return str(self)



class SyncplicityClient(object):
    def __init__(self, username="", password="", proxy=None, verify=False):
        """
        creates a syncplicity object

        :param username: login username for the service
        :param password: password for the service
        :param proxy: proxy host to use, if any required for https.  Format: http://10.10.1.10:1080
        :param verify: enable/disable SSL verification
        :return: a syncplicity client object
        """
        self.username = username
        self.password = password


        if proxy:
            self.proxy = {'https':proxy,'http':proxy}
        else:
            self.proxy = None

        self.verify = verify

        self.headers = {"accept": 'application/json'}
        logger.debug("Initialized client with username: %s" % self.username)

    def connect(self,reconnect=True):
        """
        connects to the syncplicity service

        :param reconnect: should the client automatically attempt to reconnect if needed.
        :return: None
        """
        self.syncplicity = Session()
        self.syncplicity.verify = self.verify
        self.syncplicity.proxies = self.proxy
        self.syncplicity.headers = self.headers
        self.reconnect = reconnect

        #Get the initial token
        authdata = self.syncplicity.get(url=urls.AUTH_TOKEN_URL,auth=(self.username,self.password)).json()[0]
        self.connection = SyncplicityConn()
        self.connection.id = authdata['Id']
        self.connection.duration = datetime.timedelta(seconds=int(authdata['Duration']))
        self.connection.last_name = authdata['User']['LastName']
        self.connection.last_name = authdata['User']['FirstName']
        self.connection.last_name = authdata['User']['LastName']
        self.connection.company_id = authdata['User']['Company']['Id']
        self.connection.account_type = authdata['User']['Company']['AccountType']
        self.connection.company_name = authdata['User']['Company']['Name']
        self.syncplicity.headers.update({'Authorization': "Token %s" % self.connection.id})

        logger.info("Got connection data: %s" % pformat(self.connection))

    def list_sync_points(self):
        """

        Gets a list of all syncronization points (folders) available to the user

        :return: List of SyncplicitySyncPoint
        """

        syncpoints = []
        for syncpoint in self.syncplicity.get(urls.SYNCPOINTS_LIST_URL).json():
            syncpoints.append(SyncplicitySyncPoint(syncpoint))

        logger.info("Got syncpoints %s" % syncpoints)
        return syncpoints



    def download_file(self, file, debug=False):

        """
        Downloads a file from the syncplicity service.

        :param file: SyncplicityFile object to retrieve
        :param debug: debug mode won't actuallt download the file, just show you the URL it would try.
        :return: a `Response object <http://docs.python-requests.org/en/latest/api/#requests.Response>`_
        """
        download_url = urls.DOWNLOAD_FILE_URL % (self.connection.id,file.syncpoint_id, file.latest_version_id)
        logger.debug("Attempting to download file %s from %s" % (file.filename,download_url))
        if debug:
            return
        response = self.syncplicity.get(download_url)
        logger.debug(response.headers)
        return response

    def upload_file(self, filename, folder_id, debug=False):

        """


        :param filename: filename to upload.
        :param folder_id: virtual folder id to put this file in.
        :param debug: debug mode won't actuallt download the file, just show you the URL it would try.
        :return: a ``Response object http://docs.python-requests.org/en/latest/api/#requests.Response``
        """

        file_path = "\\" + filename
        creationTimeUtc = ""
        lastWriteTimeUtc = ""
        sessionKey = self.connection.id


        file_data = open(filename,'r').read()
        sha256 = hashlib.sha256(file_data).hexdigest()
        size = len(file_data)
        logger.debug("Attempting to upload file %s with size %s and sha256 of %s" % (filename,size,sha256))

        upload_url = urls.UPLOAD_FILE_URL % file_path
        post_headers = self.headers.copy()
        #post_headers.update({'Content-Length':size})


        thedictionary = {
            'creationTimeUtc': creationTimeUtc,
            'lastWriteTimeUtc': lastWriteTimeUtc,
            'filepath':file_path,
            'sessionKey': self.connection.id,
            'sha256':sha256,
            'virtualFolderId': str(folder_id),
            'sessionKey': str(self.connection.id),
            'fileData':(filename,open(filename,'rb'),'application/octet-stream')
        }
        m = MultipartEncoder(thedictionary)

        post_headers.update({'Content-Type':m.content_type})
        if debug:
            pass
        response = self.syncplicity.post(
            url=upload_url,
            headers=post_headers,
            #files=thedictionary,
            data=m

        )
        return response


    
    def get_folder(self, syncpoint_id, folder_id, type="active"):
        """

        :param syncpoint_id: The base syncpoint id
        :param folder_id: the specific folder ID
        :param type: [active|deleted] files to show
        :return: a syncplicity folder
        :rtype:
        """
        contents = self.syncplicity.get(urls.FOLDER_CONTENT_URL % (syncpoint_id, folder_id, type)).json()
        thisfolder = SyncplicityFolder(id=contents['FolderId'],virtual_path=contents['VirtualPath'],status=contents['Status'])
        for file in contents['Files']:
            thisfolder.files.append( SyncplicityFile(id=file['FileId'],
                                                     filename=file['Filename'],
                                                     folder_id=file['FolderId'],
                                                     last_write_time_utc=file['LastWriteTimeUtc'],
                                                     latest_version_id=file['LatestVersionId'],
                                                     length=file['Length'],
                                                     status=file['Status'],
                                                     syncpoint_id=file['SyncpointId']
                                                    )

                                    )
        for folder in contents['Folders']:
            #pprint(folder)
            thisfolder.folders.append( SyncplicityFolder(id=folder['FolderId'],
                                                         status=folder['Status'],
                                                         name=folder['Name']
                                                        )
                                    )
        return thisfolder





def main():
    pass


if __name__ == "__main__":
    main()
