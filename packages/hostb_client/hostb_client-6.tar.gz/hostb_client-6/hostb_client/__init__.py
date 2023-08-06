#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2014
from __future__ import division, with_statement

import cookielib
import gzip
import StringIO
import urllib2
from urlparse import urlparse

import json
import math
import os
import socket
import sys
import time

from form import MultiPartForm
from utils import format_duration, format_bytes

DEBUG = False

__version__ = '0.1'

socket.setdefaulttimeout(300)
CHUNK_SIZE = 1024*1024

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

class Client(object):
    __name__ = 'hostb_client'
    __version__ = __version__
    DEBUG = DEBUG
    debuglevel = 0

    def __init__(self, url, cj=None):
        self.base_url = url
        self.url = os.path.join(self.base_url, 'add')
        self._resume_file = '/tmp/hostb_client.%s.json' % os.environ.get('USER')
        #super(Client, self).__init__(url, cj)
        if cj:
            self._cj = cj
        else:
            self._cj = cookielib.CookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cj),
                                            urllib2.HTTPHandler(debuglevel=self.debuglevel))
        self._opener.addheaders = [
            ('User-Agent', '%s/%s' % (self.__name__, self.__version__))
        ]

    def upload(self, filename, password=''):
        return self.upload_chunks(self.url, filename, {
            'firefogg': '1',
            'name': os.path.basename(filename),
            'password': password
        })

    def upload_chunks(self, url, filename, data=None):
        form = MultiPartForm()
        resume = None
        if os.path.exists(self._resume_file):
            with open(self._resume_file) as f:
                try:
                    resume = json.load(f)
                except:
                    resume = {}
            if resume.get('chunkUploadUrl') != url:
                resume = None
        if resume:
            data = resume
        else:
            for key in data:
                form.add_field(key, data[key])
            data = self._json_request(url, form)

        print filename
        hide_cursor()
        result_url = data.get('url')
        upload_token = data.get('token')
        if 'uploadUrl' in data:
            uploadUrl = data['uploadUrl']
            if uploadUrl.startswith('/'):
                u = urlparse(url)
                uploadUrl = '%s://%s%s' % (u.scheme, u.netloc, uploadUrl)
            f = open(filename)
            fsize = os.stat(filename).st_size
            done = 0
            start = time.mktime(time.localtime())
            if 'offset' in data and data['offset'] < fsize:
                done = data['offset']
                f.seek(done)
                resume_offset = done
            else:
                resume_offset = 0
            chunk = f.read(CHUNK_SIZE)
            fname = os.path.basename(filename)
            if isinstance(fname, unicode):
                fname = fname.encode('utf-8')
            while chunk:
                elapsed = time.mktime(time.localtime()) - start
                remaining = ""
                if done:
                    r = math.ceil((elapsed / (done/(fsize-resume_offset)) - elapsed)/60) * 60
                    r = format_duration(r, milliseconds=False, verbosity=2)
                    if r:
                        remaining = ", %s remaining" % r
                msg = '%0.2f%% %s of %s done%s' % (
                    100 * done/fsize, format_bytes(done), format_bytes(fsize), remaining)
                print ''.join([msg, ' ' * (80-len(msg)), '\r']),
                sys.stdout.flush()
                form = MultiPartForm()
                form.add_file('chunk', fname, chunk)
                if len(chunk) < CHUNK_SIZE or f.tell() == fsize:
                    form.add_field('done', '1')
                try:
                    data = self._json_request(uploadUrl, form)
                except KeyboardInterrupt:
                    print "\ninterrupted by user."
                    sys.exit(1)
                except:
                    print "uploading chunk failed, will try again in 5 seconds\r",
                    sys.stdout.flush()
                    if DEBUG:
                        print '\n', uploadUrl
                        import traceback
                        traceback.print_exc()
                    data = {'result': -1}
                    time.sleep(5)
                if data and 'status' in data:
                    if data['status']['code'] == 403:
                        print "login required"
                        return False
                    if data['status']['code'] != 200:
                        print "request returned error, will try again in 5 seconds"
                        if DEBUG:
                            print data
                        time.sleep(5)
                if data and data.get('result') == 1:
                    done += len(chunk)
                    with open(self._resume_file, 'w') as r:
                        json.dump({
                            'uploadUrl': uploadUrl,
                            'chunkUploadUrl': url,
                            'url': result_url,
                            'offset': done
                        }, r, indent=2)
                    chunk = f.read(CHUNK_SIZE)
            if os.path.exists(self._resume_file):
                os.unlink(self._resume_file)
                resume = None
            if result_url:
                print result_url + (' ' * (80-len(result_url)))
                if upload_token:
                    print 'To remove this file later, you need this token: %s' % upload_token
            else:
                print ' ' * 80
            print ''
            show_cursor()
            return data and 'result' in data and data.get('result') == 1
        else:
            if DEBUG:
                if 'status' in data and data['status']['code'] == 401:
                    print "login required"
                else:
                    print "failed to upload file to", url
                    print data
        return False

    def _json_request(self, url, form):
        result = {}
        try:
            body = str(form)
            request = urllib2.Request(str(url))
            request.add_header('Content-type', form.get_content_type())
            request.add_header('Content-Length', str(len(body)))
            request.add_header('Accept-Encoding', 'gzip, deflate')
            request.add_data(body)
            f = self._opener.open(request)
            result = f.read()
            if f.headers.get('content-encoding', None) == 'gzip':
                result = gzip.GzipFile(fileobj=StringIO.StringIO(result)).read()
            result = result.decode('utf-8')
            return json.loads(result)
        except urllib2.HTTPError, e:
            if self.DEBUG:
                import webbrowser
                if e.code >= 500:
                    with open('/tmp/error.html', 'w') as f:
                        f.write(e.read())
                    webbrowser.open_new_tab('/tmp/error.html')

            result = e.read()
            try:
                result = result.decode('utf-8')
                result = json.loads(result)
            except:
                result = {'status':{}}
            result['status']['code'] = e.code
            result['status']['text'] = str(e)
            return result
        except:
            if self.DEBUG:
                import webbrowser
                import traceback
                traceback.print_exc()
                if result:
                    with open('/tmp/error.html', 'w') as f:
                        f.write(str(result))
                    webbrowser.open_new_tab('/tmp/error.html')
            raise

