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
