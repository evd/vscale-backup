## Setup

```shell
git clone --depth 1 --single-branch https://github.com/evd/vscale-backup.git
cd vscale-backup
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Configure .env

```shell
cp .env.example .env
nano .env
```

## Add to cron

```shell
0 0 * * * cd {path_to}/vscale-backup/ && venv/bin/python3 backup.py --scalet {id} --name {name}-auto
```

## Options


| Option                     | Description                                                                          |
|----------------------------|--------------------------------------------------------------------------------------|
| -t TOKEN, --token TOKEN    | API token. Get it in account panel. Can be optional if set in .env file              |
| -s SCALET, --scalet SCALET | Scalet ID                                                                            |
| -n NAME, --name NAME       | Prefix for backup name. When backup added current datetime to each backup file       |
| -c COUNT, --count COUNT    | Count backups. Default 1. If backups more than count old backup with {name}* removed |
