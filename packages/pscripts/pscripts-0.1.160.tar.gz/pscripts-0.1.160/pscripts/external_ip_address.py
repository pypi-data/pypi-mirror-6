#!/usr/bin/env python
import re, sys, shelve, simpledaemon, time, os, yaml, html.parser, urllib.request
import logging as log
from pdb import set_trace
from urllib.error import URLError
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth
import requests
from subprocess import check_output,call


#################################
# ENTRY POINT
def update_ddns_server(updater_urls="/etc/external_ip_updater/urls.yaml", update=True, manual_force_update=False):
    try:
        external_ip = get_ip()
        if external_ip == None:
            log.warn("Unable to determine external IP.  This may be temporary or not.  Verify this warning doesn't persist.")
            return
        log.debug("External IP address {}".format(str(external_ip)))        
        ddns_urls = read_yaml_update_urls(updater_urls)
        for domain, update_url in ddns_urls.items():
            log.debug("For domain: {}, the update url is: {}".format(domain,update_url))
            prev_ext_ip = read_ip_addy(domain)
            changed = ip_addy_changed(external_ip, prev_ext_ip)
            if changed or manual_force_update or periodic_force_update():
                log.debug("IP changed or forcing update.")
                if update or manual_force_update:
                    log.info("Updating domain: {} with IP: {}".format(domain, external_ip))
                    touch_ddns_server(update_url)
                    save_ip_addy(external_ip,domain)
                else:
                    log.debug("Set to NOT update IP.")
            else:
                log.debug("IP not changed, wont DDNS update, or re-cache.")
                log.debug("---------")
    except Exception as e:
        log.warn(e)
        return

def get_refresh_period(updater_urls="/etc/external_ip_updater/urls.yaml"):
    return get_yaml_setting(setting="refresh_period_seconds")

def flush_ip_cache_file():
    log.debug("Removing file: {}".format(ip_cache_file))
    if os.path.isfile(ip_cache_file):
        os.remove(ip_cache_file)

#################################
# HELPERS

def periodic_force_update():
    global periodic_force_update_timer
    now = time.time()
    elapsed_time = now - periodic_force_update_timer
    if elapsed_time > periodic_force_update_period_seconds:
        log.debug("Periodic force update timer elapsed.  Forcing update.")
        periodic_force_update_timer = now
        return True
    return False

def get_periodic_force_update_period():
    return get_yaml_setting(setting="periodic_force_update_period_seconds")

def get_yaml_setting(setting="urls"):
    log.debug("reading file: {}".format(yaml_file))
    f = open(yaml_file)
    url_updater_hash = yaml.load(f)
    log.debug("yaml hash: {}".format(url_updater_hash))
    try:
        return url_updater_hash[setting]
    except KeyError as ke:
        log.warn("key: {} not in file: {}".format(setting, yaml_file))
        return False
    
def ip_addy_changed(external_ip, prev_ext_ip):
    if prev_ext_ip == None:
        return True
    if prev_ext_ip == external_ip:
        return False
    else:
        return True

def save_ip_addy(new_ip, domain):
    ip_updates = shelve.open(ip_cache_file)
    ip_updates[domain] = new_ip
    log.debug("Caching IP address: {}, under domain: {}".format(new_ip, domain))
    ip_updates.close

def read_ip_addy(domain):
    ip_updates = shelve.open(ip_cache_file)
    if ip_updates:
        if not domain in ip_updates:
            return None
        else:
            ip = ip_updates[domain]
            log.debug("Cached IP address: {} retrieved for domain: {}".format(ip, domain))
            return ip 

def touch_ddns_server(url):
    log.debug("touching url: {}".format(url))
    cmd = 'wget {}'.format(url).split()
    log.debug("Issuing command: " + str(cmd))
    resp = call(cmd)

def read_yaml_update_urls(yaml_conf="/etc/external_ip_updater/urls.yaml"):
    urls = get_yaml_setting("urls")
    return urls

def get_ip():
    cmd = "curl icanhazip.com"
    output = "{}".format(check_output(cmd, shell=True).strip().decode("utf-8", "ignore"))
    return output

##########################################
# Settings
#--------------
ip_cache_file = '/tmp/.current_external_ip'
yaml_file = '/etc/external_ip_updater/urls.yaml'
periodic_force_update_timer = time.time()
periodic_force_update_period_seconds = get_periodic_force_update_period()
log_file = get_yaml_setting(setting="logfile")
log_file = log_file if log_file else 'external_ip.logger'
    
#################################
# TESTS

def test_get_ip():
    ip = get_ip()
    log.debug("IP is: {}".format(ip))

def test_get_update_period():
    period = get_refresh_period()
    log.debug( "refresh period: {}".format(period))

def test_update_ip():
    updater_urls = "/etc/external_ip_updater/urls.yaml"
    update_ddns_server(updater_urls, force_update=True)

def test_yaml():
    updater_urls = "/etc/external_ip_updater/urls.yaml"
    ddns_urls = read_yaml_update_urls(updater_urls)
    for domain, update_url in ddns_urls.items():
        print("For domain: {}, use update url: {}".format(domain,update_url))

def test_get_webpage():
    html = get_simple_webpage('http://www.ip-secrets.com/')

def test_logfile_setting():
    print("log file: {}".format(log_file))

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    # set_trace()
    # test_update_ip()
    # test_get_update_period()
    # test_get_ip()
    test_logfile_setting()
    
