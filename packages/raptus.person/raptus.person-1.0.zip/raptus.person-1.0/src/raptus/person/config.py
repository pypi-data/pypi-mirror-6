"""Common configuration constants
"""

from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.person'

security = ModuleSecurityInfo('raptus.person.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = {
    'Person': 'raptus.person: Add Person'
}

for perm in ADD_PERMISSION.values():
    setDefaultRoles(perm, ('Manager', 'Contributor',))