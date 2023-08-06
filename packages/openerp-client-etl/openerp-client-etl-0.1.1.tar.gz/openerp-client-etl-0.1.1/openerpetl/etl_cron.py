#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import openerplib
import sys
from openerpetl import oer_etl

def run(hostname,port,database,login,password,log_print=True):
    oer_local = openerplib.get_connection(hostname=hostname,
                                     port=port, database=database,
                                     login=login, password=password)
    etl = oer_etl(oer_local, log_print=log_print)
    for job in etl.get_jobs():
        oer_local.get_model('etl.job').action_start([job['id']])
        for row in etl.get_rows(job['id']):
            new_id = etl.create(job['id'], etl.get_values(job['id'],row), pk=row.get('pk',False))
        oer_local.get_model('etl.job').action_done([job['id']]) 
    print "Finish etl_cron"