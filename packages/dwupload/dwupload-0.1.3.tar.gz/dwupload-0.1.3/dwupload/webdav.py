import requests


class DemandwareConnection(object):
    def __init__(self, hostname, username, password, code_version):
        self.dw_hostname = hostname
        self.dw_code_version = code_version
        self.dw_credentials = (username, password)

        self.dw_server_path = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}/" \
            .format(self.dw_hostname, self.dw_code_version)

    def get(self, url):
        r = requests.get(url=url, auth=self.dw_credentials, verify=False)
        return r.status_code

    def put(self, url, file_data=None):
        if file_data:
            r = requests.put(url=url, auth=self.dw_credentials, data=file_data.read(),
                             headers={'content-type': 'text/plain'},
                             verify=False)
        else:
            r = requests.put(url=url, auth=self.dw_credentials, verify=False)
        return r.status_code

    def delete(self, url):
        r = requests.delete(url, auth=self.dw_credentials, verify=False)
        return r.status_code

    def mkcol(self, url):
        r = requests.request("MKCOL", url, auth=self.dw_credentials, verify=False)
        return r.status_code

    def move(self, url, destination_url):
        headers = {"Destination": destination_url}
        r = requests.request('MOVE', url, auth=self.dw_credentials, headers=headers, verify=False)
        return r.status_code

    def copy(self, url, destination_url):
        headers = {"Destination": destination_url}
        r = requests.request('COPY', url, auth=self.dw_credentials, headers=headers, verify=False)
        print(r.status_code)

    def test_connection(self):
        return self.get(self.dw_server_path)