import functools
import csv
import cStringIO
import json
import re
from explorer import app_settings
from django.db import connection, models


## SQL Specific Things

def passes_blacklist(sql):
    clean = functools.reduce(lambda sql, term: sql.upper().replace(term, ""), app_settings.EXPLORER_SQL_WHITELIST, sql)
    return not any(write_word in clean.upper() for write_word in app_settings.EXPLORER_SQL_BLACKLIST)


def execute_query(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor


def execute_and_fetch_query(sql):
    cursor = execute_query(sql)
    headers = [d[0] for d in cursor.description]
    data = [[x.encode('utf-8') if type(x) is unicode else x for x in list(r)] for r in cursor.fetchall()]
    return headers, data, None


def schema_info():
    ret = []
    for app in [a for a in models.get_apps() if a.__package__ not in app_settings.EXPLORER_SCHEMA_EXCLUDE_APPS]:
        for model in models.get_models(app):
            friendly_model = "%s -> %s" % (model._meta.app_label, model._meta.object_name)
            cur_app = (friendly_model, str(model._meta.db_table), [])
            for f in model._meta.fields:
                cur_app[2].append((f.get_attname_column()[1], f.get_internal_type()))
            ret.append(cur_app)
    return ret


def param(name):
    bracket = app_settings.EXPLORER_PARAM_TOKEN
    return "%s%s%s" % (bracket, name, bracket)


def swap_params(sql, params):
    p = params.items() if params else {}
    for k, v in p:
        sql = sql.replace(param(k), str(v))
    return sql


def extract_params(text):
    regex = re.compile("\$\$([a-zA-Z0-9_|-]+)\$\$")
    params = re.findall(regex, text)
    return dict(zip(params, ['' for i in range(len(params))]))


def write_csv(headers, data):
    csv_report = cStringIO.StringIO()
    writer = csv.writer(csv_report)
    writer.writerow(headers)
    map(lambda row: writer.writerow(row), data)
    return csv_report.getvalue()


## Helpers
def shared_dict_update(target, source):
    for k_d1 in target:
        if k_d1 in source:
            target[k_d1] = source[k_d1]
    return target


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except ValueError:
        return default


def safe_json(val):
    try:
        return json.loads(val)
    except ValueError:
        return None


def get_int_from_request(request, name, default):
    val = request.GET.get(name, default)
    return safe_cast(val, int, default) if val else None


def get_json_from_request(request, name):
    val = request.GET.get(name, None)
    return safe_json(val) if val else None


def url_get_rows(request):
    return get_int_from_request(request, 'rows', app_settings.EXPLORER_DEFAULT_ROWS)


def url_get_query_id(request):
    return get_int_from_request(request, 'query_id', None)


def url_get_params(request):
    return get_json_from_request(request, 'params')


## Testing helpers (from http://stackoverflow.com/a/3829849/221390
class AssertMethodIsCalled(object):
    def __init__(self, obj, method):
        self.obj = obj
        self.method = method

    def called(self, *args, **kwargs):
        self.method_called = True
        self.orig_method(*args, **kwargs)

    def __enter__(self):
        self.orig_method = getattr(self.obj, self.method)
        setattr(self.obj, self.method, self.called)
        self.method_called = False

    def __exit__(self, exc_type, exc_value, traceback):
        assert getattr(self.obj, self.method) == self.called, "method %s was modified during assertMethodIsCalled" % self.method

        setattr(self.obj, self.method, self.orig_method)

        # If an exception was thrown within the block, we've already failed.
        if traceback is None:
            assert self.method_called, "method %s of %s was not called" % (self.method, self.obj)