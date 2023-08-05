import urllib2
import hashlib
import datetime
import os
import time
import httplib, mimetypes
from xml.dom.minidom import parseString # lxml2

class MediaFireFolder(object):
    """ Represents a folder located at MediaFire
    """

    def __init__(self,token,filexml=None):
        self._session_token = token

        if filexml:
            self._load_info(filexml)

    def __repr__(self):
        return "FOLDER: {} {}".format(self.name, self.folder_key)

    def setup(self,name,folder_key):
        self.name = name
        self.folder_key = folder_key

    def _load_info(self,f):
        """ Parse an XML fragment to get folder's informations
        """

        c = f.getElementsByTagName("name")[0]
        self.name = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")

        c = f.getElementsByTagName("folderkey")[0]
        self.folder_key = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")





class MediaFireFile(object):
    """ Represents a file located at MediaFire
    """

    def __init__(self,token,filexml):
        self._session_token = token
        self._load_info(filexml)

    def __repr__(self):
        return "FILE: {} {} bytes {} {}".format(self.filename, self.size, self.creation_date, self.quick_key)

    def _load_info(self,f):
        """ Parse an XML fragment to get file's informations
        """

        c = f.getElementsByTagName("filename")[0]
        self.filename = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")

        c = f.getElementsByTagName("size")[0]
        size = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")
        self.size = int(size)

        c = f.getElementsByTagName("quickkey")[0]
        self.quick_key = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")

        c = f.getElementsByTagName("created")[0]
        creation_date_text = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")
        self.creation_date = datetime.datetime.strptime(creation_date_text,'%Y-%m-%d %H:%M:%S')


class DevNullLogger(object):
    def __init__(self):
        pass

    def debug(self,p):
        pass

    def info(self,p):
        pass

    def exception(self,p):
        pass


