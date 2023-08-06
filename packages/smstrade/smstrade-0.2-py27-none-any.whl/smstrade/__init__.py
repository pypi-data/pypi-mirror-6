# -*- python -*-
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Jan Dittberner

from ._version import __version__
from ConfigParser import SafeConfigParser, NoOptionError
from base64 import b16encode
from datetime import datetime
from locale import getpreferredencoding
from pprint import pformat
import appdirs
import argparse
import decimal
import logging
import os
import requests


#: default configuration files
CONFIGFILES = [
    os.path.join(appdirs.site_config_dir('smstrade'),
                 'smstrade.ini'),
    os.path.join(appdirs.user_config_dir('smstrade'),
                 'smstrade.ini'),
    'smstrade.ini']

#: default values for configuration
DEFAULTS = {
    'url': 'https://gateway.smstrade.de/',
    'balanceurl': 'https://gateway.smstrade.de/credits/',
    'route': 'basic',
    'debug': 'True',  # debug is set to True to avoid costs
    'enable-cost': 'False',
    'enable-message-id': 'False',
    'enable-count': 'False',
    'enable-delivery-reports': 'False',
    'enable-response': 'False',
    'enable-concat': 'False',  # concat is disabled to avoid costs
    'charset': 'ascii',
}

#: characters allowed in GSM 03.38
GSM0338_CHARS = (
    u'@£$¥èéùìòÇ\nØø\rÅå'
    u'Δ_ΦΓΛΩΠΨΣΘΞ' + unichr(27) + u'ÆæÉ'
    u' !"#¤%&\'()*+,-./'
    u'0123456789:;<=>?'
    u'¡ABCDEFGHIJKLMNO'
    u'PQRSTUVWXYZÄÖÑÜ§'
    u'abcdefghijklmno'
    u'pqrstuvwxyzäöñüà'
)

#: characters allowed in GSM 03.38 that occupy two octets
GSM0338_TWO_OCTET_CHARS = u'€' + unichr(12) + ur'[\]^{|}~'

# Message types defined in API documentation
#: Message type flash
MESSAGE_TYPE_FLASH = 'flash'
#: Message type unicode
MESSAGE_TYPE_UNICODE = 'unicode'
#: Message type binary
MESSAGE_TYPE_BINARY = 'binary'
#: Message type voice
MESSAGE_TYPE_VOICE = 'voice'

# Route names defined in API documentation
#: Route basic
ROUTE_BASIC = 'basic'
#: Route gold
ROUTE_GOLD = 'gold'
#: Route direct
ROUTE_DIRECT = 'direct'

# Status codes defined in API documentation
#: Status receiver number not valid
STATUS_INVALID_RECEIVER_NUMBER = 10
#: Status sender number not valid
STATUS_INVALID_SENDER_NUMBER = 20
#: Status message text not valid
STATUS_INVALID_MESSAGE_TEXT = 30
#: Status message type not valid
STATUS_INVALID_MESSAGE_TYPE = 31
#: Status SMS route not valid
STATUS_INVALID_SMS_ROUTE = 40
#: Status identification failed
STATUS_IDENTIFICATION_FAILED = 50
#: Status not enough balance in account
STATUS_NOT_ENOUGH_BALANCE = 60
#: Status network does not support the route
STATUS_NETWORK_NOT_SUPPORTED_BY_ROUTE = 70
#: Status feature is not possible by the route
STATUS_FEATURE_NOT_POSSIBLE_FOR_ROUTE = 71
#: Status handover to SMSC failed
STATUS_SMSC_HANDOVER_FAILED = 80
#: Status SMS has been sent successfully
STATUS_OK = 100

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class SMSTradeError(Exception):
    """
    Custom exception type.

    """
    def __str__(self):
        return self.message.encode(getpreferredencoding())


