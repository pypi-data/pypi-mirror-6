Detailed message layout
=======================

A complete CEF message is written out into the payload section of the
heka message.

CEF metadata including syslog priority, syslog ident, and syslog facilty
are passed as string fields in the Heka message.

The following shows a capture of an example CEF message being captured
by hekad. ::

    2013/09/23 12:15:09 <
        Timestamp: 2013-09-23 12:15:09.134116864 -0400 EDT
        Type: cef
        Hostname: Victors-MacBook-Air.local
        Pid: 80776
        UUID: 95833933-db90-515f-9c43-469733c560e4
        Logger:
        Payload: Sep 23 12:15:09 Victors-MacBook-Air.local CEF:0|mozilla|weave|3|xx\|x|xx\|x|5|cs1Label=requestClientApplication cs1=MySuperBrowser requestMethod=GET request=/ src=127.0.0.1 dest=127.0.0.1 suser=none
        EnvVersion: 0.8
        Severity: 6
        Fields: [name:"cef_meta.syslog_priority" value_type:STRING representation:"" value_string:"EMERG" 
                 name:"cef_meta.syslog_ident" value_type:STRING representation:"" value_string:"my_funny_app" 
                 name:"cef_meta.syslog_facility" value_type:STRING representation:"" value_string:"KERN"]
