#!/usr/bin/env python
#coding: utf-8

"""
mdfmonitor - Monitor the file moification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **mdfmonitor** is Python module about monitoring files modification using timestamp and body.

How to use:

It's simple. 
1. Import this module.
2. Create `ModificationMonitor` class's instance.
3. Append file or files to instance using add_file method.
4. using Python for sentence, You can write anything under for sentence.

    >>> from mdfmonitor import ModificationMonitor
    >>> monitor = ModificationMonitor()
    >>> monitor.add_file("README.md")
    >>> for mdf in monitor.monitor():
    ...     print "Old timestamp: %s" % mdf.old_mtime
    ...     print "New timestamp: %s" % mdf.new_mtime
    ...     print "manager: %s" % str(mdf.manager.o_repository)
    ...     print "Diff".center(30,"=")
    ...     print mdf.diff

"""

import os
import sys
import time
import difflib
import requests

from dateutil import parser
from dateutil import tz

__version__ = "0.1.2b"

#
# Error Classes
# --------------------------
class DuplicationError(BaseException):
    """Raise this Error if you add duplication something."""

    pass

class StatusError(BaseException):
    """Raise this Error if url return invalid status code."""

    pass

class ConnectionError(requests.exceptions.ConnectionError):
    """Raise this Error if monitor can't connect url server.
    This Error inherit requests.exceptions.ConnectionError."""

    pass

#
# The Monitor classes of File Modification
# ---------------------------------------------
class FileModificationMonitor(object):
    """The ModificationMonitor can monitoring file modification.
    usage:

    it's simple.
    1. Create instance (call this instance `monitor` from now).
    2. Append file to instance using `add_file` or `add_files` method.
       Monitor has a file repository, monitor append file to repository using 
       `add_file` method. Please put a file name to argument. If you use 
       `add_files` method and put list of file to argument, Monitor append 
       files to repository.
    3. Run monitor uring `monitor` method.
       The `monitor` method is generator, return FileModificationObject.

    """

    def __init__(self):

        self.f_repository = []

    def add_file(self, file, **kwargs):
        """Append a file to file repository.

        For file monitoring, monitor instance needs file.
        Please put the name of file to `file` argument.

        :param file: the name of file you want monitor.

        """

        if os.access(file, os.F_OK):

            if file in self.f_repository:
                raise DuplicationError("file already added.")

            self.f_repository.append(file)

        else:
            raise IOError("file not found.")


    def add_files(self, filelist, **kwargs):
        """Append files to file repository.
        
        ModificationMonitor can append files to repository using this.
        Please put the list of file names to `filelist` argument.

        :param filelist: the list of file nmaes
        """

        # check filelist is list type
        if not isinstance(filelist, list):
            raise TypeError("request the list type.")

        for file in filelist:
            self.add_file(file)    

    def monitor(self, sleep=5):
        """Run file modification monitor.

        The monitor can catch file modification using timestamp and file body. 
        Monitor has timestamp data and file body data. And insert timestamp 
        data and file body data before into while roop. In while roop, monitor 
        get new timestamp and file body, and then monitor compare new timestamp
        to originaltimestamp. If new timestamp and file body differ original,
        monitor regard thease changes as `modification`. Then monitor create
        instance of FileModificationObjectManager and FileModificationObject,
        and monitor insert FileModificationObject to FileModificationObject-
        Manager. Then, yield this object.

        :param sleep: How times do you sleep in while roop.
        """


        manager = FileModificationObjectManager()

        timestamps = {}
        filebodies = {}

        # register original timestamp and filebody to dict
        for file in self.f_repository:
            timestamps[file] = self._get_mtime(file)
            filebodies[file] = open(file).read()


        while True:

            for file in self.f_repository:

                mtime = timestamps[file]
                fbody = filebodies[file]

                modified = self._check_modify(file, mtime, fbody)

                # file not modify -> continue
                if not modified:
                    continue

                # file modifies -> create the modification object

                new_mtime = self._get_mtime(file)
                new_fbody = open(file).read()

                obj = FileModificationObject(
                        file,
                        (mtime, new_mtime),
                        (fbody, new_fbody) )

                # overwrite new timestamp and filebody
                timestamps[file] = new_mtime
                filebodies[file] = new_fbody


                # append file modification object to manager
                manager.add_object(obj)

                # return new modification object
                yield obj

            time.sleep(sleep)


    def _get_mtime(self, file):

        return os.stat(file).st_mtime


    def _check_modify(self, file, o_mtime, o_fbody):

        n_mtime = self._get_mtime(file)
        n_fbody = open(file).read()

        if n_mtime == o_mtime:
            return False

        else:

            if n_fbody == o_fbody:
                return False

            else:

                return True