class SMSTradeAPIBase(object):
    """
    Base class for smstrade.eu API clients.

    """

    def __init__(self, config=None, section='smstrade'):
        """
        Initialize a new SMSTradeAPIBase instance.

        :param ConfigParser config:
            use the specified configuration instead of the default
            configuration

        :param str section:
            use the specified section in the configuration

        """
        if config:
            self.config = config
        else:
            self.config = SafeConfigParser(defaults=DEFAULTS)
            conffiles = self.config.read(CONFIGFILES)
            if not conffiles:
                log.warning((
                    u'none of the configuration files (%s) found, trying'
                    u' to continue with default values and command line'
                    u' arguments'), ", ".join(CONFIGFILES))
                self.config.add_section(section)
        self.key = None
        if self.config.has_section(section):
            try:
                self.key = self.config.get(section, 'key')
            except NoOptionError as e:
                log.warning(u"configuration is incomplete: %s", e)
        else:
            log.warning(u"configuration section %s does not exist.", section)

    def prepare_args(self, kwargs):
        """
        Take a dictionary with keyword arguments, usually parsed from the
        command line and set existing attributes of this instance.

        :param dict kwargs:
            dictionary of keyword arguments

        """
        for key, value in kwargs.iteritems():
            if value is not None:
                setattr(self, key, value)


