import requests
import json
import pandas as pd
from tabulate import tabulate

class Player:
    def __init__(self,apiKey):
        self.changed = {
            "BATTLEGROUND" : "WARLORDS",
            "MCGO" : "COPSANDCRIMS",
            "MAIN" : "GENERAL",
            "SURVIVALGAMES" : "BLITZ",
            "LEGACY" : ['ARENA', 'QUAKE','WALLS', 'VAMPIREZ', 'GINGERBREAD', 'PAINTBALL']
        }
        self.apiKey = apiKey
        self.uuid = self.getInfo(f"https://api.hypixel.net/key?key={self.apiKey}")["record"]["owner"]
        self.currentServer = None
        self.playerAchievementsOneTime = None
        self.playerAchivementsTiered = None
        self.allAchievements = self.getAllAchievements()

    def getInfo(self, call):
        r = requests.get(call)
        return r.json()
    
    def getServer(self):
        server = f"https://api.hypixel.net/status?key={self.apiKey}&uuid={self.uuid}"
        a = self.getInfo(server)
    
        if a['session']['online'] == False:
            return None
        else:
            return (str(a['session']['gameType'])).replace('_','')

    def getAllAchievements(self):
        achivements_link = "https://api.hypixel.net/resources/achievements"
        all_achievements = self.getInfo(achivements_link)
        all_achievements_one_time = all_achievements['achievements']
        return all_achievements_one_time

    def getAchievementsFromCurrentServer(self,server):
        thisServer = self.currentServer
        if server is not None:
            thisServer = server
        elif self.currentServer in self.changed:
            thisServer = self.changed[self.currentServer]
        try:
            self.playerAchievementsOneTime = pd.read_json(json.dumps(self.allAchievements[thisServer.lower()]['one_time']))
            self.playerAchievementsTiered = pd.read_json(json.dumps(self.allAchievements[thisServer.lower()]['tiered']))
        except Exception:
            pass
        return self.playerAchievementsOneTime


    def getPlayerAchievements(self):
        uuid_link = f"https://api.hypixel.net/player?key={self.apiKey}&uuid={self.uuid}"
        return self.getInfo(uuid_link)

    def removeAchievementsObtained(self,server):
        a = []
        if server is not None:
            thisServer = server
        else:
            thisServer = self.currentServer

        for ach in self.getPlayerAchievements()['player']['achievementsOneTime']:
            if ach.startswith(thisServer.lower()):
                a.append(ach.replace(thisServer.lower() + "_",''))

        for x in list(self.playerAchievementsOneTime.columns):
            if x.lower() in a:
                self.playerAchievementsOneTime = self.playerAchievementsOneTime.drop([x], axis=1) 
        self.playerAchievementsOneTime = self.playerAchievementsOneTime.loc[:, ~(self.playerAchievementsOneTime == True).any()]


    def removeAchivementsObtainedTiered(self,server):
        if not self.playerAchievementsTiered.empty:
            
            if server is not None:
                thisServer = server
            else:
                thisServer = self.currentServer

            b = self.getPlayerAchievements()['player']['achievements']
            a = {}
            for ach in b:
                if ach.startswith(thisServer.lower()):
                    a[ach.replace(thisServer.lower() + "_",'',1)] = b[ach]

            self.playerAchievementsTiered.loc['points'] = None
            for x in list(self.playerAchievementsTiered.columns):
                c = self.playerAchievementsTiered.loc["tiers",x]
                d = []
                try:
                    if a[x.lower()] >= c[len(c)-1]["amount"]:
                        c = True
                        d = True
                        greatest = a[x.lower()]
                    else:
                        for y in range(len(c[:])):
                            if a[x.lower()] >= c[y]['amount']:
                                d.insert(y,str(c[y]['points'])+ "/" + str(c[y]['points']))
                                c[y] = "Completed"
                                greatest = c[y+1]['amount']
                            else:
                                try:
                                    greatest = c[0]['amount']
                                except Exception:
                                    pass
                                c[y] = str(a[x.lower()]) + "/" + str(c[y]['amount'])
                                d.insert(y,'Incomplete')
                          
                except Exception:
                    greatest = c[0]['amount']
                    for y in range(len(c[:])):
                        c[y] =  "0/" + str(c[y]['amount'])
                        d.insert(y,'Incomplete')
                
                self.playerAchievementsTiered.loc["tiers",x] = c
                self.playerAchievementsTiered.loc["points",x] = d
                self.playerAchievementsTiered.loc['description',x] = self.playerAchievementsTiered.loc['description',x].replace("%s", str(greatest))
            self.playerAchievementsTiered = self.playerAchievementsTiered.loc[:, ~(self.playerAchievementsTiered == True).any()]


    def formatNicerLol(self):
        self.playerAchievementsOneTime = None 
        self.playerAchivementsTiered = None
        server = self.getServer()
        if self.currentServer != server:
            self.currentServer = server
            returnString = ""
            if self.currentServer == "LEGACY":
                for x in range(len(self.changed["LEGACY"])):
                    self.getAchievementsFromCurrentServer(self.changed["LEGACY"][x])
                    self.removeAchievementsObtained(self.changed["LEGACY"][x])
                    self.removeAchivementsObtainedTiered(self.changed["LEGACY"][x])
                    returnString+= "\n\n" + self.changed["LEGACY"][x] + "\n"
                    if self.playerAchievementsOneTime.empty:
                        returnString = "Current server has no remaining achievements"
                    else:
                        returnString += "Tiered Achievements: \n"
                        b = self.playerAchievementsTiered
                        b.columns = b.loc["name",:].tolist()
                        b = b.transpose()
                        b = b[['description','tiers','points']]
                        returnString += tabulate(b, headers='keys') + "\n\nOne Time Achievements: \n"

                        
                        a = self.playerAchievementsOneTime
                        a.columns = a.loc["name",:].tolist()
                        a = a.transpose()
                        a = a[['points','description']]
                        returnString += tabulate(a, headers='keys')
                                              
            else:
                if (self.getAchievementsFromCurrentServer(None) is not None):
                    self.removeAchievementsObtained(None)
                    self.removeAchivementsObtainedTiered(None)
                    if self.playerAchievementsOneTime.empty:
                        returnString = "Current server has no remaining achievements"
                    else:
                        returnString = "Tiered Achievements: \n"
                        b = self.playerAchievementsTiered
                        b.columns = b.loc["name",:].tolist()
                        b = b.transpose()
                        b = b[['description','tiers','points']]
                        returnString += tabulate(b, headers='keys') + "\n\nOne Time Achievements: \n"

                        
                        a = self.playerAchievementsOneTime
                        a.columns = a.loc["name",:].tolist()
                        a = a.transpose()
                        a = a[['points','description']]
                        returnString += tabulate(a, headers='keys')

                else:
                    returnString = "Current server has no achievements"
        
            return returnString