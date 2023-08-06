import logging

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb import ValidationError

from cubes.securityprofile import hooks


class SecurityProfileHooksTC(CubicWebTC):
    def setup_database(self):
        req = self.request()
        grp1 = req.create_entity('CWGroup', name=u'group1')
        grp2 = req.create_entity('CWGroup', name=u'group2')
        users = self.execute('Any X WHERE X is CWGroup, X name %(name)s', {'name': u'users'}).get_entity(0, 0)
        prof1 = req.create_entity('SecurityProfile', name=u'prof1', gives_membership=[users, grp1])
        prof2 = req.create_entity('SecurityProfile', name=u'prof2', gives_membership=[grp1, grp2, users])
        self.user1 = req.create_entity('CWUser', login=u'toto', upassword=u'toto', has_security_profile=prof2, in_group=users)

    def test_user1(self):
        rset = self.execute('Any G WHERE U eid %(eid)s, U in_group G',
                            {'eid': self.user1.eid})
        groups = set([g.name for g in rset.entities()])
        self.assertSetEqual(groups, set(['group1', 'group2', 'users']))

    def test_update_has_security_profile(self):
        self.execute('DELETE U has_security_profile P WHERE U eid %(eid)s, P name %(p)s',
                     {'eid': self.user1.eid,
                      'p': u'prof2'})
        self.execute('SET U has_security_profile P WHERE U eid %(eid)s, P name %(p)s',
                     {'eid': self.user1.eid,
                      'p': u'prof1'})
        self.commit()
        rset = self.execute('Any G WHERE U eid %(eid)s, U in_group G',
                            {'eid': self.user1.eid})

        groups = set([g.name for g in rset.entities()])
        self.assertSetEqual(groups, set(['group1', 'users']))

    def test_update_gives_membership(self):
        self.execute('DELETE P gives_membership G WHERE G name %(g)s, P name %(p)s',
                     {'g': u'group1',
                      'p': u'prof2'})
        self.commit()
        rset = self.execute('Any G WHERE U eid %(eid)s, U in_group G',
                            {'eid': self.user1.eid})
        groups = set([g.name for g in rset.entities()])
        self.assertSetEqual(groups, set(['group2', 'users']))



def mock_extid2eid(session, uri, extid):
    """ we are too lazy to build  & feed a full ldapfeed source ...
    hence we use the system source, by the actual system source extid2eid
    won't work with these parameters, hence we monkey-cheat.
    """
    return session.execute('Any U WHERE U is CWUser, U login %(l)s',
                           {'l': extid}).get_entity(0,0).eid

