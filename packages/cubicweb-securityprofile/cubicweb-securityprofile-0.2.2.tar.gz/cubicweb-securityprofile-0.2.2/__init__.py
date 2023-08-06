"""cubicweb-securityprofile application package

A SecurityProfile is a way to easily give membership to a set of
groups to several users: define your SecurityProfile, say that it
gives_membership to the CWGroups you're interested in, and link your
users to the profile.

This cube also adds:

* a security_officers CWGroup which has rights to manage
  SecurityProfiles and the relations used by that entity

* the possibility to map some attributes from an LDAP directory to
  define which SecurityProfiles a user is linked to
"""
