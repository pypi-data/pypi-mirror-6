# copyright 2004-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of yams.
#
# yams is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# yams is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with yams. If not, see <http://www.gnu.org/licenses/>.
from yams.buildobjs import EntityType, SubjectRelation, String, RelationDefinition

class Person(EntityType):
    firstname = String()
    knows = SubjectRelation('Person')
    works_for = SubjectRelation('Company')

class Student(Person):
    __specializes_schema__ = True

class Company(EntityType):
    name = String()

class SubCompany(Company):
    __specializes_schema__ = True

class Division(Company):
    __specializes_schema__ = True
    division_of = SubjectRelation('Company')

class SubDivision(Division):
    __specializes_schema__ = True

# This class doesn't extend the schema
class SubSubDivision(SubDivision):
    pass

class custom_attr(RelationDefinition):
    subject = 'Person'
    object = 'String'
    __permissions__ = {'read': ('managers', ),
                       'update': ('managers', )}
