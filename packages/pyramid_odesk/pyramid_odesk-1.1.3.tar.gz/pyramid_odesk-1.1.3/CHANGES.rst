1.1.3
-----
- Store first and last name in the session for further usage in templates

1.1.2
-----
- Login and Logout actions are performed via POST and has protection
  against CSRF attacks

1.1.1
-----
- Fix ``BaseHandler`` obscuring ``AttributeError`` during dispatch

1.1
---
- Use ``override_offset`` for overriding ``forbidden.jinja2`` template.
- If user is authenticated but is not authrized for some view,
  render ``forbidden`` page with **Log out** link instead of redirect
  to avoid redirect loop

1.0
---
- Initial version.
