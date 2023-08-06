# -*- python -*-
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
import argparse
import decimal
import httpretty
import os
import pytest
import smstrade
import tempfile
import time


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture()
def api():
    testconfig = SafeConfigParser(defaults=smstrade.DEFAULTS)
    testconfig.add_section('smstrade')
    testconfig.set('smstrade', 'key', 'testkey')
    testconfig.set('smstrade', 'from', 'testsender')
    return smstrade.SMSTradeAPI(testconfig)


def test_SMSTradeError():
    exception = smstrade.SMSTradeError(u"a new test")
    assert str(exception) == 'a new test'


@pytest.mark.usefixtures('cleandir')
def test_SMSTradeAPI_init():
    smstrade.SMSTradeAPI()


class TestSMSTradeAPI(object):
    def test__gsm0338_length(self, api):
        assert api._gsm0338_length(u'a') == 1
        assert api._gsm0338_length(u'€') == 2
        assert api._gsm0338_length(u'a€') == 3
        with pytest.raises(smstrade.SMSTradeError):
            api._gsm0338_length(u'Ł')

    def test__check_normal_message(self, api):
        api._check_normal_message(160 * u'a')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_normal_message(161 * u'a')
        api.concat = True
        api._check_normal_message(1530 * u'a')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_normal_message(1531 * u'a')

    def test__encoding_normal_message(self, api):
        api.charset = 'ISO-8859-1'
        api._check_normal_message(160 * u'a')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_normal_message(80 * u'€')
        api.charset = 'ISO-8859-15'
        api._check_normal_message(80 * u'€')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_normal_message(160 * u'Ω')
        api.charset = 'UTF-8'
        api._check_normal_message(160 * u'Ω')

    def test__check_unicode_message(self, api):
        api._check_unicode_message(70 * u'€')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_unicode_message(70 * unichr(0x120AE))
        with pytest.raises(smstrade.SMSTradeError):
            api._check_unicode_message(71 * u'€')

    def test__check_binary_message(self, api):
        api._check_binary_message(140 * 'a0')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_binary_message(141 * 'a0')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_binary_message(30 * 'r0')

    def test__check_voice_message(self, api):
        api._check_voice_message(160 * u'a')
        with pytest.raises(smstrade.SMSTradeError):
            api._check_voice_message(161 * u'a')

    def test__check_message(self, api):
        api._check_message(160 * u'a')
        api.messagetype = 'flash'
        api._check_message(160 * u'a')
        api.messagetype = 'unicode'
        api._check_message(70 * u'€')
        api.messagetype = 'binary'
        api._check_message(140 * 'a0')
        api.messagetype = 'voice'
        api._check_message(160 * u'a')
        api.messagetype = 'wrong'
        with pytest.raises(smstrade.SMSTradeError):
            api._check_message('does not matter')

    def test__handle_response_body(self, api):
        assert api._handle_response_body('100') == {
            'status': smstrade.STATUS_OK}
        assert api._handle_response_body(str(
            smstrade.STATUS_NOT_ENOUGH_BALANCE)) == {
            'status': smstrade.STATUS_NOT_ENOUGH_BALANCE}
        assert api._handle_response_body('100\n12345678') == {
            'status': smstrade.STATUS_OK}
        api.message_id = True
        assert api._handle_response_body('100\n12345678') == {
            'status': smstrade.STATUS_OK,
            'message_id': '12345678'}
        with pytest.raises(smstrade.SMSTradeError):
            api._handle_response_body('100')
        assert api._handle_response_body('100\n12345678\n0') == {
            'status': smstrade.STATUS_OK,
            'message_id': '12345678'}
        api.cost = True
        assert api._handle_response_body('100\n12345678\n0') == {
            'status': smstrade.STATUS_OK,
            'message_id': '12345678',
            'cost': decimal.Decimal('0')}
        api.message_id = False
        assert api._handle_response_body('100\n\n0.055') == {
            'status': smstrade.STATUS_OK,
            'cost': decimal.Decimal('0.055')}
        assert api._handle_response_body('100\n\n0.055\n1') == {
            'status': smstrade.STATUS_OK,
            'cost': decimal.Decimal('0.055')}
        api.count = True
        assert api._handle_response_body('100\n\n0.055\n1') == {
            'status': smstrade.STATUS_OK,
            'cost': decimal.Decimal('0.055'),
            'count': 1}
        api.message_id = True
        assert api._handle_response_body('100\n12345678\n0.055\n1') == {
            'status': smstrade.STATUS_OK,
            'message_id': '12345678',
            'message_id': '12345678',
            'cost': decimal.Decimal('0.055'),
            'count': 1}

    @pytest.mark.usefixtures('cleandir')
    def test__add_optional_flags(self, api):
        for attrname, param in (
                ('debug', 'debug'),
                ('cost', 'cost'),
                ('message_id', 'message_id'),
                ('count', 'count'),
                ('reports', 'dir'),
                ('response', 'response')):
            setattr(api, attrname, True)
            request_params = {}
            request_params = api._add_optional_flags(request_params)
            assert request_params[param] == 1
        api.route = smstrade.ROUTE_GOLD
        api.response = True
        request_params = {}
        api._add_optional_flags(request_params)
        assert 'response' not in request_params

    @pytest.mark.usefixtures('cleandir')
    def test__add_optional_fields(self, api):
        for attrname, param, value in (
                ('reference', 'ref', 'myref0815'),
                ('senddate', 'senddate', int(time.time() + 100)),
                ('messagetype', 'messagetype', 'flash')):
            setattr(api, attrname, value)
            request_params = {}
            request_params = api._add_optional_fields(request_params)
            assert request_params[param] == value

    @pytest.mark.usefixtures('cleandir')
    def test__build_request_parameters(self, api):
        api.key = 'Testkey'
        assert api._build_request_parameters('01717654321') == {
            'key': 'Testkey',
            'to': '01717654321',
            'route': 'basic',
            'debug': 1}
        api.route = smstrade.ROUTE_GOLD
        api.charset = 'UTF-8'
        api.sender = u'Dönermann'
        assert api._build_request_parameters('01717654321') == {
            'key': 'Testkey',
            'to': '01717654321',
            'route': 'gold',
            'debug': 1,
            'from': u'Dönermann'.encode('UTF-8'),
            'charset': 'UTF-8'}

    def test__send_normal_message(self, api):
        httpretty.enable()
        httpretty.register_uri(httpretty.POST, api.url, body='100')
        assert api._send_message('01717654321', 'Test') == {
            'status': smstrade.STATUS_OK}
        httpretty.register_uri(httpretty.POST, api.url,
                               body='100\n\n\n4')
        api.concat = True
        api.count = True
        assert api._send_message('01717654321', 140 * 'Test') == {
            'status': smstrade.STATUS_OK,
            'count': 4}

    def test__send_binary_message(self, api):
        httpretty.enable()
        httpretty.register_uri(httpretty.POST, api.url, body='100')
        api.messagetype = smstrade.MESSAGE_TYPE_BINARY
        api.udh = '040b02000820de'
        assert api._send_message('01717654321', u'48656c6c6f') == {
            'status': smstrade.STATUS_OK}

    def test__send_message(self, api):
        httpretty.enable()
        httpretty.register_uri(httpretty.POST, api.url, body='100')
        assert api._send_message('01717654321', u'Test') == {
            'status': smstrade.STATUS_OK}
        for messagetype, message in (
                (smstrade.MESSAGE_TYPE_FLASH, u'Test'),
                (smstrade.MESSAGE_TYPE_UNICODE, u'Привет мир'),
                (smstrade.MESSAGE_TYPE_BINARY, u'48656c6c6f'),
                (smstrade.MESSAGE_TYPE_VOICE, u'Test')):
            api.messagetype = messagetype
            assert api._send_message('01717654321', message) == {
                'status': smstrade.STATUS_OK}
        with pytest.raises(smstrade.SMSTradeError):
            api.messagetype = 'invalid'
            api._send_message('01717654321', u'Test')

    def test_send_sms(self, api):
        httpretty.enable()
        httpretty.register_uri(httpretty.POST, api.url, body='100')
        testargs = {'wrong': 'does not matter', 'from': 'test'}
        result = api.send_sms(['00491717654321'], 'Test', **testargs)
        assert result == {'00491717654321': {'status': smstrade.STATUS_OK}}