class SMSTradeAPI(SMSTradeAPIBase):
    """
    Abstraction of the `smstrade.eu <http://smstrade.eu>`_ http(s) mail sending
    API.

    """

    def __init__(self, config=None, section='smstrade'):
        """
        Initialize a new SMSTradeAPI instance.

        :param ConfigParser config:
            use the specified configuration instead of the default
            configuration

        :param str section:
            use the specified section in the configuration

        """
        super(SMSTradeAPI, self).__init__(config, section)

        self.response = None
        self.sender = None
        self.reference = None
        self.senddate = None
        self.messagetype = None
        self.udh = None
        if self.config.has_section(section):
            try:
                self.url = self.config.get(section, 'url')
                self.route = self.config.get(section, 'route')
                self.debug = self.config.getboolean(section, 'debug')
                self.cost = self.config.getboolean(section, 'enable-cost')
                self.message_id = self.config.getboolean(
                    section, 'enable-message-id')
                self.count = self.config.getboolean(section, 'enable-count')
                self.reports = self.config.getboolean(
                    section, 'enable-delivery-reports')
                self.response = self.config.getboolean(
                    section, 'enable-response')
                self.concat = self.config.getboolean(section, 'enable-concat')
                self.charset = self.config.get(section, 'charset')
                self.sender = self.config.get(section, 'from')
            except NoOptionError as e:
                log.warning(u"configuration is incomplete: %s", e)
        else:
            log.warning(u"configuration section %s does not exist.", section)
        log.debug(self.__dict__)

    def _handle_response_body(self, body):
        """
        Handle parsing of response body.

        :param str body:
            response body
        """
        log.info("response body:\n%s", body)
        lines = body.splitlines()
        try:
            retval = {
                'status': int(lines[0]),
            }
            if self.message_id:
                retval['message_id'] = lines[1]
            if self.cost:
                retval['cost'] = decimal.Decimal(lines[2])
            if self.count:
                retval['count'] = int(lines[3])
        except IndexError:
            raise SMSTradeError('malformed response')
        return retval

    def _add_optional_flags(self, request_params):
        if self.debug:
            request_params['debug'] = 1
        if self.cost:
            request_params['cost'] = 1
        if self.message_id:
            request_params['message_id'] = 1
        if self.count:
            request_params['count'] = 1
        if self.reports:
            request_params['dir'] = 1
        if self.response and self.route == ROUTE_BASIC:
            request_params['response'] = 1
        return request_params

    def _add_optional_fields(self, request_params):
        if self.reference is not None:
            request_params['ref'] = self.reference
        if self.senddate is not None:
            request_params['senddate'] = self.senddate
        if self.messagetype is not None:
            request_params['messagetype'] = self.messagetype
        return request_params

    def _build_request_parameters(self, recipient):
        """
        Build the request parameter dictionary based on fields in this
        SMSTradeAPI instance.

        :param str recipient:
            recipient calling number

        """
        request_params = {
            'key': self.key,
            'to': recipient,
            'route': self.route,
        }
        if self.route in (ROUTE_GOLD, ROUTE_DIRECT):
            request_params['from'] = self.sender.encode(self.charset)
        if self.charset != 'ascii':
            request_params['charset'] = self.charset
        request_params = self._add_optional_flags(request_params)
        request_params = self._add_optional_fields(request_params)
        return request_params

    def _send_normal_message(self, recipient, text):
        """
        Send a normal SMS message to the given recipient.

        :param str recipient:
            recipient calling number

        :param unicode text:
            unicode SMS message text

        """
        request_params = self._build_request_parameters(recipient)
        request_params['message'] = text.encode(self.charset)
        if self.concat:
            request_params['concat'] = 1
        response = requests.post(self.url, data=request_params)
        response.raise_for_status()
        return self._handle_response_body(response.text)

    def _send_unicode_message(self, recipient, text):
        """
        Send a unicode SMS message to the given recipient.

        :param str recipient:
            recipient calling number

        :param unicode text:
            unicode SMS message text

        """
        request_params = self._build_request_parameters(recipient)
        request_params['message'] = b16encode(text.encode('utf_16_be'))
        response = requests.post(self.url, data=request_params)
        response.raise_for_status()
        return self._handle_response_body(response.text)

    def _send_binary_message(self, recipient, text):
        """
        Send a binary SMS message to the given recipient.

        :param str recipient:
            recipient calling number

        :param str text:
            hexadecimal representation of the binary data

        """
        request_params = self._build_request_parameters(recipient)
        request_params['message'] = text
        if self.udh is not None:
            request_params['udh'] = self.udh
        response = requests.post(self.url, data=request_params)
        response.raise_for_status()
        return self._handle_response_body(response.text)

    def _send_voice_message(self, recipient, text):
        """
        Send a voice SMS message to the given recipient.

        :param str recipient:
            recipient calling number

        :param unicode text:
            the message text

        """
        request_params = self._build_request_parameters(recipient)
        request_params['message'] = text.encode(self.charset)
        response = requests.post(self.url, data=request_params)
        response.raise_for_status()
        return self._handle_response_body(response.text)

    def _send_message(self, recipient, text):
        """
        Send an SMS to a single recipient.

        :param str recipient:
            recipient calling number

        :param str text:
            SMS message text

        """
        if ((self.messagetype is None) or
                (self.messagetype == MESSAGE_TYPE_FLASH)):
            return self._send_normal_message(recipient, text)
        elif self.messagetype == MESSAGE_TYPE_UNICODE:
            return self._send_unicode_message(recipient, text)
        elif self.messagetype == MESSAGE_TYPE_BINARY:
            return self._send_binary_message(recipient, text)
        elif self.messagetype == MESSAGE_TYPE_VOICE:
            return self._send_voice_message(recipient, text)
        else:
            raise SMSTradeError(u"unknown message type %s" %
                                self.messagetype)

    def _gsm0338_length(self, text):
        charcount = 0
        for char in text:
            if char in GSM0338_CHARS:
                charcount += 1
            elif char in GSM0338_TWO_OCTET_CHARS:
                charcount += 2
            else:
                raise SMSTradeError(
                    u"character %s is not allowed in GSM messages." % char)
        return charcount

    def _check_normal_message(self, text):
        """
        Perform a plausibility check on the given message text.

        :param str text:
            the message to check

        """
        charcount = self._gsm0338_length(text)
        if ((self.concat and charcount > 1530) or
                (not self.concat and charcount > 160)):
            message = "too many characters in message"
            if not self.concat and charcount <= 1530:
                message += ", you may try to use concat"
            raise SMSTradeError(message)
        try:
            text.encode(self.charset)
        except ValueError:
            raise SMSTradeError((
                "The message can not be encoded with the chosen character set"
                " %s") % self.charset)

    def _check_unicode_message(self, text):
        """
        Perform a plausibility check on the given unicode message text.

        :param str text:
            the message to check

        """
        for char in text:
            code = ord(char)
            if (code >= 0xd800 and code <= 0xdfff) or (code > 0xffff):
                raise SMSTradeError(
                    u"the message can not be represented in UCS2")
        if len(text) > 70:
            raise SMSTradeError(
                u"too many characters in message, unicode SMS may contain up"
                u" to 70 characters")

    def _check_binary_message(self, text):
        """
        Perform a plausibility check on the given binary message text.

        :param str text:
            the message to check

        """
        try:
            length = len(text.lower().decode('hex'))
            if length > 140:
                raise SMSTradeError(
                    u'too many bytes in message, binary messages may contain'
                    u' up to 140 bytes')
        except:
            raise SMSTradeError('message cannot be encoded as bytes')

    def _check_voice_message(self, text):
        """
        Perform a plausibility check on the give message intended to be sent as
        voice message.

        :param str text:
            the message to check

        """
        if self._gsm0338_length(text) > 160:
            raise SMSTradeError(u'too many GSM characters in message')

    def _check_message(self, text):
        if ((self.messagetype is None) or
                (self.messagetype == MESSAGE_TYPE_FLASH)):
            self._check_normal_message(text)
        elif self.messagetype == MESSAGE_TYPE_UNICODE:
            self._check_unicode_message(text)
        elif self.messagetype == MESSAGE_TYPE_BINARY:
            self._check_binary_message(text)
        elif self.messagetype == MESSAGE_TYPE_VOICE:
            self._check_voice_message(text)
        else:
            raise SMSTradeError(
                u"message type %s is unknown" % self.messagetype)

    def send_sms(self, to, text, **kwargs):
        """
        Send an SMS to recipients in the to parameter.

        :param list to:
            list of recipient calling numbers

        :param str text:
            SMS message text

        :param dict kwargs:
            keyword arguments that override values in the configuration files

        """
        self.prepare_args(kwargs)

        # convert to unicode
        if not self.messagetype == 'binary':
            text = text.decode(getpreferredencoding())

        retval = {}
        for recipient in to:
            self._check_message(text)
            retval[recipient] = self._send_message(recipient, text)
        return retval