class SynchronizeProfileTC(CubicWebTC):
    def setup_database(self):
        req = self.request()
        grp1 = req.create_entity('CWGroup', name=u'group1')
        grp2 = req.create_entity('CWGroup', name=u'group2')
        users = self.execute('Any X WHERE X is CWGroup, X name %(name)s', {'name': u'users'}).get_entity(0, 0)
        self.user1 = req.create_entity('CWUser', login=u'user1', upassword=u'toto',
                                       in_group=users)
        self.user2 = req.create_entity('CWUser', login=u'user2', upassword=u'toto',
                                       in_group=users)
        sec_prof = req.create_entity('SecurityProfile',
                                     name=u'all_users',
                                     dn= u'CN=all_users,OU=test',
                                     gives_membership=[users])
        # monkeypatch system source
        # as we will fake extids with actual user logins ...
        self.session.repo.system_source.extid2eid = mock_extid2eid

    def test_sync(self):
        profiles = [sp.name for sp in self.user1.has_security_profile]
        print profiles
        logger = logging.getLogger('cubicweb.securityprofile')
        logger.setLevel(logging.DEBUG)
        ldap_profiles = [{'dn': u'CN=prof1,OU=test', 'cn': u'prof1', 'descr': u'profile1',
                     'members': [u'user1', u'user2']},
                    {'dn': u'CN=prof2,OU=test', 'cn': u'prof2', 'descr': u'profile2',
                     'members': [u'user1', ]},
                    {'dn': u'CN=prof3,OU=test', 'cn': u'prof3', 'descr': u'profile3',
                     'members': [u'user2']},
                    {'dn': u'CN=prof4,OU=test', 'cn': u'prof4', 'descr': u'profile4',
                     'members': []},
                    {'dn': u'CN=all_users,OU=test', 'cn':u'all_users', 'descr':u'all users',
                     'members': [u'user1', u'user2']},
                    ]
        self.sync(ldap_profiles)
        req = self.request()
        self.user1.clear_all_caches()
        profiles = [sp.name for sp in self.user1.has_security_profile]
        self.assertItemsEqual(profiles, ['prof1', 'prof2', 'all_users'])
        self.user2.clear_all_caches()
        profiles = [sp.name for sp in self.user2.has_security_profile]
        self.assertItemsEqual(profiles, ['prof1', 'prof3', 'all_users'])

        self.execute('SET P gives_membership G WHERE P dn %(dn)s, G name %(n)s',
                     {'dn': u'CN=prof2,OU=test',
                      'n': u'group2'})
        self.execute('SET P gives_membership G WHERE P dn %(dn)s, G name %(n)s',
                     {'dn': u'CN=prof3,OU=test',
                      'n': u'users'})

        self.commit()

        ldap_profiles = [{'dn': u'CN=prof1,OU=test', 'cn': u'prof1', 'descr': u'profile1',
                     'members': [u'user1', u'user2']},
                    {'dn': u'CN=prof2,OU=test', 'cn': u'prof2', 'descr': u'profile2',
                     'members': [u'user2', ]},
                    {'dn': u'CN=prof3,OU=test', 'cn': u'prof3', 'descr': u'profile3',
                     'members': [u'user2']},
                    {'dn': u'CN=prof4,OU=test', 'cn': u'prof4', 'descr': u'profile4',
                     'members': []},
                    {'dn': u'CN=all_users,OU=test', 'cn':u'all_users', 'descr':u'all users',
                     'members': [u'user1', u'user2']},
                    ]

        self.sync(ldap_profiles)
        self.user1.clear_all_caches()
        profiles = [sp.name for sp in self.user1.has_security_profile]
        self.assertItemsEqual(profiles, ['prof1', 'all_users'])
        self.user2.clear_all_caches()
        profiles = [sp.name for sp in self.user2.has_security_profile]
        self.assertItemsEqual(profiles, ['prof1', 'prof2',  'prof3', 'all_users'])
        #self.execute('DELETE SecurityProfile P')
        self.commit()

    def sync(self, profiles):
        import logging
        print '*******', 'sync'
        logger = logging.getLogger('cubicweb.securityprofile')
        session = self.session
        ldap_profiles = {}
        for profile in profiles:
            ldap_profiles[profile['dn']] = profile
        cw_profiles = self.execute('Any P WHERE P is SecurityProfile')
        to_delete = []
        for cw_profile in cw_profiles.entities(0):
            if cw_profile.dn in ldap_profiles:
                attrs = ldap_profiles.pop(cw_profile.dn)
                cw_profile.set_attributes(name=attrs['cn'],
                                          description=attrs.get('description', u''))
                hooks.set_profile_users(session.repo.system_source, session, attrs, 'members')
            else:
                to_delete.append(str(cw_profile.eid))
        for attrs in ldap_profiles.itervalues():
            if 'description' not in attrs:
                attrs['description'] = u''
            logger.info('synchronize profiles: inserting SecurityProfile %s'% attrs['cn'])
            session.execute('INSERT SecurityProfile X: '
                            '   X dn %(dn)s, '
                            '   X name %(cn)s, '
                            '   X description %(description)s',
                            attrs)
            hooks.set_profile_users(session.repo.system_source, session, attrs, 'members')
        if to_delete:
            logger.info('synchronize profiles: delete %s', to_delete)
            session.execute('DELETE SecurityProfile P WHERE p eid in (%s)' % ','.join(to_delete))
        session.commit()


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
