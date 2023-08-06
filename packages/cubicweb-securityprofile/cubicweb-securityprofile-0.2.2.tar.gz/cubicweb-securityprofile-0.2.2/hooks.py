# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-securityprofile specific hooks and operations"""

import logging

from cubicweb import set_log_methods
from cubicweb.server.hook import Hook, Operation, DataOperationMixIn, match_rtype
from cubicweb.predicates import is_instance

from cubicweb.sobjects.ldapparser import DataFeedLDAPAdapter

class SecurityProfileLdapParser(DataFeedLDAPAdapter):

    # the datafeed parser calls .process, THEN .handle_deletion
    # hence we plug ourselves at the very end of handle_deletion ...
    def handle_deletion(self, config, session, myuris):
        super(SecurityProfileLdapParser, self).handle_deletion(config, session, myuris)
        synchronize_profiles(session, self.source)


class UserGroupMappingRefreshRequired(Hook):
    __regid__ = 'security_profile.gives_membership_update_hook'
    events = ('after_add_relation', 'before_delete_relation')
    __select__ = Hook.__select__ & match_rtype('gives_membership', 'has_security_profile')

    def __call__(self):
        operation = UpdateUserGroups.get_instance(self._cw)
        if self.rtype == 'gives_membership':
            profile = self._cw.entity_from_eid(self.eidfrom)
            for user in profile.reverse_has_security_profile:
                operation.add_data(user.eid)
        else: # CWUser has_security_profile SecurityProfile
            operation.add_data(self.eidfrom)


class SetDefaultValueForProfileDn(Hook):
    __regid__ = 'security_profile.set_default_value_for_profile_dn'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & is_instance('SecurityProfile')

    def __call__(self):
        if not self.entity.dn:
            self.entity.set_attributes(dn=self.entity.name)


class UpdateUserGroups(DataOperationMixIn, Operation):
    new_groups_rql = ('Any G,N WHERE G name N,'
                      'U has_security_profile P, '
                      'P gives_membership G, '
                      'NOT G name in ("users", "managers"), '
                      'U eid %(eid)s')

    def precommit_event(self):
        for user_eid in self.get_data():
            if not self.session.deleted_in_transaction(user_eid):
                user = self.session.entity_from_eid(user_eid)
                self.info('update_groups for user %s', user.login)
                self._update_user_groups(user_eid)

    def _update_user_groups(self, user_eid):
        '''
        Updates the groups in which the user should belong wrt its
        SecurityProfiles
        @param user_eid: eid of the current user
        '''
        session = self.session
        user = session.entity_from_eid(user_eid)

        # get user current groups
        # (remove 'users' as it is not handled with security profiles)
        user_groups = set(group for group in user.in_group if group.name != 'users')
        current_groups = set(group.eid for group in user_groups)

        eid_name_map = dict((group.eid, group.name) for group in user_groups)

        # get groups associated to security profiles
        new_groups = set()
        for groupeid, name in session.execute(self.new_groups_rql,
                                              {'eid': user_eid}).rows:
            new_groups.add(groupeid)
            eid_name_map[groupeid] = name

        # groups to delete
        to_delete = current_groups - new_groups

        self.info('user %s: groups to delete: %s', user.login, [eid_name_map[delete]
                                                                for delete in to_delete])
        if to_delete:
            groups = ','.join(str(eid) for eid in to_delete)
            rql = 'DELETE U in_group G WHERE U eid %%(eid)s, G eid IN (%s)' % groups
            session.execute(rql, {'eid': user_eid})

        # groups to add
        to_add = new_groups - current_groups

        self.info('user %s: groups to add   : %s', user.login, [eid_name_map[add]
                                                                for add in to_add])
        if to_add:
            groups = ','.join(str(eid) for eid in to_add)
            rql = 'SET U in_group G WHERE U eid %%(eid)s, G eid IN (%s)' % groups
            session.execute(rql, {'eid': user_eid})


def synchronize_profiles(session, source):
    '''
    Synchronize profiles defined in DB wrt the ones defined in the ldap
    '''
    logger = logging.getLogger('cubicweb.securityprofile')
    logger.info('start synchronize profiles')

    # get profiles from ldap
    repo = session.repo
    cnx = repo.sources_by_uri[source.uri].get_connection().cnx
    filters = repo.config['ldap-profile-filter']
    membership_attr = repo.config['ldap-profile-member-attribute']

    ldap_profiles = {}
    for profile in get_profiles(cnx,
                                source.user_base_dn,
                                source.user_base_scope,
                                filters,
                                ('cn', 'description', membership_attr)):
        ldap_profiles[profile['dn']] = profile

    # update / create / delete profiles wrt profiles defined in DB
    to_delete = []
    profiles_to_delete = []
    cw_profiles = session.execute('Any P WHERE P is SecurityProfile')
    for cw_profile in cw_profiles.entities(0):

        if cw_profile.dn in ldap_profiles:

            # profile is in DB and in LDAP --> update
            attrs = ldap_profiles.pop(cw_profile.dn)
            cw_profile.set_attributes(name=attrs['cn'],
                                      description=attrs.get('description', u''))
            set_profile_users(source, session, attrs, membership_attr)

        else:
            # profile is in DB but not in LDAP --> delete
            to_delete.append(str(cw_profile.eid))
            profiles_to_delete.append(cw_profile.name)

    for attrs in ldap_profiles.itervalues():

        # profile is not in DB but is in ldap --> create
        if 'description' not in attrs:
            attrs['description'] = u''

        logger.info('synchronize profiles: inserting %s', attrs['cn'])
        session.execute('INSERT SecurityProfile X: '
                        'X dn %(dn)s, '
                        'X name %(cn)s, '
                        'X description %(description)s',
                        attrs)

        # link users to new profile
        set_profile_users(source, session, attrs, membership_attr)

    if to_delete:
        logger.info('synchronize profiles: delete %s', profiles_to_delete)
        session.execute('DELETE SecurityProfile P WHERE P eid IN (%s)' % ','.join(to_delete))

    session.commit()
    session.set_cnxset()

