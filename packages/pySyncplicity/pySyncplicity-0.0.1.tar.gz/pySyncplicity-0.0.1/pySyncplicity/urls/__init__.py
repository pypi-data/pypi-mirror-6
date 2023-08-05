__author__ = 'mcowger'
import logging

logger = logging.getLogger(__name__)

logger.debug("Loading Service URLs")

XML_SYNCPLICITY_URL = "https://xml.syncplicity.com"
AUTH_TOKEN_URL = "https://xml.syncplicity.com/1.1/auth/tokens.svc"
AUTH_TOKEN_DETAILS_URL = "https://xml.syncplicity.com/1.1/auth/token.svc/%s"
SYNCPOINTS_LIST_URL = "https://xml.syncplicity.com/1.1/syncpoint/syncpoints.svc/?participants=true"
ADD_SYNCPOINT_URL = "https://xml.syncplicity.com/1.1/syncpoint/syncpoints.svc/"
DEL_SYNCPOINT_URL = "https://xml.syncplicity.com/1.1/syncpoint/syncpoint.svc/"
ADD_SHARING_PARTICIPANT_URL = "https://xml.syncplicity.com/1.1/syncpoint/syncpoint_participant.svc/%s/participant/%s"
ADD_SHARING_PARTICIPANT_BULK_URL = "https://xml.syncplicity.com/1.1/syncpoint/participants.svc/"
DEL_SHARING_PARTICIPANT_URL = "https://xml.syncplicity.com/1.1/syncpoint/syncpoint_participant.svc/%s/participant/%s"
FOLDER_CONTENT_URL = "https://xml.syncplicity.com/1.1/sync/folder.svc/%s/folder/%s?include=%s"
FILE_VERSION_LIST_URL = "https://xml.syncplicity.com/1.1/sync/versions.svc/%s/file/%s/versions"

REGISTER_MACHINE_URL = "https://xml.syncplicity.com/1.1/auth/machines.svc/"
CREATE_SHAREABLE_LINK_URL = "https://xml.syncplicity.com/1.1/syncpoint/links.svc/"
DEL_SHAREABLE_LINK_URL = "https://xml.syncplicity.com/1.1/syncpoint/link.svc/%s"



DOWNLOAD_FILE_URL = "https://data.syncplicity.com/retrieveFile.php?sessionKey=%s&vToken=%s-%s"
UPLOAD_FILE_URL = "https://data.syncplicity.com/saveFile.php?filepath=%s"
CHECK_FILES_ARE_UPLOADED_URL = "https://xml.syncplicity.com/1.1/sync/global_files.svc/"
SUBMIT_FOLDER_INFORMATION_URL = "https://xml.syncplicity.com/1.1/sync/folders.svc/%s/folders"
SUBMIT_FILE_INFORMATION_URL = "https://xml.syncplicity.com/1.1/sync/files.svc/%s/files"
GET_QUOTA_INFORMATION_URL = "https://xml.syncplicity.com/1.1/sync/quota.svc/"