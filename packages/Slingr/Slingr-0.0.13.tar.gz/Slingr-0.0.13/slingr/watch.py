# -*- coding: utf-8 -*-
"""
Watch registered Coburls for updates.

Used in developer mode to update pages.
"""

from __future__ import absolute_import

from collections import defaultdict
import datetime
import threading
import time

from slingr.common import modification_time
from slingr.asset import PathVal


class FileWatcher:
    """Watch modification times of registered files in a thread."""
    def __init__(self, notify, filenames, poll_interval=1.0):
        self._lock = threading.RLock()
        self.notify, self.poll_interval = notify, poll_interval
        self.register_files(filenames)

    def register_files(self, filenames):
        with self._lock:
            self.filenames = sorted(filenames)
            self.mtimes = {}

    def watch(self):
        self.thread = threading.Thread(target=self.poll_thread)
        self.thread.daemon = True  # autodestruct when process exits
        self.thread.start()

    def poll_thread(self):
        while True:
            modified_filenames = self.poll_mtimes()
            if modified_filenames:
                self.notify(modified_filenames)
            self.sleep()

    def sleep(self):
        time.sleep(self.poll_interval)

    def poll_mtimes(self):
        """Return a list of all watched filenames that have been
        updated since the last poll."""
        modified_filenames = []
        with self._lock:
            for filename in self.filenames:
                mtime = modification_time(filename)

                if mtime is None:
                    # File has disappeared?
                    modified_filenames.append(filename)
                else:
                    old_mtime = self.mtimes.get(filename)
                    self.mtimes[filename] = mtime
                    if old_mtime is not None and mtime > old_mtime:
                        modified_filenames.append(filename)

        return modified_filenames


class CobUrlWatcher:
    """I like to watch CobUrls."""
    def __init__(self, notify, coburls):
        self.client_notify, self.coburls = notify, coburls
        # may be dupes; doesn't matter
        self.map = dict((c.abspath, c) for c in coburls)

    def watch(self):
        self.filewatcher = FileWatcher(self.notify, self.map.keys())
        self.filewatcher.watch()

    def notify(self, updated_filenames):
        """Notifies client that watched CobUrls have been modified."""
        updated_coburls = [self.map[f] for f in updated_filenames]
        self.client_notify(updated_coburls)
        return updated_coburls


class PathValMapWatcher:
    """I like to watch PathVals associated with other objects."""
    def __init__(self):
        self.map = defaultdict(list)
        self.coburls = []

    def register(self, key, pathvals, notify):
        for pv in pathvals:
            if isinstance(pv, PathVal):
                self.map[pv.url.key].append((key, notify))
                self.coburls.append(pv.url)

    def watch(self):
        self.watcher = CobUrlWatcher(self.notify, self.coburls)
        self.watcher.watch()

    def notify(self, updated_coburls):
        """Notifies clients that watched CobUrls have been modified."""
        now = datetime.datetime.now()
        for coburl in updated_coburls:
            for key, notify in self.map[coburl.key]:
                notify(key, coburl, now)
