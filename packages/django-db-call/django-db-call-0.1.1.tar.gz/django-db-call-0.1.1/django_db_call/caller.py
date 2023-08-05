# -*- coding: utf-8 -*-
"""
django-db-call

Copyright (c) 2014, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
from argparse import ArgumentParser

from first import first


def _from_mysql_call(args, **kwargs):
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-h', '--host', dest='host', default='')
    parser.add_argument('-u', '--user', dest='user', default='')
    parser.add_argument('-p', '--password', dest='password', default='')
    parser.add_argument('-D', dest='name', default='')
    parser.add_argument('-P', '--port', dest='port', default='')
    parser.add_argument('db_name', nargs='?', default='')

    args = parser.parse_args(args)

    db_name = first([args.name, args.db_name], default='')
    db_dict = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': db_name,
        'USER': args.user,
        'PASSWORD': args.password,
        'HOST': args.host,
        'PORT': args.port,
    }

    if kwargs:
        db_dict['OPTIONS'] = kwargs

    return db_dict


def _from_psql_call(args, password='', **kwargs):
    parser = ArgumentParser(add_help=False)

    parser.add_argument('-d', '--dbname', dest='name', default='')
    parser.add_argument('-h', '--host', dest='host', default='')
    parser.add_argument('-p', '--port', dest='port', default='')
    parser.add_argument('-U', '--username', dest='user', default='')
    parser.add_argument('db_name', nargs='?', default='')

    args = parser.parse_args(args)

    db_name = first([args.name, args.db_name], default='')
    db_dict = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': db_name,
        'USER': args.user,
        'PASSWORD': password,
        'HOST': args.host,
        'PORT': args.port,
    }

    if kwargs:
        db_dict['OPTIONS'] = kwargs

    return db_dict


def from_call(call, connection='default', **kwargs):
    args = call.split()

    if not args:
        raise ValueError

    if args[0] == 'mysql':
        db_dict = _from_mysql_call(args[1:], **kwargs)
    elif args[0] == 'psql':
        db_dict = _from_psql_call(args[1:], **kwargs)
    else:
        raise ValueError

    return {connection: db_dict}


def from_calls(calls):
    databases = {}

    for call in calls:
        args = []
        kwargs = {}

        for arg in call:
            if isinstance(arg, dict):
                kwargs.update(**arg)
            else:
                args.append(arg)

        database = from_call(*args, **kwargs)
        databases.update(**database)
    return databases
