##
# Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from pypump.models import AbstractModel

class Place(AbstractModel):

    name = None
    longitude = None
    latitude = None

    def __init__(self, name=None, longitude=None, latitude=None, *args, **kwargs):
        super(Place, self).__init__(*args, **kwargs)
        self.name = name
        self.longitude = longitude
        self.latitude = latitude

    def __repr__(self):
        return "<{type} {name}>".format(type=self.TYPE, name=self.name)

    def unserialize(self, data):
        self.name = data.get("displayName", None)        
        if ("lon" in data and "lat" in data):
            self.longitude = float(data["lon"])
            self.latitude = float(data["lat"])
        
        elif "position" in data:
            position = data["position"][:-1]
            if position[1:].find("+") != -1:
                latitude = position.lstrip("+").split("+", 1)[0]
                self.latitude = float(latitude)

                self.longitude = float(position[1:].split("+", 1)[1])
            else:
                latitude = position.lstrip("+").split("-", 1)[0]
                self.latitude = float(latitude)

                self.longitude = float(position[1:].split("-", 1)[1])               

        else:
            self.longitude = None
            self.latitude = None

        return self
