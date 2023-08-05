#!/usr/bin/env python
# -*- coding:UTF-8

#
# Created on 2012-8-9
#
# @author: tangcheng
#
# Example:
#    import nos
#
#    nos = Nos('172.17.2.64:8182', 'nos.netease.com',
#    access_key = "89eff7c728f0401e894d9566a4aa4bd4",
#    access_secret = "e7088fa7cfe50816b4ad9de423cc8d54")
#    data = 'adasdafsdffasdfasdfasdfasf'
#    nos.putObject('bucket01',  'object0001', data)
#    nos.putObjectWithDeDup('bucket01',  'object0002', data)
#    data = nos.getObject('bucket01', 'object0001')
#    nos.deleteObject('bucket01','object0001')
#    nos.deleteObject('bucket01','object0002')
#

import hashlib
import hmac
import binascii
import httplib
import logging
import time
import xml.dom.minidom
import urllib

LOG = logging.getLogger(__name__)


def construct_error_message_xml(message):
    error_message = '<?xml version="1.0" encoding="UTF-8"?>\n'
    error_message += '<Error><Message>%s</Message></Error>' % message
    return error_message


def httpDate(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.tm_wday]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.tm_mon - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.tm_mday, month,
        dt.tm_year, dt.tm_hour, dt.tm_min, dt.tm_sec)


class NosError(Exception):
    def __init__(self, arg0, arg1):
        LOG.error(arg1)
        try:
            doc = xml.dom.minidom.parseString(arg1)
            node = doc.getElementsByTagName("Error")[0]
            arg1 = node.getElementsByTagName('Message')[0].childNodes[0].data
        except:
            # NOTE(hzzhoushaoyu): if arg1 is not xml constructure,
            # get whole information of arg1.
            pass
        if isinstance(arg0, unicode):
            arg0 = arg0.encode('utf8')
        if isinstance(arg1, unicode):
            arg1 = arg1.encode('utf8')
        self.arg = [arg0, arg1]

    def __str__(self):
        return "NosError('" + str(self.arg[0]) + "','" \
                        + str(self.arg[1]) + "')"

    def __repr__(self):
        return "NosError('" + repr(self.arg[0]) + "','" \
                        + repr(self.arg[1]) + "')"


