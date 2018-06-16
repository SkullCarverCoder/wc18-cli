import datetime
import dateutil.parser
import time
import pytz
from tzlocal import get_localzone
from collections import defaultdict
import requests

def GetData():
    url = "https://raw.githubusercontent.com/lsv/fifa-worldcup-2018/master/data.json"
    response = requests.get(url)
    data = response.json()
    return data

data = GetData()

def LoadTeam(**kwargs):
    global data
    matchlist = []
    found = False
    if 'Country' in kwargs:
        Country = kwargs['Country']
        for country in data['teams']:
            if Country == country['name']:
                Nation_id = country['id']
                found = True
                break
        if found is False :
            raise ValueError('Error: Team Not Found!')
        Nation_group = ''
        for c in range(0, 8):
            for match in data['groups'][chr(ord('a') + c)]['matches']:
                if Nation_id == match['home_team'] or Nation_id == match['away_team']:
                    Nation_group = chr(ord('A') + c)
                    matchlist.append(match)
        return Team(Country, Nation_id, Nation_group, matchlist)
    elif 'ID' in kwargs:
        Nation_id = int(kwargs['ID'])
        for country in data['teams']:
            if Nation_id == country['id']:
                Country = country['name']
                found = True
                break
        if found is False:
            raise ValueError('Error: Team Not Found!')
        for c in range(0,8):
            for match in data['groups'][chr(ord('a')+c)]['matches']:
                if Nation_id == match['home_team'] or Nation_id == match['away_team']:
                    Nation_group = chr(ord('A') + c)
                    matchlist.append(match)
        return Team(Country, Nation_id, Nation_group, matchlist)

def IsoToDatetime(s):
    d = dateutil.parser.parse(s)
    return d

class Group():
    def __init__(self, letter,Matches, Members):
        self.Letter = letter
        self.__Matches = Matches
        self.Members = Members
        self.Nations = Members.values()
        self.Matches = []

    @property
    def _Matches(self):
        return self.__Matches



    def Table(self):
        table = {self.Members[team]: defaultdict(int)  for team in self.Members.keys()}
        for match in filter(lambda m: m['finished'] is True, self.__Matches):

            home_team = self.Members[match["home_team"]]
            table[home_team]['played'] += 1
            table[home_team]['scored'] += match["home_result"]
            table[home_team]['conceded'] += match["away_result"]

            away_team = self.Members[match["away_team"]]
            table[away_team]['played'] += 1
            table[away_team]['scored'] += match["away_result"]
            table[away_team]['conceded'] += match["home_result"]

            if match["home_result"] > match["away_result"]:
                table[home_team]['points'] += 3
            elif match["home_result"] < match["away_result"]:
                table[away_team]["points"] += 3
            else:
                table[home_team]['points'] += 1
                table[away_team]['points'] += 1

        return table
    def group_table_as_str(self):
        table = self.Table()
        ret_str = 'GROUP {0: <20} MP GF GA PTS\n'.format(self.Letter.upper())
        ret_str += '-' * 39
        for team, info in sorted(table.items(), key=lambda k: (k[1]['points'], k[1]['scored'] - k[1]['conceded']), reverse=1):
            ret_str += "\n{0: <26}  {1}  {2}  {3}  {4}".format(
                team, info['played'], info['scored'], info['conceded'], info['points'])
        return ret_str

class Team():
    def __init__(self, Nation, _id, Group, Matches):
        self.Nation = Nation
        self.id = _id
        self.__Matches = Matches
        self.Matches = []
        self.Group = Group

    @property
    def _Matches(self):
        return self.__Matches

    def LoadMatches(self):
        temp = []
        Matchdates = []
        Timestamp = pytz.UTC.localize(datetime.datetime.now())
        systimezone = get_localzone()  # System non-DST timezone
        for match in self.__Matches:
            Match_date = IsoToDatetime(match['date'])
            Matchdates = [Match_date]
            Matchdate = Match_date.astimezone(systimezone)
            Matchdate = Matchdate.strftime("%A, %d. %B %Y %I:%M%p")
            spacer = "-" * 61
            if self.id == match['home_team']:
                adversary = LoadTeam(ID=match['away_team'])
                adversary = adversary.Nation
                Prompt = '  {0} vs {1}'.format(self.Nation,adversary)
                if match['home_result'] != None or match['away_result'] != None:
                    Score = '{0} - {1}'.format(match['home_result'], match['away_result'])
                else:
                    Score = '0 - 0'
            if self.id == match['away_team']:
                adversary= LoadTeam(ID=match['home_team']).Nation
                Prompt = '  {0} vs {1}'.format(adversary,self.Nation)
                if match['home_result'] != None or match['away_result'] != None:
                    Score = '{0} - {1}'.format(match['home_result'], match['away_result'])
                else:
                    Score = '0 - 0'
            if match['finished'] == False and Match_date < Timestamp:
                status = 'Live'
            elif match['finished'] == False and Match_date > Timestamp:
                status = 'To be Played'
            else:
                status = 'Final'
            ResultString =f'''\n{spacer}\n{Prompt}\n     {Matchdate}\n         {Score}\n status: {status}\n
            '''
            temp.append(ResultString)
        self.Matches = temp
        self.SoonestMatch =self.nearest().strftime("%A, %d. %B %Y %I:%M%p")
    def __repr__(self):
        return f'{self.Nation}\'s team object'
    def __str__(self):
        self.LoadMatches()
        return f'''
Team: {self.Nation}
Group: {self.Group}
Matches:{" ".join(x for x in self.Matches)}'''

    def nearest(self):
        systimezone = get_localzone()  # System non-DST timezone
        now = pytz.UTC.localize(datetime.datetime.now())
        nearest = None
        timediff = None
        dates =[IsoToDatetime(match['date']).astimezone(systimezone)for match in self.__Matches]
        timediff = now - min(dates, key=lambda d: abs(d - now))
        timediff = timediff.days
        if timediff > 1:
            nearest = dates[dates.index(min(dates, key=lambda d: abs(d - now)))+1]
        else:
            nearest = min(dates, key=lambda d: abs(d - now))
        return nearest
