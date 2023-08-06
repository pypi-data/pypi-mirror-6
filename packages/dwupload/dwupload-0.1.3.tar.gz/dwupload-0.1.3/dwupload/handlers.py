from __future__ import print_function
from watchdog.events import PatternMatchingEventHandler
from dwupload.webdav import DemandwareConnection


class DemandwareWebDavHandler(PatternMatchingEventHandler):
    ignore_patterns = ['*.git/*', '*.svn/*', '*.idea/*', '*.DS_Store', '*.tmp', '*.swp', 'Thumbs.db', '*.project/*']

    def __init__(self, watch_path, hostname, username, password, code_version, *args, **kwargs):
        super(DemandwareWebDavHandler, self).__init__(*args, **kwargs)

        self.watch_path = watch_path
        self.conn = DemandwareConnection(hostname, username, password, code_version)

    def _get_normalized_path_segments(self, file_path):
        relative_file_path = file_path.replace(self.watch_path, "")
        normalized_path = relative_file_path.replace("\\", "/").replace("//", "/")
        path_segments = normalized_path.split("/")
        return path_segments

    def _get_normalized_server_path_from_segments(self, path_segments):
        url_normalized_path = "/".join(path_segments)[1:]
        return self.conn.dw_server_path + url_normalized_path

    def _get_server_path(self, file_path):
        path_segments = self._get_normalized_path_segments(file_path)
        return self._get_normalized_server_path_from_segments(path_segments)

    def _get_parent_directory_server_paths(self, file_path):
        path_segments = self._get_normalized_path_segments(file_path)
        server_paths = []

        while path_segments:
            server_paths.append(self._get_normalized_server_path_from_segments(path_segments))
            path_segments.pop()

        return server_paths

    def on_created(self, event):
        server_path = self._get_server_path(event.src_path)

        if event.is_directory:
            if 200 <= self.conn.mkcol(server_path) < 300:
                print("[created] {0}".format(server_path))
        else:
            with open(event.src_path, 'r') as f:
                if 200 <= self.conn.put(server_path, f) < 300:
                    print("[created] {0}".format(server_path))

    def on_deleted(self, event):
        server_path = self._get_server_path(event.src_path)

        if 200 <= self.conn.delete(server_path) < 300:
            print("[deleted] {0}".format(server_path))

    def on_modified(self, event):
        server_path = self._get_server_path(event.src_path)

        if not event.is_directory:
            with open(event.src_path, 'r') as f:
                status_code = self.conn.put(server_path, f)

            if 200 <= status_code < 300:
                print("[modified] {0}".format(server_path))

    def on_moved(self, event):
        server_path = self._get_server_path(event.src_path)
        server_destination_path = self._get_server_path(event.dest_path)

        if not event.is_directory:
            for parent_server_path in self._get_parent_directory_server_paths(event.dest_path):
                status_code = self.conn.mkcol(parent_server_path)
                if 200 <= status_code < 300:
                    print("[created] {0}".format(parent_server_path))
                elif status_code == 405:
                    break

            with open(event.dest_path, 'r') as f:
                if 200 <= self.conn.put(server_destination_path, f) < 300:
                    print("[moved] {0} > {1}".format(server_path, server_destination_path))

            if 200 <= self.conn.delete(server_path) < 300:
                print("[deleted] {0}".format(server_path))
        else:
            if 200 <= self.conn.put(server_destination_path) < 300:
                print("[moved] {0} > {1}".format(server_path, server_destination_path))

            if 200 <= self.conn.delete(server_path) < 300:
                print("[deleted] {0}".format(server_path))
