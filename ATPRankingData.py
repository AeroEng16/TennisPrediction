import requests
import bs4 
import pandas as pd
from datetime import datetime, timedelta

todayDate = datetime.now().strftime("%x").replace("/","_")  

baseURL = "https://www.tennisexplorer.com/ranking/atp-men/?page=PageNumber"
df = pd.DataFrame(columns=['Name','Rank'])

for i in range(1,8):
    modURL = baseURL.replace("PageNumber",str(i))

    main = requests.get(modURL)

    soup = bs4.BeautifulSoup(main.content)

    names = soup.find_all("td", {"class": "t-name"})
    ranks = soup.find_all("td", {"class": "rank first"})

    subsetNames = names[0:len(ranks)]

    for i,name in enumerate(subsetNames):
        df.loc[0 if pd.isnull(df.index.max()) else df.index.max() + 1]=[name.get_text(),ranks[i].get_text()]


df.to_csv("ATPRankings"+todayDate+"basicData.json", sep=',', index=False, encoding='utf-8')
