import logging
import re
import dateutil.parser
import random
import json
import time
import httplib
import ssl

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError

from time import mktime, time
from datetime import datetime
from httplib2 import Http
from collections import OrderedDict
from os.path import isdir, isfile
from os import makedirs, stat, utime
from dateutil.tz import tzlocal, tzutc

import gdrivefs.gdtool.chunked_download

from gdrivefs.errors import AuthorizationFaultError, MustIgnoreFileError, \
                            FilenameQuantityError, ExportFormatError
from gdrivefs.conf import Conf
from gdrivefs.gdtool.oauth_authorize import get_auth
from gdrivefs.gdtool.normal_entry import NormalEntry
from gdrivefs.time_support import get_flat_normal_fs_time_from_dt
from gdrivefs.gdfs.fsutility import split_path_nolookups, \
                                    escape_filename_for_query

_CONF_SERVICE_NAME = 'drive'
_CONF_SERVICE_VERSION = 'v2'


class GdriveAuth(object):
    def __init__(self):
        self.__log = logging.getLogger().getChild('GdAuth')
        self.__client = None
        self.__authorize = get_auth()
        self.__check_authorization()

    def __check_authorization(self):
        self.__credentials = self.__authorize.get_credentials()

    def get_authed_http(self):
        self.__check_authorization()
        self.__log.info("Getting authorized HTTP tunnel.")
            
        http = Http()
        self.__credentials.authorize(http)

        return http

    def get_client(self):
        if self.__client is None:
            authed_http = self.get_authed_http()

            self.__log.info("Building authorized client from Http.  TYPE= [%s]" % 
                            (type(authed_http)))
        
            # Build a client from the passed discovery document path
            
            discoveryUrl = Conf.get('google_discovery_service_url')
# TODO: We should cache this, since we have, so often, having a problem 
#       retrieving it. If there's no other way, grab it directly, and then pass
#       via a file:// URI.
        
            try:
                client = build(_CONF_SERVICE_NAME, 
                               _CONF_SERVICE_VERSION, 
                               http=authed_http, 
                               discoveryServiceUrl=discoveryUrl)
            except HttpError as e:
                # We've seen situations where the discovery URL's server is down,
                # with an alternate one to be used.
                #
                # An error here shouldn't leave GDFS in an unstable state (the 
                # current command should just fail). Hoepfully, the failure is 
                # momentary, and the next command succeeds.

                logging.exception("There was an HTTP response-code of (%d) while "
                                  "building the client with discovery URL [%s]." % 
                                  (e.resp.status, discoveryUrl))
                raise

            self.__client = client

        return self.__client


class _GdriveManager(object):
    """Handles all basic communication with Google Drive. All methods should
    try to invoke only one call, or make sure they handle authentication 
    refreshing when necessary.
    """

    def __init__(self):
        self.__log = logging.getLogger().getChild('GdManager')
        self.__auth = GdriveAuth()

    def get_about_info(self):
        """Return the 'about' information for the drive."""

        client = self.__auth.get_client()
        response = client.about().get().execute()
        
        return response

    def list_changes(self, start_change_id=None, page_token=None):
        """Get a list of the most recent changes from GD, with the earliest 
        changes first. This only returns one page at a time. start_change_id 
        doesn't have to be valid.. It's just the lower limit to what you want 
        back. Change-IDs are integers, but are not necessarily sequential.
        """

        self.__log.info("Listing changes starting at ID [%s] with page_token "
                        "[%s]." % (start_change_id, page_token))

        client = self.__auth.get_client()

