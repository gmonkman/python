# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
from funclib.iolib import PrintProgress
from funclib.iolib import folder_open
from gazetteer import gazlib
import gazetteerdb as gazetteerdb
import mmo.name_entities as ne
from mmo import totextfile


valid_ifcas = []
valid_ifcas = set(list(ne.IFCAS) + [''])


#get all by selecting the ifca and name cols in map_sites.xlsx and doing the python export
all = [['Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'North East', 'North East', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Devon and Severn', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Isles of Scilly', 'Kent and Essex', 'Kent and Essex', 'Northumberland', 'Northumberland', 'North East', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Eastern', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Northumberland', 'Northumberland', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Devon and Severn', 'Devon and Severn', 'Cornwall', 'Cornwall', 'Devon and Severn'], ['Weymouth Bay', 'Dungy Head', 'Brandy Bay', 'Egmont Point', 'St Albans Head', 'Dancing  Ledge', 'Anvil Point', 'Durlston Head', 'Perveril Point', 'Swanage Bay', 'Ballard Point', 'Old Harry Rocks', 'Studland Bay', 'Shell Bay', 'Inner Poole Patch', 'Outer Poole Patch', 'Armchair', 'Bungalows', 'Pevensey Bay', 'Langney Point', 'Sovereign Harbour', 'Selsey Bill', 'St Catherines Point', 'The Needles', 'Poole Bay', 'Bill of Portland', 'Chesil Beach', 'Lyme Bay', 'West Bay', 'Old Severn Bridge', 'Stanwood Bay', 'Hill Head', 'Calshot Light', 'Daedalus', 'Stokes Bay Wreck', 'Stokes Bay Pier', 'West Ryde Middle', 'South Bramble', 'West Bramble', 'South Ryde Middle', 'East Bramble', 'Knoll Shoal', 'North Sturbridge', 'Bull Rocks', 'Steephill Bay', 'Dunose Head', 'Culver Cliffs', 'Hengist Head', 'Hill Head', 'Browndown Bay', 'Millenium Pier', 'Warsash Beach', 'Western Shore', 'Rolling Mills Jetty', 'Pennington Marshes', 'Old Pipeline Outflow', 'Hurst Hole', 'Outfall Jetty', 'Outfall Pier', 'West Wittering Beach', 'East Wittering Beach', 'Bracklesham Bay', 'Porchester Creek', 'Chichester Harbour', 'Penninis Head', 'Dover Breakwater', 'Folkstone Pier', 'Craster Skeers', 'Creswell Skeers', 'Staincliff', 'Daymark', 'Eastern Rocks', 'Hoe Point', 'The Quay', 'Blythe Water', 'Hastings Harbour', 'The Ditches', 'Kingmere Rocks', 'Rock Tow', 'Measors Rock', 'Red Shrave', 'Roker Pier', 'Black Middens', 'Coldharbour Sluice', 'Greenhithe Promenade', 'Gravesend Promenade', 'Gravesend Sea School', 'Westminster Wall', 'Rushenden Bay', 'Barton Point', 'Bishopstone Rocks', 'Cold Harbour Sluice', 'Killicks Hole', 'Kingsdown Butts', 'Harbour Pier', 'Rotunda Beach', 'Brewers Hill', 'Princes Parade', 'Hythe Swimming Pool', 'Hythe Army Ranges', 'Willop Sluice', 'Hythe Marine Parade', 'South Deep Channel', 'Gravel Points', 'Warbarrow Tout', 'Mupe', 'Church Ope', 'Cheyne', 'Ocean Rock', 'Clock Tower Beach', 'Clocktower Beach', 'Long Quarry', 'Berryhead Quarry', 'Scabbacombe', 'Mutton Cove', 'Happy Valley', 'Main Beach', 'Tregantle', 'White Rock', 'Talland Sands', 'Pont Creek', 'Port Giskey', 'Poistreath', 'Cadgewith Cove', 'Poldu Cove', 'Gunwailoe', 'Maen-Du', 'Maen Du', 'Meon Shore', 'Polhawne', 'Ladram Beach', 'Elbury Cove', 'Navvacks', 'Pentine Head', 'Bideford Bridge']]
#all = [['Devon and Severn'], ['Weymouth Bay']]
ifcas = [s.lower() for s in all[0]]
sites = [s.lower() for s in all[1]]

assert set(ifcas).issubset(valid_ifcas), 'IFCAs %s invalid' % set(ifcas).difference(valid_ifcas)

results = ""
PP = PrintProgress(len(sites))

for i, site in enumerate(sites):
    results += gazlib.lookup(site, ifcas[i], True)
    PP.increment()


totextfile(results, 'C:/Users/Graham Monkman/OneDrive/Documents/MMOMapping/data/Data sources and sites/books+mags/map_sites_lookup.csv')
print('Done')
folder_open('C:/Users/Graham Monkman/OneDrive/Documents/MMOMapping/data/Data sources and sites/books+mags')




