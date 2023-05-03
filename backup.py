import os
import requests
import argparse
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Set up log for duplicate stdout and backup file
logging.basicConfig(filename='backup.log', format='%(asctime)s : %(levelname)-8s %(message)s')
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

# Parse command line
parser = argparse.ArgumentParser(description='Backup VScale scalet')
parser.add_argument('-t', '--token', help='API token')
parser.add_argument('-s', '--scalet', help='scalet id', required=True)
parser.add_argument('-n', '--name', help='Prefix for backup name')
parser.add_argument('-c', '--count', help='Count backups', default=1)

args = parser.parse_args()

# Set token from .env or command line
token = args.token or os.environ.get('VSCALE_TOKEN')
if not token:
    log.error('Token not specified. Set VSCALE_TOKEN in .env or in command arg --token')
    sys.exit(1)

# Setup backup name
backup_prefix = (args.name or args.scalet + '_auto')
backup_name = backup_prefix + '_' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# Make request to VScale API
def api_request(method, url, json = {}):
    response = requests.request(
        method,
        'https://api.vscale.io/v1/' + url,
        headers={'X-Token': token},
        json=json
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        log.error("Failed request %s %s %s", url, err.response.status_code, err.response.content)
        return False

    return response.json()

log.info('Make backup %s for scalet %s', backup_name, args.scalet)
response = api_request('post', 'scalets/{0}/backup'.format(args.scalet), json={'name': backup_name })
if response and 'id' in response:
    log.info('Backup queued with id %s', response['id'])
else:
    log.error('Failed make backup')
    sys.exit(1)

# Remove old backups
log.info('Remove old backups')
backups = api_request('get', 'backups')
if not backups:
    log.error('Failed get backups')
    sys.exit(1)

backups = list(filter(lambda item: item['status'] == 'finished' and str(item['scalet']) == args.scalet and not item['is_deleted'] and item['name'].startswith(backup_prefix), backups))
log.info('Get %d backups for scalet', len(backups))
backups = sorted(backups, key=lambda d: d['created'])

# One backup is created, so if we want keep 1 backup we need remove all backups + one is queue for create
backups_for_remove = backups[:len(backups) - args.count - 1]
if len(backups_for_remove):
    for backup in backups_for_remove:
        log.info('Remove backup %s %s', backup['name'], backup['id'])
        api_request('delete', 'backups/{0}'.format(backup['id']))
else:
    log.info('No backups for remove')
