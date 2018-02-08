import sqlite3

import os
from django.core.handlers.wsgi import WSGIRequest

from TeacherRating.settings import BASE_DIR


def database_using(func):
    '''
    database装饰器，凡是调用到数据库的请求，均可加上此装饰器以简化操作
    :param func:
    :return:
    '''
    def wrapper(*args, **kwargs):
        find_user = False
        arg_list = list(args)
        new_args = arg_list.copy()
        for arg in arg_list:
            if isinstance(arg, WSGIRequest):
                find_user = True
                conn = sqlite3.connect(os.path.join(BASE_DIR, 'rating.db'))
                cursor = conn.cursor()
                # sqlite为了兼容旧版本，默认不开启外键，因此每次连接时需要手动开启
                cursor.execute("PRAGMA foreign_keys = ON")
                conn.commit()
                new_args.append(cursor)
                break
        result = func(*tuple(new_args), **kwargs)
        if find_user:
            conn.commit()
            cursor.close()
            conn.close()
        return result

    return wrapper