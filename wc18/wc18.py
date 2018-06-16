#!/usr/bin/env python
import os
import requests
import click
import datetime
import dateutil.parser
import time
import pytz
from tzlocal import get_localzone
import json


def GetData():
    url = "https://raw.githubusercontent.com/lsv/fifa-worldcup-2018/master/data.json"
    response = requests.get(url)
    data = response.json()
    return data


def load_json(file):
    """Load JSON file at app start"""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, file)) as jfile:
        data = json.load(jfile)
    return data


TEAM_DATA = load_json("countries.json")["teams"]
COUNTRIES = {team["name"]: team["id"] for team in TEAM_DATA}

data = GetData()


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


def IsoToDatetime(s):
    d = dateutil.parser.parse(s)
    return d


# Load Team info for initialation of class

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


def LoadStats(team):
    global data
    Qualified = None
    GoalCount = 0
    MatchesWon = 0
    MatchesLost = 0
    for key in data['groups'].keys():
        if key == team.Group.lower() and data['groups'][key]['winner']:
            if data['groups'][key]['winner'] == team.id:
                Qualified = True
            else:
                Qualified = False
    for match in team._Matches:
        if team.id == match['home_team'] and match['home_result']:
            GoalCount += match['home_result']
            if match['home_result'] > match['away_result'] and match['finished'] is True:
                MatchesWon += 1
            elif match['home_result'] < match['away_result'] and match['finished'] is True:
                MatchesLost += 1
        elif team.id == match['away_team'] and match['away_result']:
            GoalCount += match['away_result']
            if match['home_result'] > match['away_result'] and match['finished'] is True:
                MatchesLost += 1
            elif match['home_result'] < match['away_result'] and match['finished'] is True:
                MatchesWon += 1
    if Qualified is None:
        Qualified = 'Alive'
    elif Qualified is True:
        Qualified = 'Passed'
    else:
        Qualified = 'Eliminated'
    return {
    'Status': Qualified,
    'Goals': GoalCount,
    'Matches Won': MatchesWon,
    'Matches Lost': MatchesLost
    }


# Python object of a team with internal methods given the data
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
        # self.SoonestMatch = nearest(Matchdates, Timestamp).astimezone(systimezone).strftime("%A, %d. %B %Y %I:%M%p")
    def __repr__(self):
        return f'{self.Nation}\'s team object'
    def __str__(self):
        self.LoadMatches()
        return f'''
Team: {self.Nation}
Group: {self.Group}
Matches:{" ".join(x for x in self.Matches)}'''


@click.command()
@click.option('--country', type=click.Choice(COUNTRIES.keys()), help='Show the stats of the country and its matches')
# @click.option('--group', type=click.Choice(COUNTRIES.keys()), help='Show the stats of the country and its matches')
@click.option('--allmatches', default=False ,help='Show the stats plus all the matches of the team')
def main(country, allmatches):
    if country and allmatches:
        team = LoadTeam(Country=country)
        stats = LoadStats(team)
        team.LoadMatches()
        print("--------------------------------------------------------------")
        click.echo('TEAM: ' + click.style(f'{team.Nation}', fg="magenta", bold=True))
        click.echo('GROUP: ' + click.style(f'{team.Group}', fg="yellow"))
        # click.echo('NEXT MATCH:' + click.style(f'{team.SoonestMatch}'))
        click.echo('STATISTICS:')
        if stats['Status'] is 'Alive':
            click.echo('    Status:' + click.style(stats['Status'], fg='green'))
        else:
            click.echo('    Status: ' +
             click.style(stats['Status'], fg='red'))
        click.echo('    Goals: ' + click.style(str(stats['Goals']), fg="red", blink=True))
        click.echo('    Matches Won: ' +
         click.style(str(stats['Matches Won']), fg="yellow", bold=True))
        click.echo('    Matches Lost: ' +
         click.style(str(stats['Matches Lost']), fg="cyan", bold=True))
        click.echo(click.style('\n MATCHES: ', fg='red') +
         f' \n {" ".join(x for x in team.Matches)}')
        print("--------------------------------------------------------------")
    elif country:
        team = LoadTeam(Country=country)
        stats = LoadStats(team)
        print("--------------------------------------------------------------")
        click.echo('TEAM: ' +
         click.style(f'{team.Nation}', fg="magenta", bold=True))
        click.echo('GROUP: ' +
         click.style(f'{team.Group}',fg="yellow"))
        click.echo('STATISTICS:')
        if stats['Status'] is 'Alive':
            click.echo('    *Status:' +
             click.style(stats['Status'], fg='green'))
        else:
            click.echo('    *Status: ' +
             click.style(stats['Status'], fg='red'))
        click.echo('    *Goals: ' +
         click.style(str(stats['Goals']),fg="blue", blink=True))
        click.echo('    *Matches Won: ' +
         click.style(str(stats['Matches Won']),fg="yellow", bold=True))
        click.echo('    *Matches Lost: ' +
            click.style(str(stats['Matches Lost']), fg="cyan", bold=True))
        print("--------------------------------------------------------------")

if __name__ == '__main__':
    main()
