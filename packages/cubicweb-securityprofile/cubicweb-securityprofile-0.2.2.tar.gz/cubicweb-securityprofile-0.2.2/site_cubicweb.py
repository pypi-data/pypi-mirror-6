options = (
    ('ldap-profile-filter',
     {'type': 'string',
      'default': None,
      'help': 'set e.g. to (&(objectClass=group)(cn=prefix*))',
      'group': 'securityprofile',
      'level': 1,
      }
    ),
    ('ldap-profile-member-attribute',
     {'type': 'string',
      'default': 'member',
      'help': 'the name of the attribute listing the DN of the members of the profile',
      'group': 'securityprofile',
      'level': 1,
     }
    )
)