class SMSTradeBalanceAPI(SMSTradeAPIBase):
    """
    Abstraction of the `smstrade.eu <http://smstrade.eu>`_ http(s) account
    balance API.

    """

    def __init__(self, config=None, section='smstrade'):
        """
        Initialize a new SMSTradeBalanceAPI instance.

        :param ConfigParser config:
            use the specified configuration instead of the default
            configuration

        :param str section:
            use the specified section in the configuration

        """
        super(SMSTradeBalanceAPI, self).__init__(config, section)

        if self.config.has_section(section):
            self.url = self.config.get(section, 'balanceurl')
        else:
            log.warning(u"configuration section %s does not exist.", section)
        log.debug(self.__dict__)

    def get_balance(self, **kwargs):
        """
        Get the account balance from smstrade.eu and return it as a
        :pyclass:`decimal.Decimal` instance.

        :param dict kwargs:
            keyword arguments that override values in the configuration files

        """
        self.prepare_args(kwargs)
        if self.key is None:
            raise SMSTradeError(
                u'you need to define an API key either in a configuration'
                u' file or on the command line')
        response = requests.get(self.url, params={'key': self.key})
        response.raise_for_status()
        return decimal.Decimal(response.text)


def hexstr(value):
    """
    Check whether the given hexadecimal value can successfully be decoded to
    bytes.

    :param str value:
        string of hexadecimal representations of bytes

    """
    try:
        value.lower().decode('hex')
    except TypeError as te:
        raise argparse.ArgumentTypeError(te.message)
    return value


def secondssinceepoch(seconds):
    """
    Check whether the given value is a valid timestamp after the current
    timestamp.

    :param str seconds:
        string value that represents an int specifying a timestamp relative to
        the UNIX epoch

    """
    value = int(seconds)
    if datetime.fromtimestamp(value) < datetime.now():
        raise argparse.ArgumentTypeError(
            "timestamps in the past are not allowed.")
    return value


