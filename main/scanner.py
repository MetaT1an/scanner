import requests
import json
import time
import threading

import settings

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Scanner(object):
    def __init__(self):
        self.base_url = settings.base_url
        self.username = settings.user_name
        self.password = settings.password
        self.scan_id = None
        self.token = None

    def get_header(self):
        if not self.token:
            session_api = self.base_url + "/session"
            user_info = {
                'username': self.username,
                'password': self.password
            }
            r = requests.post(session_api, data=user_info, verify=False)
            if r.status_code == 200:
                self.token = r.json()['token']
            else:
                print("[login] login error!")
                return None

        header = {      # generate header info
            'X-Cookie': 'token={0}'.format(self.token),
            'content-type': 'application/json'
        }
        return header

    def scan_status(self):
        status_api = self.base_url + "/scans/{scan_id}".format(scan_id=self.scan_id)
        _status = False

        while True:
            time.sleep(10)
            r = requests.get(status_api, headers=self.get_header(), verify=False)

            if r.status_code == 200:
                status = r.json()['info']['status']
                print("[scan status] %s" % status)

                if status == "completed":
                    _status = True
                    break

        return _status

    def scan_info(self, info_dict):
        details_api = self.base_url + "/scans/{0}".format(self.scan_id)
        r = requests.get(details_api, headers=self.get_header(), verify=False)

        # to generate an info dict via response
        hosts_dict, detail_dict, vuls_list = r.json()['hosts'][0], r.json()['info'], r.json()['vulnerabilities']

        info_dict['vulns'], info_dict['details'] = {}, {}
        info_dict['vulns']['list'] = []

        info_dict['vulns']['critical_num'] = hosts_dict['critical']
        info_dict['vulns']['high_num'] = hosts_dict['high']
        info_dict['vulns']['medium_num'] = hosts_dict['medium']
        info_dict['vulns']['low_num'] = hosts_dict['low']
        info_dict['vulns']['info_num'] = hosts_dict['info']

        for vul in vuls_list:
            info_dict['vulns']['list'].append({
                'pluginname': vul['plugin_name'],
                'severity': vul['severity'],
                'pluginset': vul['plugin_family'],
                'count': vul['count']
            })

        info_dict['details']['name'] = detail_dict['name']
        info_dict['details']['status'] = detail_dict['status']

        # generate time information
        start_time, end_time = detail_dict['scan_start'], detail_dict['scan_end']
        elapse = end_time - start_time

        info_dict['details']['start'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_time))
        info_dict['details']['end'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(end_time))
        info_dict['details']['elapse'] = "{0}min {1}s".format(elapse // 60, elapse % 60)
        info_dict['details']['target'] = detail_dict['targets']

        print("[scan_info] info ready")

    def scan_report(self, report_dict):

        file_api = self.base_url + "/scans/{0}/export".format(self.scan_id)
        format_data = {
            'format': 'html',
            'chapters': 'vuln_hosts_summary;vuln_by_host'
        }
        
        r = requests.post(file_api, data=json.dumps(format_data), headers=self.get_header(), verify=False)
        file_id = r.json()['file']

        time.sleep(2)       # need some time to generate the report

        report_url = self.base_url + "/scans/{0}/export/{1}/download".format(self.scan_id, file_id)
        report_file = requests.get(report_url, headers=self.get_header(), verify=False)

        report_dict['report'] = report_file.content.decode("utf8")

        print("[scan_report] report ready")

    """
    name: name of the scan
    target: the ip to scan
    description: the description of the scan
    @:return scan info dict to store in redis
    """
    def scan_task(self, name, target, policy_name, description=None):
        create_api = self.base_url + "/scans"

        # 1. get policy id via given policy name
        policy_id = self.get_policy_id(policy_name)

        # 2. generate request data
        data = {
            'uuid': "ad629e16-03b6-8c1d-cef6-ef8c9dd3c658d24bd260ef5f9e66",
            'settings': {
                'name': name,
                'description': description,
                'enabled': False,
                'text_targets': target,
                'launch_now': True,
                'policy_id': policy_id
            }
        }

        # 3. create a scan task and launch immediately
        r = requests.post(create_api, data=json.dumps(data), headers=self.get_header(), verify=False)
        self.scan_id = r.json()['scan']['id']
        print("[scan task submitted]id: %s" % self.scan_id)

        # 4. listen until scan completed
        info_dict, report_dict = {}, {}
        if self.scan_status():
            report_thread = threading.Thread(target=self.scan_report, args=(report_dict,))
            report_thread.start()   # might take longer time

            info_thread = threading.Thread(target=self.scan_info, args=(info_dict,))
            info_thread.start()

            info_thread.join()
            report_thread.join()

            self.token = None

        return dict(info_dict, **report_dict)       # merge into one

    def get_policy_id(self, policy_name):
        policy_id = None

        policy_api = self.base_url + "/policies"
        r = requests.get(policy_api, headers=self.get_header(), verify=False)
        
        policy_list = r.json()['policies']
        for policy in policy_list:
            if policy['name'] == policy_name:
                policy_id = policy['id']

        return policy_id


# if __name__ == '__main__':
#     scanner = Scanner()
#     data = scanner.scan_task("v1.0", "192.168.2.10", "ubuntu", "test")
#     # scanner.plugin_test()
#     # print(data['vulns'])
