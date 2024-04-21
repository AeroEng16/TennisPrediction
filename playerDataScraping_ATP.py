import requests
import re
import json
import datetime
import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}

apiLink = "https://atptour.com/en/-/www/rank/sglroll/200?v=1"

individualPlayerBaseURL = "https://www.atptour.com/en/-/www/stats/PLAYERID/YEAR/COURTTYPE?v=1"
year="all"  #year (e.g. 2024) or all
courtType = "all" #grass,clay,hard, carpet or all

playerDataSrc = requests.get(apiLink,headers=headers).json()
playerData = []
for i in playerDataSrc:

    filteredDataSet = {key: value for key, value in zip(i.keys(), i.values()) if "RankNo" in key or "Name" in key or "Points" in key or "PlayerId" in key or "Movement" in key}
    print(filteredDataSet["PlayerId"])
    for k,j in enumerate(["PLAYERID","YEAR","COURTTYPE"]):
        if k==0:
            localURL = individualPlayerBaseURL.replace(j,filteredDataSet["PlayerId"])
        elif k == 1:
            localURL = localURL.replace(j,year)
        elif k == 2:
            localURL = localURL.replace(j,courtType)

    responseIndividualPlayer = requests.get(localURL,headers=headers)
    servingStats = responseIndividualPlayer.json()["Stats"]["ServiceRecordStats"]
    recevingStats = responseIndividualPlayer.json()["Stats"]["ReturnRecordStats"]
    relevantServingStats = {key: value for key, value in zip(servingStats.keys(), servingStats.values()) if "Percentage" in key }
    relevantReceivingStats = {key: value for key, value in zip(recevingStats.keys(), recevingStats.values()) if "Percentage" in key }
    overallPlayerData = {**filteredDataSet,**relevantServingStats,**relevantReceivingStats}
    #print(json.dumps(overallplayerData, indent=2))
    playerData.append(overallPlayerData)


playerDF = pd.DataFrame(playerData)

todayDate = datetime.datetime.now().strftime("%x").replace("/","_")  
playerDF.to_csv("playerData_Year_"+year+"_courtType_"+courtType+"_"+todayDate, sep=',', index=False, encoding='utf-8')