# TODO: We expected that this reports all changes to all files. If this is the 
#       case, than what's the point of the watch() call in Files?
        response = client.changes().list(pageToken=page_token, \
                        startChangeId=start_change_id).execute()

        items             = response[u'items']
        largest_change_id = int(response[u'largestChangeId'])
        next_page_token   = response[u'nextPageToken'] if u'nextPageToken' \
                                                       in response else None

        changes = OrderedDict()
        last_change_id = None
        for item in items:
            change_id   = int(item[u'id'])
            entry_id    = item[u'fileId']
            was_deleted = item[u'deleted']
            entry       = None if item[u'deleted'] else item[u'file']

            if last_change_id and change_id <= last_change_id:
                message = "Change-ID (%d) being processed is less-than the " \
                          "last change-ID (%d) to be processed." % \
                          (change_id, last_change_id)

                self.__log.error(message)
                raise Exception(message)

            try:
                normalized_entry = None if was_deleted \
                                        else NormalEntry('list_changes', entry)
            except:
                self.__log.exception("Could not normalize entry embedded in "
                                     "change with ID (%d)." % (change_id))
                raise

            changes[change_id] = (entry_id, was_deleted, normalized_entry)
            last_change_id = change_id

        return (largest_change_id, next_page_token, changes)

    def get_parents_containing_id(self, child_id, max_results=None):
        
        self.__log.info("Getting client for parent-listing.")

        client = self.__auth.get_client()

        self.__log.info("Listing entries over child with ID [%s]." %
                        (child_id))

        response = client.parents().list(fileId=child_id).execute()

        return [ entry[u'id'] for entry in response[u'items'] ]

    def get_children_under_parent_id(self, \
                                     parent_id, \
                                     query_contains_string=None, \
                                     query_is_string=None, \
                                     max_results=None):

        self.__log.info("Getting client for child-listing.")

        client = self.__auth.get_client()

        if query_contains_string and query_is_string:
            self.__log.exception("The query_contains_string and query_is_string "
                              "parameters are mutually exclusive.")
            raise

        if query_is_string:
            query = ("title='%s'" % 
                     (escape_filename_for_query(query_is_string)))
        elif query_contains_string:
            query = ("title contains '%s'" % 
                     (escape_filename_for_query(query_contains_string)))
        else:
            query = None

        self.__log.info("Listing entries under parent with ID [%s].  QUERY= "
                     "[%s]" % (parent_id, query))

        response = client.children().list(q=query, folderId=parent_id, \
                                          maxResults=max_results). \
                                          execute()

        return [ entry[u'id'] for entry in response[u'items'] ]

    def get_entries(self, entry_ids):

        retrieved = { }
        for entry_id in entry_ids:
            try:
                entry = drive_proxy('get_entry', entry_id=entry_id)
            except:
                self.__log.exception("Could not retrieve entry with ID [%s]." % 
                                     (entry_id))
                raise

            retrieved[entry_id] = entry

        self.__log.debug("(%d) entries were retrieved." % (len(retrieved)))

        return retrieved

    def get_entry(self, entry_id):
        client = self.__auth.get_client()

        try:
            entry_raw = client.files().get(fileId=entry_id).execute()
        except:
            self.__log.exception("Could not get the file with ID [%s]." % 
                                 (entry_id))
            raise

        try:
            entry = NormalEntry('direct_read', entry_raw)
        except:
            self.__log.exception("Could not normalize raw-data for entry with "
                                 "ID [%s]." % (entry_id))
            raise

        return entry

    def list_files(self, query_contains_string=None, query_is_string=None, 
                   parent_id=None):
        
        self.__log.info("Listing all files. CONTAINS=[%s] IS=[%s] "
                        "PARENT_ID=[%s]" % 
                        (query_contains_string 
                            if query_contains_string is not None 
                            else '<none>', 
                         query_is_string 
                            if query_is_string is not None 
                            else '<none>', 
                         parent_id if parent_id is not None 
                                   else '<none>'))

        client = self.__auth.get_client()

        query_components = []

        if parent_id:
            query_components.append("'%s' in parents" % (parent_id))

        if query_is_string:
            query_components.append("title='%s'" % 
                                    (escape_filename_for_query(query_is_string)))
        elif query_contains_string:
            query_components.append("title contains '%s'" % 
                                    (escape_filename_for_query(query_contains_string)))

        # Make sure that we don't get any entries that we would have to ignore.

        hidden_flags = Conf.get('hidden_flags_list_remote')
        if hidden_flags:
            for hidden_flag in hidden_flags:
                query_components.append("%s = false" % (hidden_flag))

        query = ' and '.join(query_components) if query_components else None

        page_token = None
        page_num = 0
        entries = []
        while 1:
            self.__log.debug("Doing request for listing of files with page-"
                             "token [%s] and page-number (%d): %s" % 
                             (page_token, page_num, query))

            result = client.files().list(q=query, pageToken=page_token).\
                        execute()

            self.__log.debug("(%d) entries were presented for page-number "
                             "(%d)." % 
                             (len(result[u'items']), page_num))

            for entry_raw in result[u'items']:
                try:
                    entry = NormalEntry('list_files', entry_raw)
                except:
                    self.__log.exception("Could not normalize raw-data for "
                                         "entry with ID [%s]." % 
                                         (entry_raw[u'id']))
                    raise

                entries.append(entry)

            if u'nextPageToken' not in result:
                self.__log.debug("No more pages in file listing.")
                break

            self.__log.debug("Next page-token in file-listing is [%s]." % (result[u'nextPageToken']))
            page_token = result[u'nextPageToken']
            page_num += 1

        return entries

    def download_to_local(self, output_file_path, normalized_entry, mime_type, 
                          allow_cache=True):
        """Download the given file. If we've cached a previous download and the 
        mtime hasn't changed, re-use. The third item returned reflects whether 
        the data has changed since any prior attempts.
        """

        self.__log.debug("Downloading entry with ID [%s] and mime-type [%s].", 
                         normalized_entry.id, mime_type)

        if mime_type != normalized_entry.mime_type and \
                mime_type not in normalized_entry.download_links:
            message = ("Entry with ID [%s] can not be exported to type [%s]. "
                       "The available types are: %s" % 
                       (normalized_entry.id, mime_type, 
                        ', '.join(normalized_entry.download_links.keys())))

            self.__log.warning(message)
            raise ExportFormatError(message)

        temp_path = Conf.get('file_download_temp_path')

        if not isdir(temp_path):
            try:
                makedirs(temp_path)
            except:
                self.__log.exception("Could not create temporary download "
                                     "path [%s]." % (temp_path))
                raise

        gd_mtime_epoch = mktime(normalized_entry.modified_date.timetuple())

        self.__log.debug("File will be downloaded to [%s].", 
                         (output_file_path))

        use_cache = False
        if allow_cache and isfile(output_file_path):
            # Determine if a local copy already exists that we can use.
            try:
                stat_info = stat(output_file_path)
            except:
                self.__log.exception("Could not retrieve stat() information "
                                     "for temp download file [%s]." % 
                                     (output_file_path))
                raise

            if gd_mtime_epoch == stat_info.st_mtime:
                use_cache = True

        if use_cache:
            # Use the cache. It's fine.

            self.__log.debug("File retrieved from the previously downloaded, "
                            "still-current file.")
            return (stat_info.st_size, False)

        # Go and get the file.

