#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import pyodbc
import openerplib
import psycopg2
import logging
import decimal
import sys, traceback
_logger = logging.getLogger(__name__)

class oer_etl(object):
    
    local = None
    __jobs = {}
    __servers = {}
    __value_mapping = {}
    log_print = False
    
    def __init__(self, oer_local, log_print=False):
        self.local = oer_local
        self.__jobs = {}
        self.__servers = {}
        self.__value_mapping = {}
        self.log_print = log_print
    
    def get_jobs(self):
        job_obj = self.local.get_model('etl.job')
        job_ids = job_obj.search([('state','=','ready'),('type','=','batch')])
        res = []
        for job_id in job_ids:
            job = self.get_job(job_id)
            self.__jobs[job_id] = job
            res.append(job)
        _logger.info('Geting %s Jobs',len(job_ids))
        return res
    
    def get_job(self, job_id):
        res = False
        if self.__jobs.has_key(job_id):
            res = self.__jobs[job_id]
        else:
            job_obj = self.local.get_model('etl.job')
            map_obj = self.local.get_model('etl.mapping.job')
            res = job_obj.read([job_id])[0]
            res['mappings'] = []
            for map_id in res['mapping_ids']:
                map = map_obj.read([map_id])[0]
                res['mappings'].append(map)
            self.__jobs[job_id] = res
        return res
    
    def get_server(self, server_id):
        res = False
        if self.__servers.has_key(server_id):
            res = self.__servers[server_id]
        else:
            server_obj = self.local.get_model('etl.server')
            res = server_obj.read([server_id])[0]
            self.__servers[server_id] = res
        return res
    
    def get_connection(self, server_id):
        conn = False
        server = self.get_server(server_id)
        if server['type'] == 'xmlrpc':
            conn = openerplib.get_connection(hostname=server['host'],
                                             port=server['port'], database=server['database'],
                                             login=server['login'], password=server['password'])
        elif server['type'] == 'odbc':
            conn = pyodbc.connect(server['str_connection'])
        elif server['type'] == 'postgresql':
            conn = psycopg2.connect(server['str_connection'])
        _logger.debug('Server Connection %s',conn)
        return conn
    
    def get_rows(self, job_id, localdict={}):
        job = self.get_job(job_id)
        conn = self.get_connection(job['src_server_id'][0])
        cr = conn.cursor()
        if job['query_begin']:
            cr.execute(job['query_begin']%localdict)
        cr.execute(job['query']%localdict)
        rows = cr.fetchall()
        row_description = cr.description
        if job['query_end']:
            cr.execute(job['query_end']%localdict)
        rows = [dict([(type(col) is tuple and col[0] or col.name,r[i]) for i,col in enumerate(row_description)]) for r in rows]
        default_value = {}
        if job['row_default_value']:
            default_value = eval(job['row_default_value']%localdict)
        res = []
        for r in rows:
            d = default_value.copy()
            for x,y in r.iteritems():
                if y is None:
                    y = False
                if type(y) is decimal.Decimal:
                    y = float(y)
                d[x] = y
            res.append(d)
        cr.close()
        conn.close()
        return res
    
    def get_value_mapping(self, mapping_id, val, job_id):
        if not self.__value_mapping.has_key(mapping_id):
            mapping_obj = self.local.get_model('etl.mapping')
            line_obj = self.local.get_model('etl.mapping.line')
            mapping = mapping_obj.read([mapping_id])[0]
            job = self.get_job(job_id)
            self.__value_mapping[mapping_id] = {}
            for line in line_obj.read(mapping['line_ids']):
                line_value = False
                if line.get('map_ref'):
                    line_value = int(line['map_ref'].split(',')[1])
                elif line.get('map_id'):
                    line_value = line['map_id']
                elif line.get('map_xml_id'):
                    mod_xml = line['map_xml_id'].split('.')
                    if len(mod_xml) == 2:
                        model_data_obj = self.get_connection(job['dst_server_id'][0]).get_model('ir.model.data')
                        line_value = model_data_obj.get_object(mod_xml[0],mod_xml[1])
                elif line.get('map_char'):
                    line_value = line['map_char']
                self.__value_mapping[mapping_id][line['name']] = line_value
        val = self.__value_mapping[mapping_id].get(val,val)
        return val
        
    def get_values(self, job_id, row):
        res = {}
        job = self.get_job(job_id)
        for map in job['mappings']:
            val = eval(map['value'],row)
            if map['mapping_id']:
                val = self.get_value_mapping(map['mapping_id'][0],val,job_id)
            
            if map['field_type'] == 'many2one':
                val_obj = self.get_connection(job['dst_server_id'][0]).get_model(map['field_relation'])
                if map['name_search']:
                    val_ids = val_obj.search(eval(map['name_search'],row))
                    if val_ids:
                        val = val_ids[0]
                if type(val) is not int:
                    val_ids = val_obj.search([('name','=',val)])
                    if val_ids:
                        val = val_ids[0]
                    elif map['per_call_job_id']:
                        per_call_job = self.get_job(map['per_call_job_id'][0])
                        if per_call_job['state'] == 'ready':
                            val = self.create_from_value(map['per_call_job_id'][0], val, row)
            res[map['field_name']] = val
        return res
    
    def get_logs(self, job_id, pk=None, id=None, level=None):
        log_obj = self.local.get_model('etl.log')
        domain = [('job_id','=',job_id)]
        if pk:
            domain.append(('pk','=',pk))
        if id:
            domain.append(('model_id','=',id))
        if level:
            domain.append(('level','=',level))
        job = self.get_job(job_id)
        return log_obj.search(domain)
        
    def create_from_value(self, job_id, value, row):
        localdict = row.copy()
        localdict['etl_row_value'] = value
        rows = self.get_rows(job_id, localdict)
        if rows:
            value = self.create(job_id, self.get_values(job_id, rows[0]), pk=rows[0].get('pk',False))
        else:
            self.log(job_id, "%s Not Found on source server %s"%(value,self.get_job(job_id)['src_server_id']), level='error')
        return value
    
    def create(self, job_id, values, pk=False):
        job = self.get_job(job_id)
        oer = self.get_connection(job['dst_server_id'][0])
        load_model = oer.get_model(job['load_model'])
        if job['reprocess'] and pk:
            model_ids = []
            for log in self.get_logs(job_id,pk,level='info'):
                if log['id']:
                    model_ids.append(log['id'])
            if model_ids:
                model_ids = load_model.search([('id','in',model_ids)])
            if model_ids:
                return model_ids[0]
        new_id = False
        try:
            new_id = load_model.create(values)
        except Exception as e:
            self.log(job['id'],'Unexpected Error: %s'%e, stack=sys.exc_info(), level='error', pk=pk)
        else:
            self.log(job['id'],'Ok', id=new_id, pk=pk)
        return new_id
    
    def log(self, job_id, msg, level=None, id=None, pk=None, stack=None):
        msg = msg.replace('\\\\n','\\n')
        if self.log_print: to_print = "Job: %s - Message:%s"%(job_id,msg.replace('\\\\n','\\n'))
        log_obj = self.local.get_model('etl.log')
        job = self.get_job(job_id)
        vals = {'job_id': job_id,'log': msg, 'model': job['load_model']}
        if level:
            vals['level'] =  level
        if id:
            vals['model_id'] = id
            if self.log_print: to_print += " - ID:%s"%id
        if pk:
            vals['pk'] = pk
            if self.log_print: to_print += " - PK:%s"%pk 
        if stack:
            exc_type, exc_value, exc_traceback = stack
            stack = traceback.format_exception(exc_type, exc_value, exc_traceback)
            vals['traceback'] = ''.join(stack)
        if self.log_print: print to_print
        return log_obj.create(vals)
    