class MediaFireSession(object):
    """ Represents a session with MediaFire.
    This is the main class you'll use to interact with MediaFire.
    It supports the very basic subset of the MediaFire API (download/upload, read/create folders).
    Feel free to contribute patches.
    """


    MEDIAFIRE_DOMAIN = 'www.mediafire.com'

    def _call(self,selector,https=True):
        protocol = ""
        if https:
            protocol = "s"

        url = "http{}://{}/api{}".format(protocol,self.MEDIAFIRE_DOMAIN,selector)
        f = self.urlopener.open(url)
        res = f.read()
        self.logger.debug("Called {}".format(url))
        return res



    def __init__(self,email,password,appid,sessionkey,proxy_url=None,proxy_port=None,logger=None):
        """ Initialize a session to MediaFire
        email, password, appid and sessionkey is the authorization tuple for MediaFire.
        proxy_url and proxy_port are optional. Since some MediaFire operations
        require https, we expect http and https proxy to be located at the
        same address and port.
        """

        if logger:
            self.logger = logger
        else:
            self.logger = DevNullLogger()

        self.proxy_url = proxy_url
        self.proxy_port = proxy_port

        if proxy_url:
            proxy = "{}:{}".format(proxy_url,proxy_port)
            self.logger.debug("Using a proxy : {}".format(proxy))

            self.urlopener = urllib2.build_opener(
                urllib2.ProxyHandler({'https': proxy,
                                      'http' : proxy}))
        else:
            self.urlopener = urllib2.build_opener(
                urllib2.HTTPHandler(),
                urllib2.HTTPSHandler())

        h = hashlib.sha1()
        h.update("{}{}{}{}".format(email,password,appid,sessionkey))

        try:
            tokenxml = self._call("/user/get_session_token.php?email={}&password={}&application_id={}&signature={}&version=1".format(email,password,appid,h.hexdigest()))

            dom = parseString(tokenxml)
            self._session_token = dom.getElementsByTagName('session_token')[0].firstChild.toxml()

            self.logger.debug("Session opened!")
        except Exception, ex:
            self.logger.error("Unable to open a session on mediafire")
            self.logger.exception(ex)
            self._session_token = None
            raise ex



    def load_folder(self,mfdir=None):
        """ Load a directory represented by a MediaFireFolder without recursion.
        If no folder is given, then the root folder is loaded.
        Returns a sequence of MediaFireFile and MediaFireFolder
        """
        assert mfdir is None or type(mfdir) == MediaFireFolder

        folder_key = ""
        if mfdir is not None:
            folder_key = "&folder_key=" + mfdir.folder_key

        content = self._call("/folder/get_content.php?session_token={}&content_type=files{}".format(self._session_token,folder_key))
        allfiles = []
        for f in parseString(content).getElementsByTagName("file"):
            allfiles.append(MediaFireFile(self._session_token,f))

        content = self._call("/folder/get_content.php?session_token={}&content_type=folders{}".format(self._session_token,folder_key))
        for f in parseString(content).getElementsByTagName("folder"):
            # print f.toprettyxml()
            allfiles.append(MediaFireFolder(self._session_token,f))

        return allfiles



    def create_folder(self,foldername):
        """ Create a folder with the given name.
        Returns a MediaFireFolder representing the created folder.
        """

        content = self._call("/folder/create.php?session_token={}&foldername={}".format(self._session_token,foldername))

        c = parseString(content).getElementsByTagName("folder_key")[0]
        folder_key = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")

        folder = MediaFireFolder(self._session_token)
        folder.setup(foldername,folder_key)
        return folder


    def upload(self,mediafire_folder,outfile):
        """ Upload the file of path outfile into the given folder.
        If the give folder is None, then we upload to the root directory.
        The name of the file in MediaFire is the filename without the path.
        This will block until the file is successfuly uploaded.
        """

        assert mediafire_folder is None or type(mediafire_folder) == MediaFireFolder

        in_file = file(outfile,'rb')

        upload_key = ""
        if mediafire_folder:
            upload_key = "&uploadkey={}".format(mediafire_folder.folder_key)

        self.logger.debug("Uploading {} as {}".format(outfile,os.path.split(outfile)[-1]))

        res = self._post_multipart(self.MEDIAFIRE_DOMAIN + ":80",
                                   "/api/upload/upload.php?session_token={}{}".format(self._session_token,upload_key),
                                   [], [(os.path.split(outfile)[-1],os.path.split(outfile)[-1],in_file.read())])
        in_file.close()

        c = parseString(res).getElementsByTagName("key")[0]
        upload_key = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")

        status = None
        while status != '99':
            if status is not None:
                time.sleep(5)

            res = self._call("/upload/poll_upload.php?session_token={}&key={}".format(self._session_token,upload_key),https=False)
            c = parseString(res).getElementsByTagName("status")[0]
            status = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")

    def delete(self, f):
        """ Deletes the given MediaFireFile
        """

        resp = self._call("/file/delete.php?session_token={}&quick_key={}".format(self._session_token,f.quick_key))


    def download(self, f, outfile):
        """ Download the given MediaFireFile into outfile.
        We check that the downloaded file size equals he file size reported
        by Mediafire.
        """
        
        resp = self._call("/file/get_links.php?session_token={}&quick_key={}&link_type=direct_download".format(self._session_token,f.quick_key))

        c = parseString(resp).getElementsByTagName("direct_download")[0]
        download_url = reduce(lambda acc,node: acc + node.nodeValue, c.childNodes,"")

        out = file(outfile,'wb')
        out.write( self.urlopener.open(download_url).read())
        out.close()

        dlsize = os.path.getsize(outfile)

        if f.size != dlsize:
            raise Exception("Downloaded file size is {} bytes and DOES NOT correspond to mediafire ({})".format(dlsize,f.size))


    def _post_multipart(self,host, selector, fields, files):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return the server's response page.
        """
        content_type, body = self._encode_multipart_formdata(fields, files)

        # request = urllib2.Request('http://example.org', data='your_put_data')
        # request.add_header('Content-Type', 'your/contenttype')
        # request.get_method = lambda: 'POST'
        # url = opener.open(request)

        h = None
        if self.proxy_url:
            h = httplib.HTTPConnection(self.proxy_url, self.proxy_port)
            h.putrequest('POST', "http://" + host + selector)
        else:
            h = httplib.HTTPConnection(host)
            h.putrequest('POST', selector)

        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.putheader('x-filesize', str(len(body)))
        h.endheaders()

        h.send(body)

        t =  h.getresponse().read()
        return t

        errcode, errmsg, headers = h.getreply()
        return h.file.read()



    def _encode_multipart_formdata(self,fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self._get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def _get_content_type(self,filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
