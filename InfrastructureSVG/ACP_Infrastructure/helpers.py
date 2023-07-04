import json
import re

import requests as req


def get_sr_version(acp_name):
    resp = req.get(f"https://{acp_name}/swagger/index.html", verify=False)
    json_pattern = '(?=\\[\\{\\"url\\"\\:)(.*)(?=\\,\"deepLinking)'
    output = re.findall(json_pattern, resp.text)
    multiple_srs = []
    if len(output) == 1:
        json_data = json.loads(output[0])
        for sr in json_data:
            sr_name = sr["name"]
            if re.match(r'\d{2}\.\d{1,2}', sr_name) and sr_name != '20.5':
                multiple_srs.append(sr_name)

    return max(multiple_srs, default=None)
