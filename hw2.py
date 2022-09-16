from bs4 import BeautifulSoup
import requests
import csv

url = "https://mgoblue.com/sports/softball/stats/2021"
soup = BeautifulSoup(requests.get(url).text, 'html.parser')

players = soup.find_all('tr')
player_names = []
for player in players:
    ths = player.find('th')
    try:
        a = ths.find('a', {'data-player-id':True})
        player_names.append(a.text)
    except:
        continue

hits = [int(x.text) for x in soup.find_all('td', {'data-label':'H'})]
bb = [int(x.text) for x in soup.find_all('td', {'data-label':'BB'})]
hbp = [int(x.text) for x in soup.find_all('td', {'data-label':'HBP'})]
tb = [int(x.text) for x in soup.find_all('td', {'data-label':'TB'})]
ab = [int(x.text) for x in soup.find_all('td', {'data-label':'AB'})]
gdp = [int(x.text) for x in soup.find_all('td', {'data-label':'GDP'})]
sf = [int(x.text) for x in soup.find_all('td', {'data-label':'SF'})]
sh = [int(x.text) for x in soup.find_all('td', {'data-label':'SH'})]
sbatt = [x.text for x in soup.find_all('td', {'data-label':'SB'})]
x2b = [int(x.text) for x in soup.find_all('td', {'data-label':'2B'})]
x3b = [int(x.text) for x in soup.find_all('td', {'data-label':'3B'})]
hr = [int(x.text) for x in soup.find_all('td', {'data-label':'HR'})]

cs = []
sb = []
for sba in sbatt:
    s = sba.split('-')
    try:
        c = int(s[1]) - int(s[0])
        cs.append(c)
        sb.append(int(s[0]))
    except:
        continue

stats = {}
counter = 0
for player in player_names:
    stats[player] = {'hits':hits[counter], 'bb':bb[counter], 'hbp':hbp[counter], 'tb': tb[counter], 'ab':ab[counter], 'gdp':gdp[counter], 'sf':sf[counter], 'sh':sh[counter], 'cs':cs[counter], '2b':x2b[counter], '3b':x3b[counter], 'hr':hr[counter], 'sb':sb[counter]}
    counter += 1
    if player == 'Hoogenraad, Haley':
        break

# lm = -4.02 + 0.43(1B) + 0.32(2B) + 1.55(3B) + 0.66(HR) + 0.33(HP + BB) + 0.19(SB) + 0.86(CS)

scale_factors = {}
for player in stats:
    # We assume 46 games and 966 total outs for the 2021 Michigan softball season
    outs = 0.982 * stats[player]['ab'] - stats[player]['hits'] + stats[player]['gdp'] +stats[player]['sf'] + stats[player]['sh'] + stats[player]['cs']
    scale_factors[player] = 966/outs

print(f"calculated scale factors: {scale_factors}")

player_runs = {}
for player in stats:
    estimated_runs = -4.02 + 0.43*(stats[player]['hits'] * scale_factors[player] - stats[player]['2b'] * scale_factors[player] - stats[player]['3b'] * scale_factors[player] - stats[player]['hr'] * scale_factors[player]) + 0.32*(stats[player]['2b'] * scale_factors[player]) + 1.55*(stats[player]['3b'] * scale_factors[player]) + 0.66*(stats[player]['hr'] * scale_factors[player]) + 0.33*(stats[player]['hbp'] * scale_factors[player] + stats[player]['bb'] * scale_factors[player]) + 0.19*(stats[player]['sb'] * scale_factors[player]) + 0.86*(stats[player]['cs'] * scale_factors[player])
    player_runs[player] =  round(estimated_runs/46, 2)

with open('umsoftball_2021linearweights.csv', "w") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["player", "runs/game"])
    csvwriter.writerows(player_runs.items())
