=============================
collective.local.contentrules
=============================

This product provides string interpolators for email content rule action.

They get emails of users who have a role on the content
and have a read access to the content.

This is useful for notifying members that share contents in folders.
That's why we included it in collective.local namespace.

Unlike default Plone string interpolators, you don't send emails to users that
have a role on a content but do not actually have access to the content
(by example if the content is private.)
