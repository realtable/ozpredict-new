from daterangeparser import parse as date_parse
import csv
import pickle
import re


def csv_to_polls(year):
    # get csv as list of dics
    with open(f'polls/{year}.csv') as f:
        raw_polls = [{k: v for k, v in row.items()}
                     for row in csv.DictReader(f, skipinitialspace=True)]

    # parse raw polls
    polls = []
    election = date_parse('21 May 2022')[0]
    firms = {
        'Morgan': 'Roy Morgan',
        'Morgan (face)': 'Roy Morgan',
        'Morgan (phone)': 'Roy Morgan',
        'Morgan (multi)': 'Roy Morgan',
        'Roy Morgan': 'Roy Morgan',
        'Galaxy': 'YouGov',
        'YouGov-Galaxy': 'YouGov',
        'YouGov': 'YouGov',
        'Newspoll-YouGov': 'YouGov',
        'Newspoll': 'YouGov',
        'ReachTEL': 'ReachTEL',
        'ReachTel': 'ReachTEL',
        'Essential': 'Essential',
        'Ipsos': 'Ipsos',
        # 'AMR': 'AMR',
        # 'Lonergan': 'Lonergan',
        'Nielsen': 'Nielsen',
        'Resolve Strategic': 'Resolve Strategic'
    }

    for poll in raw_polls:
        try:
            if poll['Firm'].split('[')[0] in firms:
                _ = poll['ALP2'].split('%')[0]
                date = date_parse(re.split(', |,|/', poll['Date'])[-1])[0]
                polls.append({
                    'date': date,
                    'until': (election - date).days,
                    'firm': firms[poll['Firm'].split('[')[0]],
                    'ALP': float(poll['ALP2'].split('%')[0]),
                    'LNP': float(poll['LNP2'].split('%')[0])
                })
        except:
            pass

    return polls


def polls_to_trends(years):
    elections = {  # LNP TPP
        2022: {'date': date_parse('21 May 2022')[0], 'pct': 50}, # 50 cos we dont want relative
        2019: {'date': date_parse('18 May 2019')[0], 'pct': 51.53},
        2016: {'date': date_parse('2 Jul 2016')[0], 'pct': 50.40},
        2013: {'date': date_parse('7 Sep 2013')[0], 'pct': 53.50},
        2010: {'date': date_parse('21 Aug 2010')[0], 'pct': 49.90}
    }
    results = {
        2022: {},
        2019: {},
        2016: {},
        2013: {},
        2010: {}
    }

    for year in years:
        polls = csv_to_polls(year)
        for poll in polls:
            if poll['firm'] != 'Election':
                if (elections[year]['date'] - poll['date']).days <= 200:
                    firm = poll['firm']
                    if firm not in results[year]:
                        results[year][firm] = {'until': [], 'diff': []}
                    results[year][firm]['until'].append(
                        (elections[year]['date'] - poll['date']).days)
                    results[year][firm]['diff'].append(
                        round(poll['LNP'] - elections[year]['pct'], 1))

    return results


if __name__ == '__main__':
    polls = csv_to_polls(2022)
    with open('poll_current.p', 'wb+') as f:
        pickle.dump(polls, f)

    trends = polls_to_trends([2013, 2016, 2019, 2022])
    with open('poll_accuracy.p', 'wb+') as f:
        pickle.dump(trends, f)