class ModificationObjectManager(object):
    """This manager manages  modification objects.

    Manager has a history list of ModificationObject. Object can refer to 
    any object what above or below position. Maager is iterable if manager was
    added object. If manager has not any object, manager is not iterable.
    """

    def __init__(self):

        self.o_repository = []

        self.__is_iterable = False
        self.__r_pointer = 0


    def add_object(self, obj):

        self.o_repository.append(obj)

        obj._set_manager(self)

        if not self.__is_iterable:
            self.__is_iterable = True

        return self

    def __iter__(self):

        if not self.__is_iterable:
            raise TypeError(
                    "'%s' object is not iterable" % self.__class__.__name__)
            return self

    def next(self):

        if not self.__is_iterable:
            raise TypeError(
                    "'%s' object is not iterable" % self.__class__.__name__)

            if self.__r_pointer == len(self.o_repository):
                raise StopIteration

        result = self.o_repository[self.__r_pointer]
        self.__r_pointer += 1
        return result

    def __next__(self):

        return self.next()

    def seek(self, offset):

        self.__r_pointer = offset

class FileModificationObject(object):
    """The FileModificationObject has any element of file modification.

    The object can generate difference of old and new file body Because object
    has old and new file body. 

    :param file: file name
    :param t_mtime: this is tuple of old and new timestamp.
    :param t_fbody: this is tuple of old and new file body.
    """

    def __init__(self, file, t_mtime, t_fbody):

        self.file = file

        self.old_mtime, self.new_mtime = t_mtime
        self.old_fbody, self.new_fbody = t_fbody

        self.manager = None
        self.diff = self._diffgen()

    def _set_manager(self, manager):

        self.manager = manager

    def _diffgen(self):

        contents = []

        for line  in difflib.unified_diff(
                self.old_fbody.splitlines(),
                self.new_fbody.splitlines(),
                "old/"+self.file, "new/"+self.file,
                self._strftime(self.old_mtime),
                self._strftime(self.new_mtime)):

            contents.append(line)

        return "\n".join(contents)

    def _strftime(self, etime):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(etime))


#
# The Monitor classes of URL Modification
# ---------------------------------------------
class URLModificationMonitor(object):

    def __init__(self):

        self.url_repository = []

    def add_url(self, url, **kwargs):

        if url in self.url_repository:
            raise DuplicationError("url already added.")

        if not self._is_status(url, 200):
            raise StatusError("This URL didn't return 200 status code.")

        self.url_repository.append(url)

    def add_urls(self, urllist, **kwargs):

        # check urllist is list type
        if not isinstance(urllist, list):
            raise TypeError("request the list type.")

        for url in urllist:
            self.add_url(url)

    def monitor(self, sleep=60):

        manager = ModificationObjectManager()

        datestamps = {}
        respbodies = {}

        # register original datestamp and htmlbody to dict
        for url in self.url_repository:
            datestamps[url] = self._get_dtime(url)
            respbodies[url] = self._access(url).text

        while True:

            for url in self.url_repository:

                dtime = datestamps[url]
                rbody = respbodies[url]

                modified = self._check_modify(url, dtime, rbody)

                if not modified:
                    continue

                new_dtime = self._get_dtime(url)
                new_rbody = self._access(url).text

                obj = URLModificationObject(
                        url,
                        (dtime, new_dtime),
                        (rbody, new_rbody) )

                datestamps[url] = new_dtime
                respbodies[url] = new_rbody

                manager.add_object(obj)

                yield obj

            time.sleep(sleep)

    def _is_status(self, url, status_code):

        return self._access(url).status_code == status_code
    
    def _get_dtime(self, url):

        # parse header's date to datetime object
        o_date = parser.parse(self._access(url).headers["date"])

        # change timezone from GMT to local timezone
        return o_date.astimezone(tz.tzlocal())

    def _check_modify(self, url, o_dtime, o_rbody):

        n_dtime = self._get_dtime(url)
        n_rbody = self._access(url).text

        if n_dtime == o_dtime:
            return False

        else:

            if n_rbody == o_rbody:
                return False

            else:

                return True

    def _access(self, url):

        header = {"User-Agent": \
                        "URLModificationMonitor/" + \
                        "%s " % __version__ + \
                        "(about me: https://github.com/alice1017/mdfmonitor)"}

        try:
            return requests.get(url, headers=header)

        except requests.exceptions.ConnectionError:
            raise ConnectionError("Monitor can't connect the server of url you added.")
                

        
class URLModificationObject(object):
    """The URLModificationObject has any element of url modification.

    The object can generate difference of old and new html body Because object
    has old and new html body. 

    :param url: file name
    :param t_dtime: this is tuple of old and new timestamp.
    :param t_rbody: this is tuple of old and new file body.
    """

    def __init__(self, url, t_dtime, t_rbody):

        self.url = url

        self.old_dtime, self.new_dtime = t_dtime
        self.old_rbody, self.new_rbody = t_rbody

        self.manager = None
        self.diff = self._diffgen()

    def _set_manager(self, manager):

        self.manager = manager

    def _diffgen(self):

        contents = []

        for line  in difflib.unified_diff(
                self.old_rbody.splitlines(),
                self.new_rbody.splitlines(),
                "old/"+self.url, "new/"+self.url,
                self._strftime(self.old_dtime),
                self._strftime(self.new_dtime)):

            contents.append(line)

        return "\n".join(contents)

    def _strftime(self, etime):
        return etime.strftime('%Y-%m-%d %H:%M:%S')





