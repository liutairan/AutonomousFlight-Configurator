#!/usr/bin/env python3

'''
    This file is part of AutonomousFlight Configurator.

    AutonomousFlight Configurator is free software: you can
    redistribute it and/or modify it under the terms of the
    GNU General Public License as published by the Free Software
    Foundation, either version 3 of the License, or (at your
    option) any later version.

    AutonomousFlight Configurator is distributed in the hope
    that it will be useful, but WITHOUT ANY WARRANTY; without
    even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE.  See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public
    License along with AutonomousFlight Configurator. If not,
    see <https://www.gnu.org/licenses/>.
'''

__author__ = "Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "GPLv3"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"

import json
import io

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

def writeSettingFile(data):
    with io.open('Default_Settings.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))

def readDefaultSettingFile():
    with open('Default_Settings.json') as data_file:
        data_loaded = json.load(data_file)
    return data_loaded

def readUserSettingFile():
    with open('User_Settings.json') as data_file:
        data_loaded = json.load(data_file)
    return data_loaded

def writeSettingItems(itemDict):
    oldSettings = readSettingFile()
    newSettings = oldSettings
    for tempDict in itemDict:
        newSettings[tempDict] = itemDict[tempDict]
    writeSettingFile(newSettings)

def readSettingItems(itemList):
    settings = readSettingFile()
    retDict = {}
    for item in itemList:
        retDict[item] = settings[item]
    return retDict

if __name__ == "__main__":
    # Sample
    # cfgData = {"PID Tuning": {
    #                "Roll": {"P":40, "I":30, "D":23},
    #                "Pitch": {},
    #                "Yaw": {},
    #                "Position Z": {},
    #                "Velocity Z": {},
    #                "Heading": {},
    #                "Position XY": {},
    #                "Velocity XY": {},
    #                "Surface": {},
    #                "Level": {},
    #                "Roll rate": {},
    #                "Pitch rate": {},
    #                "Yaw rate": {},
    #                "Manual Roll rate": {},
    #                "Manual Pitch rate": {},
    #                "Manual Yaw rate": {},
    #                "MagHold rate": {}
    #            }
    #            }
    # writeSettingFile(cfgData)
    rec = readDefaultSettingFile()
    print(rec)
