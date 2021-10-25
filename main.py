import requests
import json
import logging

with open('config.json') as config_file:
    config = json.load(config_file)

header_data = config["header"]
zones = config["zone_data"]
ip_api = config["ip_api_url"]

logging.basicConfig(filename='dns_log.txt', encoding='utf-8', level=logging.INFO)


def get_public_ip(ip_api_url):
    try:
        public_ip = requests.get(ip_api_url)
        public_ip.raise_for_status()
        public_ip = public_ip.text
        return str(public_ip)

    except Exception as e:
        raise SystemExit(e)


def get_record_ip(zone, fqdn):
    r = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records?&name={fqdn}",
        headers=header_data
    )
    return r.json()


def update_record(zone, fqdn, ip, record_id):
    payload = {
        "type": "A",
        "name": f"{fqdn}",
        "content": f"{ip}",
        "ttl": 1,
        "proxied": True

    }
    r = requests.put(
        f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/{record_id}",
        headers=header_data,
        json=payload
    )
    return r.json()

def create_record(zone, fqdn, ip):
    payload = {
        "type": "A",
        "name": f"{fqdn}",
        "content": f"{ip}",
        "ttl": 1,
        "proxied": True

    }
    r = requests.post(
        f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/",
        headers=header_data,
        json=payload
    )
    return r.json()


if __name__ == '__main__':
    current_ip = get_public_ip(ip_api)

    for zone in zones:
        check = get_record_ip(zone["zone_id"], zone['name'])
        print(check)
        if len(check['result']) > 0:
            if check['result'][0]['content'] != current_ip:
                update = update_record(zone["zone_id"], zone["name"], current_ip, check["result"][0]["id"])
                logging.warning('IP CHANGE DETECTED')
                logging.info(update)
        else:
            create = create_record(zone["zone_id"], zone["name"], current_ip)
            logging.warning('RECORD NOT EXIST - CREATING')
            logging.info(create)

