#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
#=============================================================================
#
#     FileName: run_svdog.py
#         Desc: 当supervisor发现某些进程有问题的时候，要记录下来或者发送邮件
#
#       Author: dantezhu
#        Email: dantezhu@qq.com
#     HomePage: http://www.vimer.cn
#
#      Created: 2013-07-29 16:37:24
#      History:
#               0.0.1 | dantezhu | 2013-07-29 16:37:24 | init
#               0.0.2 | dantezhu | 2013-12-13 10:00:07 | use -d
#               0.0.3 | dantezhu | 2013-12-13 10:00:07 | 升级到argparse
#               0.0.4 | dantezhu | 2013-12-13 10:00:07 | 捕获KeyboardInterrupt
#               0.1.4 | dantezhu | 2013-12-23 15:08:07 | 开源
#
#=============================================================================
"""

import sys
sys.path.insert(0, '../../')

import argparse
import os.path as op
import logging
import logging.config
import svdog
from svdog import SVDog


# 日志
# 为了保证邮件只有在正式环境发送
class RequireDebugOrNot(logging.Filter):
    _need_debug = False

    def __init__(self, need_debug, *args, **kwargs):
        super(RequireDebugOrNot, self).__init__(*args, **kwargs)
        self._need_debug = need_debug
        
    def filter(self, record):
        return debug if self._need_debug else not debug


FILE_MODULE_NAME = op.splitext(op.basename(__file__))[0]

LOG_FILE_PATH = "/tmp/svdog.log"

LOG_FORMAT = '\n'.join((
    '/' + '-' * 80,
    '[%(levelname)s][%(asctime)s][%(process)d:%(thread)d][%(filename)s:%(lineno)d %(funcName)s]:',
    '%(message)s',
    '-' * 80 + '/',
))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'standard': {
            'format': LOG_FORMAT,
        },
    },

    'filters': {
        'require_debug_false': {
            '()': RequireDebugOrNot,
            'need_debug': False,
        },
        'require_debug_true': {
            '()': RequireDebugOrNot,
            'need_debug': True,
        },
    },

    'handlers': {
        'flylog': {
            'level': 'CRITICAL',
            'class': 'flylog.FlyLogHandler',
            'formatter': 'standard',
            'source': 'svdog',
        },
        'rotating_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['require_debug_true'],
        },
    },

    'loggers': {
        'default': {
            'handlers': ['console', 'rotating_file', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'svdog': {
            'handlers': ['console', 'rotating_file', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}


debug = False
logger = logging.getLogger('default')

 
def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--process', help='process name', action='append')
    parser.add_argument('-d', '--debug', default=False, help='debug mode', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%s' % svdog.__version__)
    return parser


def configure_logging():
    logging.config.dictConfig(LOGGING)

 
def main():
    global debug

    configure_logging()

    args = build_parser().parse_args()

    debug = args.debug
 
    logger.info('debug: %s, processes: %s', debug, args.process)

    prog = SVDog(processes=args.process)
    try:
        prog.run()
    except KeyboardInterrupt:
        sys.exit(0)
 
if __name__ == '__main__':
    main()
