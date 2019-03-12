import requests
import json
import settings
import time

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
            api = self.base_url + "/session"
            user_info = {
                'username': self.username,
                'password': self.password
            }
            r = requests.post(api, data=user_info, verify=False)
            if r.status_code == 200:
                self.token = r.json()['token']
            else:
                print("[login] login error!")
                return

        header = {      # generate header info
            'X-Cookie': 'token={0}'.format(self.token),
            'content-type': 'application/json'
        }
        return header

    def scan_status(self):
        status_api = self.base_url + "/scans/{scan_id}".format(scan_id=self.scan_id)

        while True:
            time.sleep(10)
            r = requests.get(status_api, headers=self.get_header(), verify=False)

            if r.status_code == 200:
                status = r.json()['info']['status']
                print("[scan status]", status)

                if status == "completed":
                    return True
                else:
                    continue

        return False

    def save_to_redis(self):
        # 凑成一个字典，返回
        details_api = self.base_url + "/scans/{0}".format(self.scan_id)
        r = requests.get(details_api, headers=self.get_header(), verify=False)

        hosts_dict = r.json()['hosts'][0]
        critical_num = hosts_dict['critical']
        high_num = hosts_dict['high']
        medium_num = hosts_dict['medium']
        low_num = hosts_dict['low']
        info_num = hosts_dict['info']
        print(critical_num, high_num, medium_num, low_num, info_num)

        print("[redis_thread] sava to redis")
        pass

    def html_report(self):

        file_api = self.base_url + "/scans/{0}/export".format(self.scan_id)
        format_data = json.dumps({
            'format': 'html',
            'chapters': 'vuln_hosts_summary;vuln_by_host'
            })
        
        r = requests.post(file_api, data=format_data, headers=self.get_header(), verify=False)
        file_id = r.json()['file']

        # print(file_id)
        time.sleep(2)       # need some time to generate the report

        report_url = self.base_url + "/scans/{0}/export/{1}/download".format(self.scan_id, file_id)
        report_file = requests.get(report_url, headers=self.get_header(), verify=False)

        # to write the content into a file
        with open("report_{0}.html".format(self.scan_id), "wb") as report:
            report.write(report_file.content)

        print("[report_thread]report downloaded")

    """
    name: name of the scan
    target: the ip to scan
    description: the description of the scan
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

        # create a scan task and launch immediately
        r = requests.post(create_api, data=json.dumps(data), headers=self.get_header(), verify=False)
        scan_id = r.json()['scan']['id']

        self.scan_id = scan_id
        print("[scan task submitted]id: %s" % scan_id)

        if self.scan_status():
            import threading
            redis_thread = threading.Thread(target=self.save_to_redis)
            redis_thread.start()
            # self.save_to_redis()      # redis
            # self.html_report()        # report
            report_thread = threading.Thread(target=self.html_report)
            report_thread.start()

    def get_policy_id(self, policy_name):
        policy_id = None

        policy_api = self.base_url + "/policies"
        r = requests.get(policy_api, headers=self.get_header(), verify=False)
        
        policy_list = r.json()['policies']
        for policy in policy_list:
            if policy['name'] == policy_name:
                policy_id = policy['id']

        return policy_id


scanner = Scanner()
scanner.scan_task("2019-3-11 22:32:34", "192.168.2.10", "ubuntu", "launch from console")
# scanner.plugin_test()
# scanner.save_to_redis()
