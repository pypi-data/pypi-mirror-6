=====================
django-ui-permissions
=====================

**WARNING:** *This module is under development and is more a proof of concept than ready solution*

``django-ui-permissions`` tries to speed up adding and managing very detailed permissions.
Detailed enough so that you can specify which fields or page elements are visible or editable for given role.
It does all that independently from typical Model permissions. Instead you describe role by what given user can do on
web page (e.g what part of web page does he sees or what fields he can edit).