# TODO(dustin): This might establish a new connection. Not cool.
        authed_http = self.__auth.get_authed_http()

        url = normalized_entry.download_links[mime_type]

#        self.__log.debug("Downloading file from [%s]." % (url))
#
#        try:
#            data_tuple = authed_http.request(url)
#        except:
#            self.__log.exception("Could not download entry with ID [%s], type "
#                              "[%s], and URL [%s]." % (normalized_entry.id, 
#                                                       mime_type, url))
#            raise
#
#        (response_headers, data) = data_tuple
#
#        # Throw a log-item if we see any "Range" response-headers. If GD ever
#        # starts supporting "Range" headers, we'll be able to write smarter 
#        # download mechanics (resume, etc..).
#
#        r = re.compile('Range')
#        range_found = [("%s: %s" % (k, v)) for k, v 
#                                           in response_headers.iteritems() 
#                                           if r.match(k)]
#        if range_found:
#            self.__log.info("GD has returned Range-related headers: %s" % 
#                            (", ".join(found)))
#
#        self.__log.info("Downloaded file is (%d) bytes. Writing to [%s]." % 
#                        (len(data), output_file_path))
#
#        try:
#            with open(output_file_path, 'wb') as f:
#                f.write(data)
#        except:
#            self.__log.exception("Could not cached downloaded file. Skipped.")
#
#        else:
#            self.__log.info("File written to cache successfully.")

        with open(output_file_path, 'wb') as f:
            downloader = gdrivefs.gdtool.chunked_download.ChunkedDownload(
                            f, 
                            authed_http, 
                            url)

            while 1:
                status, done, total_size = downloader.next_chunk()
                if done is True:
                    break

        try:
            utime(output_file_path, (time(), gd_mtime_epoch))
        except:
            self.__log.exception("Could not set time on [%s]." % 
                                 (output_file_path))
            raise

        return (total_size, True)

    def __insert_entry(self, filename, mime_type, parents, data_filepath=None, 
                       modified_datetime=None, accessed_datetime=None, 
                       is_hidden=False, description=None):

        if parents is None:
            parents = []

        now_phrase = get_flat_normal_fs_time_from_dt()

        if modified_datetime is None:
            modified_datetime = now_phrase 
    
        if accessed_datetime is None:
            accessed_datetime = now_phrase 

        self.__log.info("Creating file with filename [%s] under parent(s) "
                        "[%s] with mime-type [%s], mtime= [%s], atime= [%s]." % 
                        (filename, ', '.join(parents), mime_type, 
                         modified_datetime, accessed_datetime))

        client = self.__auth.get_client()

        body = { 
                'title': filename, 
                'parents': [dict(id=parent) for parent in parents], 
                'mimeType': mime_type, 
                'labels': { "hidden": is_hidden }, 
                'description': description 
            }

        if modified_datetime is not None:
            body['modifiedDate'] = modified_datetime

        if accessed_datetime is not None:
            body['lastViewedByMeDate'] = accessed_datetime

        args = { 'body': body }

        if data_filepath:
            args['media_body'] = MediaFileUpload(filename=data_filepath, \
                                                 mimetype=mime_type)

        self.__log.debug("Doing file-insert with:\n%s" % (args))

        try:
            result = client.files().insert(**args).execute()
        except:
            self.__log.exception("Could not insert file [%s]." % (filename))
            raise

        normalized_entry = NormalEntry('insert_entry', result)
            
        self.__log.info("New entry created with ID [%s]." % 
                        (normalized_entry.id))

        return normalized_entry

    def truncate(self, normalized_entry):

        self.__log.info("Truncating entry [%s]." % (normalized_entry.id))

        try:
            entry = self.update_entry(normalized_entry, data_filepath='/dev/null')
        except:
            self.__log.exception("Could not truncate entry with ID [%s]." % 
                                 (normalized_entry.id))
            raise

    def update_entry(self, normalized_entry, filename=None, data_filepath=None, 
                     mime_type=None, parents=None, modified_datetime=None, 
                     accessed_datetime=None, is_hidden=False, 
                     description=None):

        if not mime_type:
            mime_type = normalized_entry.mime_type

        self.__log.debug("Updating entry [%s].", normalized_entry)

        client = self.__auth.get_client()

        body = { 'mimeType': mime_type }

        if filename is not None:
            body['title'] = filename
        
        if parents is not None:
            body['parents'] = parents

        if is_hidden is not None:
            body['labels'] = { "hidden": is_hidden }

        if description is not None:
            body['description'] = description

        set_mtime = True
        if modified_datetime is not None:
            body['modifiedDate'] = modified_datetime
        else:
            body['modifiedDate'] = get_flat_normal_fs_time_from_dt()

        if accessed_datetime is not None:
            set_atime = 1
            body['lastViewedByMeDate'] = accessed_datetime
        else:
            set_atime = 0

        args = { 'fileId': normalized_entry.id, 
                 'body': body, 
                 'setModifiedDate': set_mtime, 
                 'updateViewedDate': set_atime 
                 }

        if data_filepath:
            args['media_body'] = MediaFileUpload(data_filepath, 
                                                 mimetype=mime_type)

        result = client.files().update(**args).execute()
        normalized_entry = NormalEntry('update_entry', result)

        self.__log.debug("Entry with ID [%s] updated." % (normalized_entry.id))

        return normalized_entry

    def create_directory(self, filename, parents, **kwargs):

        mimetype_directory = Conf.get('directory_mimetype')
        return self.__insert_entry(filename, mimetype_directory, parents, 
                                   **kwargs)

    def create_file(self, filename, data_filepath, parents, mime_type=None, 
                    **kwargs):
