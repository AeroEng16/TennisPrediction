import pandas as pd

basicRankingInfo = pd.read_csv("ATPRankings02_24_24basicData.csv")
detailedRankingInfo = pd.read_csv("playerData_02_19_24.csv")

detailedMatchData = pd.read_csv("matchData_02_24_24.csv")

additionalMatchData2023 = pd.read_csv("githubATPMatchData_2023.csv")

additionalMatchData2022 = pd.read_csv("githubATPMatchData_2022.csv")

print(list(additionalMatchData2023))

print(basicRankingInfo.head())
print(detailedMatchData.head())
print(detailedRankingInfo.head())
print(additionalMatchData2023.head())