def set_profile_users(source, session, profile_attrs, membership_attr):
    '''
    Set or delete relations between a security profile and its associated users
    '''
    logger = logging.getLogger('cubicweb.securityprofile')

    # get ldap members
    ldap_members = profile_attrs.get(membership_attr, [])
    if isinstance(ldap_members, unicode):
        ldap_members = [ldap_members]

    ldap_member_eids = []
    repo = session.repo
    for member in ldap_members:
        # A divergence of the source filter and security profile filter
        # can yield divergent sets of users.
        # Hence, we must carefully ask to NOT create the entity if it does not exist yet
        # and do nothing in this case but complain.
        usereid = repo.extid2eid(source, str(member), 'CWUser', session, insert=False)
        if usereid is not None:
            ldap_member_eids.append(usereid)
        else:
            logger.warning('user %s seen by security_profile does not exist '
                           'in the repository; check your filters', member)

    ldap_member_names = [session.entity_from_eid(eid).login
                         for eid in ldap_member_eids]

    profile_cn = profile_attrs['cn']
    logger.debug('profile: %s, ldap members: %s', profile_cn, ldap_member_names)

    # get cw members
    profile_dn = profile_attrs['dn']
    cw_profile = session.execute('Any P WHERE P dn %(dn)s', {'dn': profile_dn}).get_entity(0, 0)
    cw_member_eids = [u.eid for u in cw_profile.reverse_has_security_profile]
    cw_member_names = [u.login for u in cw_profile.reverse_has_security_profile]

    logger.debug('profile: %s, cw members: %s', profile_cn, cw_member_names)
    eids_to_add = set(ldap_member_eids) - set(cw_member_eids)
    eids_to_remove = set(cw_member_eids) - set(ldap_member_eids)

    if eids_to_remove or eids_to_add:

        # add users
        to_add = set(ldap_member_names) - set(cw_member_names)
        logger.info('profile: %s, members to add: %s', profile_cn, list(to_add))
        for eid in eids_to_add:
            # The NOT clause below is crucial, as we have seen on site
            # some user DN in ldap which where listed in the Profile
            # group, but where not CWUsers (because they did not match the
            # filters configured in ldapuser). Such users could show up in
            # the relation table but would not appear in the
            # cw_users_with_profile list.
            session.execute('SET U has_security_profile P '
                            'WHERE U eid %(u)s, P eid %(p)s, '
                            '      NOT U has_security_profile P',
                            {'u': eid, 'p': cw_profile.eid})

        # remove users
        to_remove = set(cw_member_names) - set(ldap_member_names)
        logger.info('profile: %s, members to remove: %s', profile_cn, list(to_remove))
        for eid in eids_to_remove:
            session.execute('DELETE U has_security_profile P '
                            'WHERE U eid %(u)s, P eid %(p)s',
                            {'u': eid, 'p': cw_profile.eid})

        members = session.execute('Any U '
                                  'WHERE U has_security_profile P, '
                                  '      P eid %(eid)s',
                                  {'eid': cw_profile.eid}).entities()
        logger.info('profile: %s, members: %s', profile_cn, [m.login for m in members])

def get_profiles(cnx, base, scope, searchstr, attrs):
    '''
    Get Security Profiles from ldap wrt instance config
    '''
    import ldap
    logger = logging.getLogger('cubicweb.securityprofile')
    try:
        res = cnx.search_s(base, scope, searchstr, attrs)
    except ldap.PARTIAL_RESULTS:
        res = cnx.result(all=0)[1]
    except ldap.NO_SUCH_OBJECT:
        logger.warning('ldap NO SUCH OBJECT')
        return []

    result = []
    for rec_dn, rec_dict in res:
        # When used against Active Directory, "rec_dict" may not be
        # be a dictionary in some cases (instead, it can be a list)
        # An example of a useless "res" entry that can be ignored
        # from AD is
        # (None, ['ldap://ForestDnsZones.PORTAL.LOCAL/DC=ForestDnsZones,DC=PORTAL,DC=LOCAL'])
        # This appears to be some sort of internal referral, but
        # we can't handle it, so we need to skip over it.
        try:
            items = rec_dict.items()
        except AttributeError:
            # 'items' not found on rec_dict, skip
            continue
        for key, value in items: # XXX syt: huuum ?
            if not isinstance(value, str):
                try:
                    for i in range(len(value)):
                        value[i] = unicode(value[i], 'utf-8')
                except:
                    pass
            if isinstance(value, list) and len(value) == 1:
                rec_dict[key] = value = value[0]
        rec_dict['dn'] = unicode(rec_dn)
        result.append(rec_dict)
    return result

for cls in (UserGroupMappingRefreshRequired,
            SetDefaultValueForProfileDn,
            UpdateUserGroups):
    set_log_methods(cls, logging.getLogger('cubicweb.securityprofile'))

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (SecurityProfileLdapParser,))
    if 'parsers' in vreg:
        vreg.register_and_replace(SecurityProfileLdapParser, DataFeedLDAPAdapter)
    vreg.warning('no parsers in registry yet, SecurityProfileParser not registered')
