#
# This file is part of Efforia project.
#
# Copyright (C) 2011-2013 William Oliveira de Lagos <william@efforia.com.br>
#
# Efforia is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Efforia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Efforia. If not, see <http://www.gnu.org/licenses/>.
#

from django.db.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context,Template
from datetime import date

locale = settings.LOCALE_DATE

class Deliverable(Model):
    name = CharField(default='((',max_length=50)
    user = ForeignKey(User,related_name='+')
    product = IntegerField(default=1)
    mail_code = CharField(default='',max_length=100)
    height = IntegerField(default=1)
    length = IntegerField(default=1)
    width = IntegerField(default=1)
    weight = IntegerField(default=10)
    value = FloatField(default=0.0)
    date = DateTimeField(default=date.today(),auto_now_add=True)
    def token(self): return self.name[:2]
    def name_trimmed(self): return self.name.split(';')[0][1:]
    def month(self): return locale[self.date.month-1]