def send_sms(cmdline=None):
    """
    Send SMS from the command line.

    :param list cmdline:
        list of command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Send one or more SMS via the smstrade.eu API")
    parser.add_argument(
        '-c', '--config', type=file,
        help=(
            "alternative configuration instead of the default configuration"
            "files:\n {0}").format(", ".join(CONFIGFILES)))
    parser.add_argument(
        '-s', '--section', type=str, default='smstrade',
        help='use the specified section in the configuration file')
    parser.add_argument(
        '-k', '--key', type=str,
        help="personal identification code")
    parser.add_argument(
        '-f', '--from', dest='sender', type=str,
        help="source identifier (ignored for route basic)")
    parser.add_argument(
        '-r', '--route', choices=[ROUTE_BASIC, ROUTE_GOLD, ROUTE_DIRECT],
        help='SMS route')
    parser.add_argument(
        '-d', '--debug', action='store_const', const=True,
        help='activate debug mode')
    parser.add_argument(
        '--cost', action='store_const', const=True,
        help='enable output of sending costs')
    parser.add_argument(
        '-m', '--message-id', action='store_const', const=True,
        dest='message_id',
        help='enable output of message ids')
    parser.add_argument(
        '--count', action='store_const', const=True,
        help='enable output of message count')
    parser.add_argument(
        '--dir', action='store_const', const=True,
        dest='reports',
        help='enable delivery reports')
    parser.add_argument(
        '--response', action='store_const', const=True,
        help='enable receiving of reply SMS (only for route basic)')
    parser.add_argument(
        '--ref', type=str, dest='reference',
        help='add an own reference for this message')
    parser.add_argument(
        '-l', '--concat', action='store_const', const=True,
        help='send as linked (longer) SMS')
    parser.add_argument(
        '--charset', choices=['UTF-8', 'ISO-8859-1', 'ISO-8859-15'],
        help=(
            "character set of the message (defaults to current locale's"
            " charset) converted to UTF-8 if necessary"))
    parser.add_argument(
        '--senddate', type=secondssinceepoch,
        help='send time delayed SMS at the given time (UNIX timestamp)')
    parser.add_argument(
        '--messagetype', choices=[
            MESSAGE_TYPE_FLASH, MESSAGE_TYPE_UNICODE, MESSAGE_TYPE_BINARY,
            MESSAGE_TYPE_VOICE],
        help='enable sending of flash, unicode, binary or voice messages')
    parser.add_argument(
        '--udh', type=hexstr,
        help='hexadecimal representation of bytes for a binary message')
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument(
        'to',
        nargs='+', type=str, help="receiver of the SMS",)
    parser.add_argument(
        'smstext',
        type=str,
        help="the text content of the SMS message to send")

    if cmdline is not None:
        args = parser.parse_args(cmdline)
    else:
        args = parser.parse_args()

    config = None
    if args.config:
        config = SafeConfigParser(defaults=DEFAULTS)
        config.readfp(args.config)

    smstrade = SMSTradeAPI(config=config, section=args.section)
    to = args.to
    smstext = args.smstext
    del args.config
    del args.section
    del args.to
    del args.smstext
    try:
        retval = smstrade.send_sms(to, smstext, **args.__dict__)
        log.info("Return value:\n%s", pformat(retval))
    except SMSTradeError as e:
        log.error(e)


def account_balance(cmdline=None):
    """
    Get the smstrade.eu account balance from the command line.

    :param list cmdline:
        list of command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Send one or more SMS via the smstrade.eu API")
    parser.add_argument(
        '-c', '--config', type=file,
        help=(
            "alternative configuration instead of the default configuration"
            "files:\n {0}").format(", ".join(CONFIGFILES)))
    parser.add_argument(
        '-s', '--section', type=str, default='smstrade',
        help='use the specified section in the configuration file')
    parser.add_argument(
        '-k', '--key', type=str,
        help="personal identification code")

    if cmdline is not None:
        args = parser.parse_args(cmdline)
    else:
        args = parser.parse_args()

    config = None
    if args.config:
        config = SafeConfigParser(defaults=DEFAULTS)
        config.readfp(args.config)

    smstradebalance = SMSTradeBalanceAPI(
        config=config, section=args.section)
    del args.config
    del args.section
    try:
        balance = smstradebalance.get_balance(**args.__dict__)
        log.info(u"Your smstrade balance : %.03f €", balance)
    except SMSTradeError as e:
        log.error(e)
