from git import *
import os
import time
import main
from fileio.config import parse_config
from log import setup_log, log

def daemonize(squadron_dir, config_file, polltime, repo, loglevel):
    """
    Runs squadron every polltime minutes.

    Keyword arguments:
        squadron_dir -- squadron directory
        config_file -- config file or None for defaults
        polltime -- minutes to sleep in between runs
        repo -- source code for the squadron_dir for updating
        loglevel -- how much to log
    """

    setup_log(loglevel)

    parsed_config = parse_config(config_file)

    if not polltime:
        polltime = int(parsed_config['polltime'])

    if not os.path.exists(squadron_dir):
        repo = Repo.clone_from(repo, squadron_dir)
    else:
        repo = Repo(squadron_dir)

    while(True):
        git = repo.git

        log.debug('Git checkout: ' + git.checkout('master'))
        log.debug('Git pull: ' + git.pull('--rebase'))

        if not main.go(squadron_dir, config_file=config_file):
            log.error('Squadron had an error')

        time.sleep(polltime)