# TODO: It doesn't seem as if the created file is being registered.
        # Even though we're supposed to provide an extension, we can get away 
        # without having one. We don't want to impose this when acting like a 
        # normal FS.

        # If no data and no mime-type was given, default it.
        if mime_type == None:
            mime_type = Conf.get('file_default_mime_type')
            self.__log.debug("No mime-type was presented for file "
                             "create/update. Defaulting to [%s]." % 
                             (mime_type))

        return self.__insert_entry(filename,
                                   mime_type,
                                   parents,
                                   data_filepath,
                                   **kwargs)

    def rename(self, normalized_entry, new_filename):

        result = split_path_nolookups(new_filename)
        (path, filename_stripped, mime_type, is_hidden) = result

        self.__log.debug("Renaming entry [%s] to [%s]. IS_HIDDEN=[%s]" % 
                         (normalized_entry, filename_stripped, is_hidden))

        return self.update_entry(normalized_entry, filename=filename_stripped, 
                                 is_hidden=is_hidden)

    def remove_entry(self, normalized_entry):

        self.__log.info("Removing entry with ID [%s]." % (normalized_entry.id))

        client = self.__auth.get_client()

        args = { 'fileId': normalized_entry.id }

        try:
            result = client.files().delete(**args).execute()
        except (Exception) as e:
            if e.__class__.__name__ == 'HttpError' and \
               str(e).find('File not found') != -1:
                raise NameError(normalized_entry.id)

            self.__log.exception("Could not send delete for entry with ID "
                                 "[%s]." %
                                 (normalized_entry.id))
            raise

        self.__log.info("Entry deleted successfully.")

