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

"""cubicweb-securityprofile schema"""
from yams.buildobjs import (EntityType, String, SubjectRelation, RelationDefinition) #pylint:disable-msg=E0611
from cubicweb.schema import RQLConstraint, RQLVocabularyConstraint
_ = unicode

class SecurityProfile(EntityType):
    """
    A security profile : a CWUser linked to such a profile is made a
    member of the CWGroups linked to the profile.
    
    In the context of TPM Security Central, ADAM users are memberOf a
    number of such profiles. The ldap-profile configuration variable
    is used to do the mapping.
    """
    __permissions__ = {'read': ('users', 'managers'),
                       'add': ('managers', 'profile_managers'),
                       'update': ('managers', 'profile_managers'),
                       'delete': ('managers', 'profile_managers')}
    name = String(maxsize=16, required=True,
                  description=_('the name of the profile'))
    dn = String(maxsize=255, unique=True,
                description=_('the dn of the profile in the LDAP source, if in use. '
                              'This is an internal attribute managed and used by hooks'))
    description = String(maxsize=255)
    gives_membership = SubjectRelation('CWGroup', cardinality='**',
                                       constraints = [RQLConstraint('NOT O name "managers"'),],
                                      __permissions__={
                                           'read': ('users', 'managers'),
                                           'add': ('managers', 'profile_managers'),
                                           'delete': ('managers', 'profile_managers')
                                           })

class has_security_profile(RelationDefinition):
    subject = 'CWUser'
    object = 'SecurityProfile'
    __permissions__ = {
        'read': ('users', 'managers'),
        'add': ('managers', 'profile_managers'),
        'delete': ('managers', 'profile_managers')
        }
