import requests
import re
from datetime import datetime, timedelta
import pandas as pd
import json

#Base URLS

listOfTournamentsURL = "https://www.24live.com/api/match-list-category/10?lang=en&type=all&sort=alpha&from=CURRENTDATE%2000:00:00&to=CURRENTDATE%2023:59:59"
listOfMatchesURL = "https://www.24live.com/api/match-list-data/10?lang=en&type=all&subtournamentIds=COMMASEPARATEDTOURNAMENTIDS&sort=alpha&short=1&from=CURRENTDATE%2000:00:00&to=CURRENTDATE%2023:59:59"

baseMatchURL = "https://www.24live.com/api/match/MATCHID"
todayDate = datetime.now().strftime("%x").replace("/","_")  



allMatchdf = pd.DataFrame(columns=['Date','Tournament',"Court Type",'Player1', 'Player1_Rank', 'Player1_RankingPoints', 'Player2', 'Player2_Rank', 'Player2_RankingPoints','Best of Sets','ScoreProgression_Games','ScoreProgression_Sets'])

# Loop through each day in the calendar from current date back to June 2022 when details are not available earlier than that (as of 21/02/24)
for dayNumber in range(1,600):
    d = datetime.today() - timedelta(days=dayNumber)
    d = d.strftime('%Y-%m-%d').replace("/","-") 

    currentTournamentList = listOfTournamentsURL.replace('CURRENTDATE',d)

    tournamentList = requests.get(currentTournamentList)
    tournamentList = [i for i in tournamentList.json() if i["category_name"]=="ATP" and i["singles_doubles"]==1]

    tournamentList = [{key: value for key, value in zip(i.keys(), i.values()) if "sub_tournament_id" in key or "tournament_name" in key or "sub_tournament_ground" in key} for i in tournamentList]

    tournIDList = [str(i["sub_tournament_id"])+"," for i in tournamentList]
    tournIDList = "".join(tournIDList)[:-1]
    
    currentMatchListURL = listOfMatchesURL.replace("CURRENTDATE",d)
    currentMatchListURL = currentMatchListURL.replace("COMMASEPARATEDTOURNAMENTIDS",tournIDList)

    currentDayMatchList = requests.get(currentMatchListURL).json()
    allMatchIds = [i["id"] for i in currentDayMatchList]
    
    #allMatches = []
    #allMatchIds = []

# Loop through match ids
    for id in allMatchIds:
        matchURL = baseMatchURL.replace("MATCHID",str(id))
        matchResponse = requests.get(matchURL)
        try:
            jsonResponse = matchResponse.json()
        except requests.exceptions.JSONDecodeError:
            print("jsonError")
            continue
        # Extract player name, rank and rank points
        if jsonResponse["code_state"]!="ended":
            print("no match data for "+str(id))
            continue
        
        player1={}
        player2={}
        player1["name"]  = re.split("\(",[player for player in jsonResponse["participants"] if player["type"]=="home_team"][0]["name"])[0].strip()
        player2["name"] = re.split("\(",[player for player in jsonResponse["participants"] if player["type"]=="away_team"][0]["name"])[0].strip()
        if "/" in player1["name"]:
            continue        
        # if either player isn't ranked then ignore match and continue
        try:
            player1["rankingPoints"] = [points for points in jsonResponse["tennis_rankings"] if points["info"]["name"]==player1["name"]][0]["points"]
        except IndexError:
            continue
        try:
            player2["rankingPoints"] = [points for points in jsonResponse["tennis_rankings"] if points["info"]["name"]==player2["name"]][0]["points"]
        except IndexError:
            continue
        player1["ranking"] = [points for points in jsonResponse["tennis_rankings"] if points["info"]["name"]==player1["name"]][0]["ranking"]
        player2["ranking"] = [points for points in jsonResponse["tennis_rankings"] if points["info"]["name"]==player2["name"]][0]["ranking"]
        # Extract game timeline from 
        matchData = jsonResponse["live_timelines"]
        matchData = [[item["home_score"],item["away_score"]] for item in matchData if item["type"] =="period_score" or item["type"]=="period_start"]
        matchData = [score for score in matchData if score != [None,None]]
        matchDataBySet = []
        for i,score in enumerate(matchData):

            if i==0:
                matchDataBySet.append([score])
            else:
                if sum(matchData[i])>sum(matchData[i-1]):
                    matchDataBySet[-1].append(score)
                else:
                    matchDataBySet.append([score])

        numberOfSets = len(matchDataBySet)
        setScores = []
        for i in range(0,numberOfSets):
            setScores.append([0,0])

        for i,score in enumerate(matchDataBySet):

            try:
                if score[-1][0]>score[-1][1]:
                #setScores[i][0]+=1
                    setScores = [[x[0]+1,x[1]] if count>=i else x for count,x in enumerate(setScores) ]
            except IndexError:
                print("Error for match data "+str(id))
                continue
            if score[-1][1]>score[-1][0]:
                setScores = [[x[0],x[1]+1] if count>=i else x for count,x in enumerate(setScores) ]
        try:
            bestOf = 3 if max(setScores[-1])==2  else 5 
        except IndexError:
            print("Error for match data "+str(id))
            continue
        allMatchdf.loc[0 if pd.isnull(allMatchdf.index.max()) else allMatchdf.index.max() + 1]=[d,jsonResponse["sub_tournament_name"],jsonResponse["sub_tournament_ground"].replace("web.ground-type_",""),player1["name"],player1["ranking"],player1["rankingPoints"],player2["name"],player2["ranking"],player2["rankingPoints"],bestOf,matchDataBySet,setScores]
        if len(allMatchdf.index) % 100 == 0:
            allMatchdf.to_csv("matchData_test_"+todayDate+".json", sep=',', index=False, encoding='utf-8')
allMatchdf.to_csv("matchData_test_"+todayDate+".json", sep=',', index=False, encoding='utf-8')
      
        