class _GoogleProxy(object):
    """A proxy class that invokes the specified Google Drive call. It will 
    automatically refresh our authorization credentials when the need arises. 
    Nothing inside the Google Drive wrapper class should call this. In general, 
    only external logic should invoke us.
    """
    
    def __init__(self):
        self.__log = logging.getLogger().getChild('GoogleProxy')
        self.authorize      = get_auth()
        self.gdrive_wrapper = _GdriveManager()

    def __getattr__(self, action):
        self.__log.debug("Proxied action [%s] requested." % (action))
    
        try:
            method = getattr(self.gdrive_wrapper, action)
        except (AttributeError):
            self.__log.exception("Action [%s] can not be proxied to Drive. "
                              "Action is not valid." % (action))
            raise

        def proxied_method(auto_refresh=True, **kwargs):
            # Now, try to invoke the mechanism. If we succeed, return 
            # immediately. If we get an authorization-fault (a resolvable 
            # authorization problem), fall through and attempt to fix it. Allow 
            # any other error to bubble up.
            
            self.__log.debug("Attempting to invoke method for action [%s]." % 
                             (action))

            for n in range(0, 5):
                try:
                    return method(**kwargs)
                except (ssl.SSLError, httplib.BadStatusLine) as e:
                    # These happen sporadically. Use backoff.
                    self.__log.exception("There was a transient connection "
                                         "error (%s). Trying again (%s): %d" %
                                         (e.__class__.__name__, str(e), n))

                    time.sleep((2 ** n) + random.randint(0, 1000) / 1000)
                except HttpError as e:
                    try:
                        error = json.loads(e.content)
                    except ValueError:
                        _logger.error("Non-JSON error while doing chunked "
                                      "download: %s", e.content) 
                    
                    if error.get('code') == 403 and \
                       error.get('errors')[0].get('reason') \
                       in ['rateLimitExceeded', 'userRateLimitExceeded']:
                        # Apply exponential backoff.
                        self.__log.exception("There was a transient HTTP "
                                             "error (%s). Trying again (%d): "
                                             "%s" %
                                             (e.__class__.__name__, str(e), n))

                        time.sleep((2 ** n) + random.randint(0, 1000) / 1000)
                    else:
                        # Other error, re-raise.
                        raise
                except AuthorizationFaultError:
                    # If we're not allowed to refresh the token, or we've
                    # already done it in the last attempt.
                    if not auto_refresh or n == 1:
                        raise

                    # We had a resolvable authorization problem.

                    self.__log.info("There was an authorization fault under "
                                    "action [%s]. Attempting refresh." % 
                                    (action))
                    
                    authorize = get_auth()
                    authorize.check_credential_state()

                    # Re-attempt the action.

                    self.__log.info("Refresh seemed successful. Reattempting "
                                    "action [%s]." % (action))
                        
        return proxied_method
                
def drive_proxy(action, auto_refresh=True, **kwargs):
    if drive_proxy.gp == None:
        drive_proxy.gp = _GoogleProxy()

    method = getattr(drive_proxy.gp, action)
    return method(auto_refresh, **kwargs)
    
drive_proxy.gp = None

