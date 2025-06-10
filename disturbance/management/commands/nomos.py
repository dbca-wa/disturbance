
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import requests

import itertools

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch nomos data'

    def handle(self, *args, **options):
        #logger.info('Running command {}')
        import ipdb; ipdb.set_trace()
        
        logger.info('Running command {}'.format(__name__))

        errors = []
        updates = []
        
        my_url='{}/token'.format(settings.NOMOS_URL)
        
        username= settings.NOMOS_USERNAME
        passwd= settings.NOMOS_PASSWORD
        kingdom_id=5

        data1=[{'grant_type': 'password',
        'scope': 'READER',
        'username': username,
        'password': passwd }]
        taxon_names=[]
        #logger.info('username: {} Password: {}'.format(username, passwd))

        try:
            res=requests.post(url=my_url, data=data1[0])
            if res.status_code==200:
                r=res.json()
                r['access_token']
                token='{} {}'.format(r['token_type'], r['access_token'])
                logger.info('Access token {}'.format(token))
                
                taxon_url='{}/v1/taxon_names'.format(settings.NOMOS_URL)
                taxon_res=requests.get(taxon_url, headers={'Authorization': token})
                tres=taxon_res.json()
                #logger.info('Taxon data:{} '.format(tres))
                try:
                    for t in tres:
                        taxon_names.append(t['canonical_name'])
                        updates.append(t['taxon_name_id'])
                    print(taxon_names)
                except Exception as e:
                    err_msg = 'Taxon failed'
                    logger.error('{}\n{}'.format(err_msg, str(e)))
                    errors.append(err_msg)
            else:
                err_msg = 'Login failed with status code {}'.format(res.status_code)
                #logger.error('{}\n{}'.format(err_msg, str(e)))
                logger.error('{}'.format(err_msg))
                errors.append(err_msg)
        except Exception as e:
            err_msg = 'Error at the end'
            logger.error('{}\n{}'.format(err_msg, str(e)))
            errors.append(err_msg)


        cmd_name = __name__.split('.')[-1].replace('_', ' ').upper()
        err_str = '<strong style="color: red;">Errors: {}</strong>'.format(len(errors)) if len(errors)>0 else '<strong style="color: green;">Errors: 0</strong>'
        msg = '<p>{} completed. Errors: {}. IDs updated: {}.</p>'.format(cmd_name, err_str, updates)
        logger.info(msg)
        print(msg) # will redirect to cron_tasks.log file, by the parent script