class Nos():
    def __init__(self, context, url, host, access_key, access_secret,
                 is_whitelist=False, use_nos_store_class=False):
        '''
        if one uses white list, it should set project_id and display_name,
        and NOS should open white list for the host ip.
        otherwise, the access_key and access_secret should be passed in.
        In NOS white list head,access_secret should be set value as projectId
        and access_key should be set value as display_name.
        '''
        self.context = context
        self.url = url
        self.host = host
        self.is_whitelist = is_whitelist
        self.access_key = access_key
        self.access_secret = access_secret
        self.use_nos_store_class = use_nos_store_class
        self.nos_whitelist_head = "%s %s" % \
                            (self.access_secret, self.access_key)

    def __del__(self):
        pass

    def _get_auth_head(self, bucketName, objectKey, vDate, httpVerb,
                       contentType, contentMD5, canonicalized_headers=None):
        if bucketName:
            bucketName = urllib.quote(bucketName)

        if objectKey:
            objectKey = urllib.quote(objectKey)

        stringToSign = "%s\n%s\n%s\n%s\n" % (httpVerb, contentMD5,
                                             contentType, vDate)
        if canonicalized_headers is not None:
            stringToSign += "%s\n" % canonicalized_headers
        stringToSign += "/%s/" % bucketName
        if objectKey is not None:
            stringToSign += objectKey
        hashed = hmac.new(self.access_secret, stringToSign, hashlib.sha256)
        signature = binascii.b2a_base64(hashed.digest())[:-1]
        authorization = "NOS" + " " + self.access_key + ":" + signature
        return authorization

    def _update_auth_header(self, bucketName, objectKey, vDate, httpVerb,
                contentMD5, contentType, headers, canonicalized_headers=None):
        self._update_store_class_header(headers)
        if "x-nos-storage-class" in headers:
            # FIXME(hzzhoushaoyu): canonicalized headers should order in ASC.
            # if canonicalized is not None, please make sure
            # x-nos-storage-class is in right place.
            if canonicalized_headers is None:
                canonicalized_headers = "x-nos-storage-class:%s" % \
                                        headers['x-nos-storage-class']
            else:
                canonicalized_headers = "\nx-nos-storage-class:%s" % \
                                        headers['x-nos-storage-class']
        if self.is_whitelist:
            headers.update({"x-nos-whitelist": self.nos_whitelist_head})
        else:
            authorization = self._get_auth_head(bucketName, objectKey,
                vDate, httpVerb, contentType, contentMD5,
                canonicalized_headers)
            headers.update({"Authorization": authorization})

    def _update_store_class_header(self, headers):
        if self.use_nos_store_class:
            headers.update({"x-nos-storage-class": "sata-critical"})

    #url='172.17.2.64:8182'
    #PUT /${ObjectKey} HTTP/1.1
    #HOST: ${BucketName}.nos.163.com
    #Content-Length: ${length}
    #Content-MD5: ${md5}
    #Authorization: ${signature}
    def putObject(self, bucketName, objectKey, content, contentLength):
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'PUT'
        contentMD5 = hashlib.md5(content).hexdigest().upper()
        contentType = ''

        headers = {
        "HOST": "%s.%s" % (bucketName, self.host),
        "Content-Length": contentLength,
        "Content-MD5": contentMD5,
        "Date": vDate
        }
        self._update_auth_header(bucketName, objectKey, vDate,
                            httpVerb, contentMD5, contentType, headers)

        self.conn_request(conn, httpVerb, '/' + objectKey, content, headers)
        httpres = conn.getresponse()

        if httpres.status != 200:
            reason = httpres.read()
            raise NosError(httpres.status, reason)
        conn.close()
        return httpres.getheader("etag")

    #GET /${ObjectKey}?versionId=${version} HTTP/1.1
    #HOST: ${BucketName}.nos.163.com
    #Date: ${date}
    #Authorization: ${signature}
    #Range: ${range}
    # 404, not found
    def getObject(self, bucketName, objectKey):
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'GET'
        contentType = ''
        contentMD5 = ''

        headers = {
        "HOST": "%s.%s" % (bucketName, self.host),
        "Date": vDate,
        }
        self._update_auth_header(bucketName, objectKey, vDate, httpVerb,
                                 contentMD5, contentType, headers)

        self.conn_request(conn, httpVerb, '/' + objectKey, '', headers)
        httpres = conn.getresponse()
        res = httpres.read()
        if httpres.status != 200:
            raise NosError(httpres.status, res)
        conn.close()
        return res

    def _head_object(self, conn, bucketName, objectKey):
        vDate = httpDate(time.gmtime())
        httpVerb = 'HEAD'
        contentType = ''
        contentMD5 = ''
        headers = {
            "HOST": "%s.%s" % (bucketName, self.host),
            "Date": vDate,
            }
        self._update_auth_header(bucketName, objectKey, vDate, httpVerb,
                                 contentMD5, contentType, headers)
        self.conn_request(conn, httpVerb, '/' + objectKey, '', headers)
        httpres = conn.getresponse()
        return httpres

    def get_object_length(self, bucketName, objectKey):
        conn = httplib.HTTPConnection(self.url)
        httpres = self._head_object(conn, bucketName, objectKey)
        if httpres.status != 200:
            reason = httpres.read()
            raise NosError(httpres.status, reason)
        length = 0
        try:
            length = int(httpres.getheader("content-length", -1))
        except Exception, e:
            raise NosError("content-length is not Int",
                           construct_error_message_xml(e.message))
        conn.close()
        return length

    def checkObjectExist(self, bucketName, objectKey):
        """
        check whether object exists
        """
        conn = httplib.HTTPConnection(self.url)
        httpres = self._head_object(conn, bucketName, objectKey)
        if httpres.status == 404:
            return False
        elif httpres.status != 200:
            reason = httpres.read()
            raise NosError(httpres.status, reason)
        conn.close()
        return True

    #return ${host_name:port}/${BucketName}/${ObjectKey}?
    #NOSAccessKeyId=${NOSaccessKey}&Expires=${expires}&Signature=${signature}
    def getObjectURL(self, bucketName, objectKey, expires, use_domain=True):
        '''
        Note(hzzhoushaoyu): only specified user can access object url
        '''
        # FIXME(hzzhoushaoyu): if url is to response to user,
        # this url may expose too much information to user
        if self.is_whitelist:
            raise NosError(403, construct_error_message_xml(
                                    "should not get url by white list user"))
        httpVerb = 'GET'
        contentType = ''
        contentMD5 = ''

        stringToSign = "%s\n%s\n%s\n%s\n/%s/%s" % (httpVerb, contentMD5,
                                contentType, expires, bucketName, objectKey)

        hashed = hmac.new(self.access_secret, stringToSign, hashlib.sha256)
        signature = urllib.quote_plus(
                            binascii.b2a_base64(hashed.digest()).strip())

        url2 = "/%s/%s?NOSAccessKeyId=%s&Expires=%s&Signature=%s" % \
                (bucketName, objectKey, self.access_key, expires, signature)

        if use_domain:
            return self.host + url2
        else:
            return self.url + url2

    #PUT /${ObjectKey}?deduplication HTTP/1.1
    #HOST: ${BucketName}.nos.163.com
    #Content-Length :
    #Content-MD5: ${md5}
    #x-nos-object-md5: ${objectMD5}
    #Authorization: ${signature}
    def deduplicate(self, bucketName, objectKey, md5):
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'PUT'
        contentType = ''
        contentMD5 = ''

        headers = {
        "HOST": "%s.%s" % (bucketName, self.host),
        "Content-Length": 0,
        "Date": vDate,
        "x-nos-object-md5": md5
        }
        self._update_auth_header(bucketName, objectKey, vDate, httpVerb,
                                 contentMD5, contentType, headers)
        self.conn_request(conn, httpVerb, '/' + objectKey + '?deduplication',
                          '', headers)

        httpres = conn.getresponse()
        result = httpres.read()
        if httpres.status != 200:
            raise NosError(httpres.status, result)
        conn.close()
        doc = xml.dom.minidom.parseString(result)
        nodes = doc.getElementsByTagName("ObjectContentAlreadyExist")
        wrong_result_message = "NOS returned the wrong result: %s" % (result)
        if len(nodes) <= 0:
            raise NosError(-1,
                           construct_error_message_xml(wrong_result_message))

        if not nodes[0].childNodes:
            raise NosError(-1,
                           construct_error_message_xml(wrong_result_message))

        if len(nodes[0].childNodes) <= 0:
            raise NosError(-1,
                           construct_error_message_xml(wrong_result_message))

        if nodes[0].childNodes[0].nodeValue.lower() == "true":
            return 1
        elif nodes[0].childNodes[0].nodeValue.lower() == "false":
            return 0
        else:
            raise NosError(-1,
                           construct_error_message_xml(wrong_result_message))

    def putObjectWithDeDup(self, bucketName, objectKey,
                           content, contentLength):
        contentMD5 = hashlib.md5(content).hexdigest().upper()
        isDup = self.deduplicate(bucketName, objectKey, contentMD5)
        if not isDup:
            self.putObject(bucketName, objectKey, content, contentLength)

    #DELETE /${ObjectKey} HTTP/1.1
    #HOST: ${BucketName}.nos.163.com
    #Authorization: ${signature}
    #return 404 status if not exists
    def deleteObject(self, bucketName, objectKey):
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'DELETE'
        contentType = ''
        contentMD5 = ''

        headers = {
        "HOST": "%s.%s" % (bucketName, self.host),
        "Date": vDate
        }
        self._update_auth_header(bucketName, objectKey, vDate,
                                 httpVerb, contentMD5, contentType, headers)

        self.conn_request(conn, httpVerb, '/' + objectKey, '', headers)

        httpres = conn.getresponse()
        if httpres.status != 200:
            reason = httpres.read()
            raise NosError(httpres.status, reason)
        conn.close()

    #hzzhoushaoyu add
    def create_bucket(self, bucket_name, location_constraint="HZ",
                      object_deduplicate="False"):
        """
        PUT / HTTP/1.1
        HOST: {bucket_name}.nos.netease.com
        Content-Length: {contentLength}
        Authorization: {signature}

        <CreateBucketConfiguration >
            <location_constraint>{location_constraint}</location_constraint>
            <object_deduplicate>{object_deduplicate}</object_deduplicate>
        </CreateBucketConfiguration >

        :param bucket_name: the name of bucket
        :param location_constraint: HZ|BJ|GZ default HZ
        :param object_deduplicate: whether support deduplicate
        :retval: the response from nos
        """

        content = "<CreateBucketConfiguration ><location_constraint>" + \
                     location_constraint + "</location_constraint>" + \
                    "<object_deduplicate>" + object_deduplicate + \
                    "</object_deduplicate></CreateBucketConfiguration >"
        contentLength = len(content)
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'PUT'
        contentType = 'text/xml'
        contentMD5 = hashlib.md5(content).hexdigest()

        headers = {
        "HOST": "%s.%s" % (bucket_name, self.host),
        "Content-Length": contentLength,
        "Content-Type": contentType,
        "Content-MD5": contentMD5,
        "Date": vDate
        }
        self._update_auth_header(bucket_name, None, vDate,
                                 httpVerb, contentMD5, contentType, headers)

        self.conn_request(conn, httpVerb, '/', content, headers)

        httpres = conn.getresponse()
        res = httpres.read()
        conn.close()
        if httpres.status != 200:
            raise NosError(httpres.status, res)
        return res

    #hzzhoushaoyu add
    def check_bucket_exist(self, bucket_name):
        """
        check whether bucket exists
        """
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'HEAD'
        contentType = ''
        contentMD5 = ''

        headers = {
        "HOST": "%s.%s" % (bucket_name, self.host),
        "Date": vDate
        }
        self._update_auth_header(bucket_name, None, vDate,
                                 httpVerb, contentMD5, contentType, headers)

        self.conn_request(conn, httpVerb, '/', '', headers)

        httpres = conn.getresponse()
        if httpres.status == 404:
            return False
        elif httpres.status != 200:
            reason = httpres.read()
            raise NosError(httpres.status, reason)
        conn.close()
        return True

    def list_bucket_objects(self, bucket_name):
        '''
        list all objects in the bucket
        '''
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'GET'
        contentType = ''
        contentMD5 = ''

        headers = {
        "HOST": "%s.%s" % (bucket_name, self.host),
        "Date": vDate
        }
        self._update_auth_header(bucket_name, None, vDate, httpVerb,
                                 contentMD5, contentType, headers)
        self.conn_request(conn, httpVerb, '/', '', headers)

        httpres = conn.getresponse()
        result = httpres.read()
        conn.close()
        if httpres.status != 200:
            raise NosError(httpres.status, result)
        return result

    def delete_bucket(self, bucket_name):
        """
        delete the bucket named bucket_name
        """
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'DELETE'
        contentType = ''
        contentMD5 = ''

        headers = {
        "HOST": "%s.%s" % (bucket_name, self.host),
        "Date": vDate
        }
        self._update_auth_header(bucket_name, None, vDate, httpVerb,
                                 contentMD5, contentType, headers)
        self.conn_request(conn, httpVerb, '/', '', headers)

        httpres = conn.getresponse()
        if httpres.status != 200:
            reason = httpres.read()
            raise NosError(httpres.status, reason)
        conn.close()

    #hzzhoushaoyu add
    def init_multi_upload(self, bucket_name, object_key):
        """
        init a multi part upload and return the upload id
        """
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'POST'
        contentType = ''
        contentMD5 = ''

        headers = {
        "HOST": "%s.%s" % (bucket_name, self.host),
        "Date": vDate
        }
        self._update_auth_header(bucket_name, object_key + "?uploads",
                            vDate, httpVerb, contentMD5, contentType, headers)
        self.conn_request(conn, httpVerb, '/' + object_key + "?uploads", '',
                          headers)

        httpres = conn.getresponse()
        result = httpres.read()
        if httpres.status != 200:
            raise NosError(httpres.status, result)
        conn.close()
        doc = xml.dom.minidom.parseString(result)
        nodes = doc.getElementsByTagName("InitiateMultipartUploadResult")
        wrong_result_message = "NOS returned the wrong result: %s" % (result)
        if len(nodes) <= 0:
            raise NosError(-1,
                           construct_error_message_xml(wrong_result_message))

        if not nodes[0].childNodes:
            raise NosError(-1,
                           construct_error_message_xml(wrong_result_message))

        if len(nodes[0].childNodes) <= 6:   # include '\n' Text node
            raise NosError(-1,
                           construct_error_message_xml(wrong_result_message))
        upload_id = nodes[0].childNodes[5].childNodes[0].data
        return upload_id

    #hzzhoushaoyu add
    def upload_part(self, bucket_name, object_key, part_number,
                    upload_id, content):
        """
        upload a part of the muti part with part_number and upload_id

        :retval: return the part etag
        """
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())
        content_length = len(content)
        httpVerb = 'PUT'
        contentMD5 = hashlib.md5(content).hexdigest().upper()
        contentType = ''
        resource = object_key + "?partNumber=" + str(part_number) + \
                            "&uploadId=" + upload_id
        headers = {
        "HOST": "%s.%s" % (bucket_name, self.host),
        "Content-Length": content_length,
        "Content-MD5": contentMD5,
        "Date": vDate
        }
        self._update_auth_header(bucket_name, resource, vDate, httpVerb,
                                 contentMD5, contentType, headers)
        self.conn_request(conn, httpVerb, '/' + resource, content, headers)
        httpres = conn.getresponse()
        if httpres.status != 200:
            reason = httpres.read()
            raise NosError(httpres.status, reason)
        conn.close()
        return httpres.getheader("etag")

    #hzzhoushaoyu add
    def multi_upload_complete(self, bucket_name, object_key, upload_id,
                              object_md5, part_info):
        """
         multi upload complet,content upload should be large enough
        :param bucket_name: bucket name
        :param object_key: object key
        :param upload_id: upload id
        :param object_md5: for future deduplicate
        :param part_info: [{"part-number":"ETAG-FOR-PART"}]
        """
        content = "<CompleteMultipartUpload>"
        for part in part_info:
            content += "<Part><PartNumber>" + str(part.keys()[0]) + \
            "</PartNumber><ETag>" + str(part.values()[0]) + "</ETag></Part>"
        content += "</CompleteMultipartUpload>"

        contentLength = len(content)
        conn = httplib.HTTPConnection(self.url)
        vDate = httpDate(time.gmtime())

        httpVerb = 'POST'
        contentType = 'text/xml'
        contentMD5 = hashlib.md5(content).hexdigest().upper()

        canonicalized_headers = "x-nos-object-md5:" + object_md5 + "\n"
        resource = object_key + "?uploadId=" + upload_id

        headers = {
        "HOST": "%s.%s" % (bucket_name, self.host),
        "Content-Length": contentLength,
        "Content-Type": contentType,
        "Content-MD5": contentMD5,
        "Date": vDate,
        "x-nos-object-md5": object_md5
        }
        self._update_auth_header(bucket_name, resource, vDate, httpVerb,
                                 contentMD5, contentType, headers,
                                 canonicalized_headers)
        self.conn_request(conn, httpVerb, '/' + resource, content, headers)
        httpres = conn.getresponse()
        res = httpres.read()
        conn.close()
        if httpres.status != 200:
            raise NosError(httpres.status, res)
        return res

    def conn_request(self, conn, method, url, content, headers):
        logId = None
        logSeq = None

        if self.context:
            logId = self.context.to_dict().get('unified_log_id', None)
            logSeq = self.context.to_dict().get('unified_log_seq', None)

        if logId and logSeq:
            log_seq_nums = logSeq.split('.')
            log_seq_nums[-1] = str(int(log_seq_nums[-1]) + 1)
            new_log_seq = '.'.join(log_seq_nums)
            self.context.unified_log_seq = new_log_seq
            if url.endswith('?') or url.endswith('&'):
                url = url + "logid=%s&logseq=%s" % (logId, new_log_seq)
            elif url.find('?') != -1:
                url = url + "&logid=%s&logseq=%s" % (logId, new_log_seq)
            else:
                url = url + "?logid=%s&logseq=%s" % (logId, new_log_seq)
        conn.request(method, url, content, headers)
