import requests
from pprint import pprint
import json

"""
https://docs.nextcloud.com/server/12/admin_manual/configuration_user/user_provisioning_api.html
https://docs.nextcloud.com/server/12/developer_manual/core/externalapi.html
"""

# config start
admin_name_password = "admin:password"
http = "https://"
host_port = "my.domain.ntu.edu.tw:444"
user_list = ['name']
password = "password"
# config end

header = {
    "OCS-APIRequest": "true",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

def addUser(name):
    resp = requests.post(http + admin_name_password + '@' + host_port + "/ocs/v1.php/cloud/users",
                         data={'userid': name, 'password': password},
                         headers=header)
    pprint(resp.json())
    return True

def setStorage(name):
    return {
        "mount_point": "\/share_" + name,
        "storage": "\\OC\\Files\\Storage\\Local",
        "authentication_type": "null::null",
        "configuration": {
            "datadir": "/external_data/" + name
        },
        "options": {
            "encrypt": True,
            "previews": True,
            "enable_sharing": False,
            "filesystem_check_changes": 1,
            "encoding_compatibility": False
        },
        "applicable_users": [
            name
        ],
        "applicable_groups": []
    }

for i in user_list:
    addUser(i)
storages = [setStorage(i) for i in user_list]
json.dump(storages, open("nextcloud/my_storages.json", "w"))

"""
This file should import like this
php occ files_external:import my_storges.json
"""
