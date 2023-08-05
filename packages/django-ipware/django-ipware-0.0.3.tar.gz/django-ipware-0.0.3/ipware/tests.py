# -*- coding: utf-8 -*-

from django.http import HttpRequest
from django.test import TestCase
from ipware.ip import get_real_ip

class IPv4TestCase(TestCase):
    """IP address Test"""

    def test_x_forwarded_for_multiple(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.255.182, 10.0.0.0, 127.0.0.1, 198.84.193.157, 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "198.84.193.157")

    def test_x_forwarded_for_multiple_bad_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, 192.168.255.182, 10.0.0.0, 127.0.0.1, 198.84.193.157, 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "198.84.193.157")

    def test_x_forwarded_for_singleton(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.139")

    def test_x_forwarded_for_singleton_private_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.255.182',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.132")

    def test_bad_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.132")

    def test_empty_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.132")

    def test_empty_x_forwarded_for_empty_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.133")

    def test_empty_x_forwarded_for_private_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '192.168.255.182',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.133")


    def test_private_x_forward_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '127.0.0.1',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, None)

    def test_private_real_ip_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '127.0.0.1',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, None)

    def test_private_remote_addr_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '127.0.0.1',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, None)

    def test_missing_x_forwarded(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.132")


    def test_missing_x_forwarded_missing_real_ip(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "177.139.233.133")


class IPv6TestCase(TestCase):
    """IP address Test"""

    def test_x_forwarded_for_multiple(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, fe80:0:0:0:200:f8ff:fe21:67cf',
            'HTTP_X_REAL_IP': 'fe80:0:0:0:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': 'fe80:0:0:0:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "3ffe:1900:4545:3:200:f8ff:fe21:67cf")

    def test_x_forwarded_for_multiple_bad_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, ::1/128, fe80:0:0:0:200:f8ff:fe21:67cf',
            'HTTP_X_REAL_IP': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_x_forwarded_for_singleton(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'fe80:0:0:0:200:f8ff:fe21:67cf',
            'HTTP_X_REAL_IP': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_x_forwarded_for_singleton_private_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '::1/128',
            'HTTP_X_REAL_IP': 'fe80:0:0:0:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_bad_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown ::1/128',
            'HTTP_X_REAL_IP': 'fe80:0:0:0:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_empty_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': 'fe80:0:0:0:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_empty_x_forwarded_for_empty_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': 'fe80:0:0:0:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_empty_x_forwarded_for_private_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '::1/128',
            'REMOTE_ADDR': 'fe80:0:0:0:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_private_x_forward_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '::1/128',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, None)

    def test_private_real_ip_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '::1/128',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, None)

    def test_private_remote_addr_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '::1/128',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, None)

    def test_missing_x_forwarded(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': 'fe80:0:0:0:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': 'fe80:0:0:0:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")


    def test_missing_x_forwarded_missing_real_ip(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': 'fe80:0:0:0:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEquals(ip, "fe80:0:0:0:200:f8ff:fe21:67cf")

    def test_missing_x_forwarded_missing_real_ip_mix_case(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': 'fe80:0:0:0:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertNotEquals(ip, "FE80:0:0:0:200:f8ff:fe21:67cf")





