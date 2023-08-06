collective.anonfeedback
=======================

This package contains two views, a form that will collect feedback, and view
to view the feedback. They are protected by two different permissions, the
permission to enter feedback is by default given to everyone, and the
permission to view the feedback is by default given to site administrators.

The feedback is stored in var/anonfeedback with each feedback in it's own
file. The reason for this is that if we store the feeback in the ZODB we
create a ZODB transaction, and if you are logged in to the site at that
point, it will be possible to see who wrote the feedback from the Undo
transaction log, and the requirement of this package was explicitly that you
should be anonymous even if you forget to log out.

Warning!
********

Please note that it may still be possible to figure out the posters identity
by comparing web-server logs and IP-adresses and times, etc. To achieve true
anonymity you must also anonymize the internet access. The purpose of this
package is just to make it hard for your boss to figure out who thought his
proposal for site color scheme was ugly, not to provide truly anonymous
whistleblower access.
