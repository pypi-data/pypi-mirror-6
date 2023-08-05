# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2012
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****
HEKA_METHOD_NAME = 'cef'

VALID_FACILITY = ['KERN', 'USER', 'MAIL', 'DAEMON', 'AUTH', 'LPR',
'NEWS', 'UUCP', 'CRON', 'LOCAL0', 'LOCAL1', 'LOCAL2', 'LOCAL3',
'LOCAL4', 'LOCAL5', 'LOCAL6', 'LOCAL7', ]

VALID_PRIORITY = ['EMERG', 'ALERT', 'CRIT', 'ERR', 'WARNING',
'NOTICE', 'INFO', 'DEBUG']


class InvalidArgumentError(RuntimeError):
    pass


def check_config(syslog_facility, syslog_ident, syslog_priority):

    if syslog_facility:
        if syslog_facility not in VALID_FACILITY:
            msg = "Facility should be one of: %s" % str(VALID_FACILITY)
            raise InvalidArgumentError(msg)

    if syslog_ident:
        if not isinstance(syslog_ident, basestring):
            msg = "syslog_ident should be a string"
            raise InvalidArgumentError(msg)

    if syslog_priority:
        if syslog_priority not in VALID_PRIORITY:
            msg = "Priority should be one of : %s" % str(VALID_PRIORITY)
            raise RuntimeError(msg)


def config_plugin(config):
    """
    CEF requires no special configuration
    """
    syslog_facility = config.pop('syslog_facility', "LOCAL4")
    syslog_ident = config.pop('syslog_ident', "")
    syslog_priority = config.pop('syslog_priority', "")

    check_config(syslog_facility, syslog_ident, syslog_priority)

    if len(config) > 0:
        msg = "Unexpected arguments: %s" % str(config.keys())
        raise InvalidArgumentError(msg)

    cef_meta = {}
    cef_meta['syslog_facility'] = syslog_facility
    cef_meta['syslog_ident'] = syslog_ident
    cef_meta['syslog_priority'] = syslog_priority

    def log_cef(self, name, severity, environ, config, username='none',
                signature=None, **kw):
        """Creates a CEF record, and emit it to heka in the fields blob.

        Args:
            - name: name to log
            - severity: integer from 0 to 10
            - environ: the WSGI environ object
            - config: configuration dict
            - signature: CEF signature code - defaults to name value
            - username: user name - defaults to 'none'
            - extra keywords: extra keys used in the CEF extension
        """
        from cef import _get_fields, _format_msg, _filter_params
        config = _filter_params('cef', config)
        fields = _get_fields(name, severity, environ, config,
                             username=username, signature=signature, **kw)
        msg = _format_msg(fields, kw)

        try:
            self.heka(type='cef', payload=msg, fields={'cef_meta': cef_meta})
        except ValueError:
            # Brutal brute force back into unicode. CEF lib explicitly converts
            # unicode to UTF8, but protobuf lib barfs on UTF8, it wants
            # unicode. Which it then proceeds to convert back into UTF8. *sigh*
            # Ideally cef lib is updated to accept a "give me unicode" option.
            msg = unicode(msg, "UTF-8", "replace")
            self.heka(type='cef', payload=msg, fields={'cef_meta': cef_meta})

        # Return the formatted message
        return msg
    log_cef.heka_name = HEKA_METHOD_NAME
    log_cef.cef_meta = cef_meta

    return log_cef
