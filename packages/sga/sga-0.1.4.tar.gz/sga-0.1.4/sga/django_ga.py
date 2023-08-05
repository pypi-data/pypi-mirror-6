# -*- coding: utf-8 -*-

"""
django插件，绑定之后可以自动给本地的ga_center发送数据
要求配置:
    GA_ID : Google分析的跟踪ID
    GA_CENTER_HOST : GACenter的启动IP
    GA_CENTER_PORT : GACenter的启动端口
"""

import logging
import socket
import json
import errno
import time
from django.conf import settings

import constants

logger = logging.getLogger('django_ga')


class DjangoGA(object):
    _ga_id = None
    _ga_center_host = None
    _ga_center_port = None

    _local_ip = ''

    _socket = None

    def __init__(self):
        self._ga_id = getattr(settings, 'GA_ID', None)
        self._ga_center_host = getattr(settings, 'GA_CENTER_HOST', None) or constants.GA_CENTER_DEFAULT_HOST
        self._ga_center_port = getattr(settings, 'GA_CENTER_PORT', None) or constants.GA_CENTER_DEFAULT_PORT

        self._local_ip = socket.gethostbyname(socket.gethostname()) or ''

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 非阻塞
        self._socket.setblocking(0)

    def process_request(self, request):
        request.ga_begin_time = time.time()

    def process_response(self, request, response):
        """
        无论是否抛出异常，都会执行这一步
        """
        self.send_ga_data(request)
        return response

    def send_ga_data(self, request):
        ga_end_time = time.time()
        logger.debug('ga_id:%s', self._ga_id)

        if not self._ga_id:
            return

        try:
            send_dict = dict(
                funcname='track_pageview',
                tracker=dict(
                    __ga=True,
                    account_id=self._ga_id,
                    domain_name=request.get_host(),
                    campaign=dict(
                        __ga=True,
                        source=self._local_ip,
                        content='/',
                    ),
                ),
                session=dict(
                    __ga=True,
                ),
                page=dict(
                    __ga=True,
                    path=request.path,
                    load_time=int((ga_end_time-request.ga_begin_time) * 1000),
                ),
                visitor=dict(
                    __ga=True,
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                ),
            )
            self.send_data_to_ga_center(send_dict)
        except Exception, e:
            logger.error('exception occur. msg[%s], traceback[%s]', str(e), __import__('traceback').format_exc())

    def send_data_to_ga_center(self, send_dict):
        """
        可以在网站中调用
        """
        try:
            self._socket.sendto(json.dumps(send_dict), (self._ga_center_host, self._ga_center_port))
        except socket.error, e:
            # errno.EWOULDBLOCK = errno.EAGAIN = 11
            if e.args[0] == errno.EWOULDBLOCK:
                logger.info('errno.EWOULDBLOCK')
            else:
                logger.error('exception occur. msg[%s], traceback[%s]', str(e), __import__('traceback').format_exc())