def test_hexstr():
    assert smstrade.hexstr('A0a0') == 'A0a0'
    with pytest.raises(argparse.ArgumentTypeError):
        smstrade.hexstr('R0')


def test_secondssinceepoch():
    timestamp = str(int(time.time() + 100))
    assert smstrade.secondssinceepoch(timestamp) == int(timestamp)
    timestamp = str(int(time.time() - 100))
    with pytest.raises(argparse.ArgumentTypeError):
        smstrade.secondssinceepoch(timestamp)


@pytest.mark.usefixtures('cleandir')
def test_send_sms():
    httpretty.enable()
    httpretty.register_uri(httpretty.POST, smstrade.DEFAULTS['url'],
                           body='100')
    with pytest.raises(SystemExit):
        smstrade.send_sms([])
    smstrade.send_sms(['00491717654321', 'Test'])
    smstrade.send_sms(['--messagetype', 'binary', '00491717654321', 'Test'])
    with open('dummy.ini', 'w') as inifile:
        inifile.write('[smstrade]\nkey = fake')
    smstrade.send_sms(['--config', 'dummy.ini', '00491717654321', 'Test'])


@pytest.mark.usefixtures('cleandir')
def test_account_balance():
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, smstrade.DEFAULTS['balanceurl'], body='0.000')
    smstrade.account_balance([])
    smstrade.account_balance(['--key', 'fake'])
    with open('dummy.ini', 'w') as inifile:
        inifile.write('[smstrade]\nkey = fake')
    smstrade.account_balance(['--config', 'dummy.ini'])
