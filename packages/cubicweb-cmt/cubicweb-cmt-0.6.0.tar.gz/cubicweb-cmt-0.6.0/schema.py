# copyright 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-cmt schema"""


from yams.buildobjs import RelationDefinition, EntityType, String

from cubicweb.schema import ERQLExpression

from cubes.shoppingcart.schema import ShoppingItem
from cubes.conference.schema import user_owns_subject,  user_owns_object

ShoppingItem.get_relation('quantity').default = 1

class book_conf(RelationDefinition):
    subject = 'ShoppingCart'
    object = 'Conference'
    cardinality = '1*'

class has_shoppingitemtype(RelationDefinition):
    subject = 'Conference'
    object = 'ShoppingItemType'
    cardinality = '*1'

class BillingAddress(EntityType):
    __permissions__ = {
        'read':   ('managers', ERQLExpression('X owned_by U'),),
        'add':    ('managers', 'users',),
        'update': ('managers', 'owners',),
        'delete': ('managers', 'owners',),
        }
    organisation = String(required=True, maxsize=256)
    street = String(required=True, maxsize=256)
    street2 = String(maxsize=256)
    postalcode = String(required=True, maxsize=256)
    city = String(required=True, maxsize=256)
    country = String(required=True, maxsize=256)
    your_ref = String(maxsize=256)

class billing(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users'),
        'add':    ('managers', user_owns_subject()),
        'delete': ('managers', user_owns_subject()),
        }
    subject = 'ShoppingCart'
    object = 'BillingAddress'
    cardinality = '?1'
    composite = 'subject'
