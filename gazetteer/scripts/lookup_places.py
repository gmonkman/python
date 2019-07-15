# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''helper to look up places'''
from funclib.iolib import PrintProgress
from funclib.iolib import folder_open
from gazetteer import gazlib

import mmo.name_entities as ne
from mmo import totextfile


valid_ifcas = []
valid_ifcas = set(list(ne.IFCAS) + [''])


#get all by selecting the ifca and name cols in map_sites.xlsx and doing the python export
#all_ = [['Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'North East', 'North East', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Devon and Severn', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Isles of Scilly', 'Kent and Essex', 'Kent and Essex', 'Northumberland', 'Northumberland', 'North East', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Eastern', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Northumberland', 'Northumberland', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Devon and Severn', 'Devon and Severn', 'Cornwall', 'Cornwall', 'Devon and Severn'], ['Weymouth Bay', 'Dungy Head', 'Brandy Bay', 'Egmont Point', 'St Albans Head', 'Dancing  Ledge', 'Anvil Point', 'Durlston Head', 'Perveril Point', 'Swanage Bay', 'Ballard Point', 'Old Harry Rocks', 'Studland Bay', 'Shell Bay', 'Inner Poole Patch', 'Outer Poole Patch', 'Armchair', 'Bungalows', 'Pevensey Bay', 'Langney Point', 'Sovereign Harbour', 'Selsey Bill', 'St Catherines Point', 'The Needles', 'Poole Bay', 'Bill of Portland', 'Chesil Beach', 'Lyme Bay', 'West Bay', 'Old Severn Bridge', 'Stanwood Bay', 'Hill Head', 'Calshot Light', 'Daedalus', 'Stokes Bay Wreck', 'Stokes Bay Pier', 'West Ryde Middle', 'South Bramble', 'West Bramble', 'South Ryde Middle', 'East Bramble', 'Knoll Shoal', 'North Sturbridge', 'Bull Rocks', 'Steephill Bay', 'Dunose Head', 'Culver Cliffs', 'Hengist Head', 'Hill Head', 'Browndown Bay', 'Millenium Pier', 'Warsash Beach', 'Western Shore', 'Rolling Mills Jetty', 'Pennington Marshes', 'Old Pipeline Outflow', 'Hurst Hole', 'Outfall Jetty', 'Outfall Pier', 'West Wittering Beach', 'East Wittering Beach', 'Bracklesham Bay', 'Porchester Creek', 'Chichester Harbour', 'Penninis Head', 'Dover Breakwater', 'Folkstone Pier', 'Craster Skeers', 'Creswell Skeers', 'Staincliff', 'Daymark', 'Eastern Rocks', 'Hoe Point', 'The Quay', 'Blythe Water', 'Hastings Harbour', 'The Ditches', 'Kingmere Rocks', 'Rock Tow', 'Measors Rock', 'Red Shrave', 'Roker Pier', 'Black Middens', 'Coldharbour Sluice', 'Greenhithe Promenade', 'Gravesend Promenade', 'Gravesend Sea School', 'Westminster Wall', 'Rushenden Bay', 'Barton Point', 'Bishopstone Rocks', 'Cold Harbour Sluice', 'Killicks Hole', 'Kingsdown Butts', 'Harbour Pier', 'Rotunda Beach', 'Brewers Hill', 'Princes Parade', 'Hythe Swimming Pool', 'Hythe Army Ranges', 'Willop Sluice', 'Hythe Marine Parade', 'South Deep Channel', 'Gravel Points', 'Warbarrow Tout', 'Mupe', 'Church Ope', 'Cheyne', 'Ocean Rock', 'Clock Tower Beach', 'Clocktower Beach', 'Long Quarry', 'Berryhead Quarry', 'Scabbacombe', 'Mutton Cove', 'Happy Valley', 'Main Beach', 'Tregantle', 'White Rock', 'Talland Sands', 'Pont Creek', 'Port Giskey', 'Poistreath', 'Cadgewith Cove', 'Poldu Cove', 'Gunwailoe', 'Maen-Du', 'Maen Du', 'Meon Shore', 'Polhawne', 'Ladram Beach', 'Elbury Cove', 'Navvacks', 'Pentine Head', 'Bideford Bridge']]
#all = [['Devon and Severn'], ['Weymouth Bay']]
#ifcas = [s.lower() for s in all[0]]
#sites = [s.lower() for s in all[1]]

ifcas = []

sites = ['plymouth harbour', 'littlehampton harbour', 'Newquay', 'fleetwood marina', 'Sunderland Marina', 'orford harbour', 'whitby harbour', 'hartlepool marina', 'minehead harbour', 'whitby harbour', 'Weymouth Harbour', 'weymouth harbour', 'minehead harbour', 'Lyme Regis', 'lyme regis harbour', 'weymouth harbour', 'gosport marina ', 'Shotley Harbour', 'grimsby harbour', 'Salcombe', 'Torquay Harbour', 'brighton marina', 'mevagissey harbour', 'poole harbour marina', 'Poole Harbour', 'weymouth harbour', 'Minehead', 'Newquay', 'newquay harbour', 'newquay harbour', 'Salcombe', 'hartlepool marina', 'Shoreham', 'brixham harbour', 'Ramsgate Harbour', 'Brixham', 'Poole Harbour', 'mevagissey harbour', 'Ramsgate Harbour', 'portland harbour', 'Penzance', 'Brighton Marina', 'poole harbour marina', 'Shoreham', 'Shoreham', 'fleetwood marina', 'exmouth Harbour', 'Lyme Regis', 'great yarmouth harbour', 'ilfracombe harbour', 'Tyne Marina', 'Craster', 'Ramsgate Harbour', 'poole harbour marina', 'ramsgate harbour', 'Newquay', 'Newquay', 'exmouth Harbour', 'Essex Marina', 'Paignton Harbour', 'Scarborough Harbour', 'Branscombe Beach', 'brighton marina', 'Brightlingsea Harbour', 'brighton marina', 'gosport marina', 'Plymouth Harbour', 'Penzance', 'Brightlingsea', 'Newhaven', 'Looe', 'Poole Harbour', 'Sunderland Marina', 'penzance harbour', 'Padstow', 'Lymington', 'Weymouth Harbour', 'brighton marina', 'bridport harbour', 'Whitby', 'Paignton Harbour', 'newquay harbour', 'Whitby', 'Bradwell Marina', 'bradwell marina', 'littlehampton harbour', 'Lowestoft Marina', 'Shotley', 'West Bay', 'Rye', 'lowestoft harbour', 'Wallasea Island Moorings', 'Langstone Harbour', 'Poole Harbour', 'gosport marina', 'hartlepool marina', 'Langstone Harbour', 'Porthleven', 'hartlepool marina', 'poole harbour marina', 'blyth Harbour', 'Bradwell Marina', 'Fambridge', 'Bridport', 'Levington Marina', 'Essex Marina', 'Wallasea Island Moorings', 'langstone harbour', 'Sovereign Harbour', 'Minehead', 'brighton marina', 'chatham marina', 'isle of sheppey', 'hartlepool marina', 'liverpool marina', 'gosport marina ', 'St Ives', 'burnham-on-crouch marina', 'lymington harbour marina', 'Lowestoft Marina', 'Weymouth Harbour', 'ramsgate harbour', 'Keyhaven', 'littlehampton harbour', 'West Mersea', 'west mersea harbour', 'Minehead', 'Lowestoft Marina', 'chichester harbour', 'padstow harbour', 'Liverpool Marina', 'West Mersea', 'west mersea harbour', 'Torquay Harbour', 'hartlepool marina', 'hartlepool marina', 'sovereign harbour marina', 'Ramsgate Harbour', 'hartlepool marina', 'littlehampton harbour', 'portland harbour', 'Dover Harbour', 'Weymouth Harbour', 'weymouth harbour', 'weymouth harbour', 'folkestone Harbour', 'Looe Harbour', 'exmouth Harbour', 'Lyme Regis', 'Lowestoft Marina', 'west mersea harbour', 'Dartmouth', 'dover harbour', 'Liverpool Marina', 'liverpool marina', 'Two Tree Island Slipway', 'Seahouses', 'Brightlingsea Harbour', 'Harwich Harbour', 'Brighton Marina', 'Langstone Harbour', 'Dover Harbour', 'brighton marina', 'weymouth harbour', 'Wallasea Island Moorings', 'Whitby', 'bridlington harbour', 'Lymington', 'lymington harbour marina', 'Great Yarmouth Harbour', 'great yarmouth harbour', 'Brightlingsea', 'isle of sheppey', 'Lowestoft Marina', 'Clovelly', 'Canvey Island Moorings', 'Ilfracombe', 'whitby harbour', 'littlehampton harbour', 'Liverpool Marina', 'liverpool marina', 'Clovelly', 'Tyne Marina', 'Looe', 'Portsmouth Harbour', 'Lyme Regis', 'Poole Harbour', 'Dover Harbour', 'Canvey Island Moorings', 'Torbay Marina', 'Lyme Regis', 'Torquay Harbour', 'Seahouses', 'christchurch harbour', 'Plymouth Harbour', 'southampton Harbour', 'Ramsgate Harbour', 'weymouth harbour', 'sovereign harbour marina', 'littlehampton harbour', 'hayling island', 'brixham harbour', 'Tyne Marina', 'bridlington Harbour', 'Ilfracombe', 'Newhaven', 'fleetwood marina', 'Brixham', 'gosport marina', 'Lyme Regis', 'ramsgate harbour', 'chatham marina', 'Langstone Harbour', 'hartlepool marina', 'Essex Marina', 'west mersea harbour', 'fleetwood marina', 'Ramsgate Harbour', 'Padstow', 'Brighton Marina', 'Shoeburyness', 'Langstone Harbour', 'lymington harbour marina', 'levington marina', 'lowestoft harbour', 'dover harbour', 'whitby harbour', 'Seaton Marina', 'Watchet', 'Mevagissey', 'Whitby', 'Weymouth Harbour', 'dover harbour', 'lowestoft harbour', 'littlehampton harbour', 'Minehead', 'exmouth Harbour', 'Cowes Harbour', 'Whitby', 'Seahouses', 'hayling island', 'lymington harbour marina', 'littlehampton harbour', 'Lyme Regis', 'Two Tree Island Slipway', 'Minehead', 'dover harbour', 'weymouth harbour', 'Weymouth Harbour', 'Penzance', 'monks ferry slipway', 'gosport marina', 'littlehampton harbour', 'plymouth harbour', 'Lyme Regis', 'Rye', 'Tyne Marina', 'Whitby', 'poole harbour marina', 'Essex Marina', 'Walton-on-the-Naze', 'Looe', 'Langstone Harbour', 'Isle of Sheppey', 'burnham-on-crouch marina', 'Brighton Marina', 'Weymouth Harbour', 'Newquay', 'Looe', 'Amble', 'Clovelly', 'Lyme Regis', 'Whitby', 'Canvey Island Moorings', 'isle of sheppey', 'gosport marina', 'brixham harbour', 'bridlington Harbour', 'hartlepool marina', 'Keyhaven', 'poole harbour marina', 'brighton marina', 'Newhaven', 'Weymouth Harbour', 'Berwick-upon-Tweed', 'brixham harbour', 'Portishead Marina', 'Minehead', 'Ilfracombe', 'Minehead', 'minehead harbour', 'Keyhaven', 'Poole Harbour', 'paignton harbour', 'littlehampton harbour', 'Weymouth Harbour', 'Looe Harbour', 'dartmouth harbour', 'Ramsgate Harbour', 'Southwold', 'Sovereign Harbour', 'folkestone Harbour', 'Falmouth Harbour', 'plymouth harbour', 'Weymouth Harbour', 'rye harbour', 'lyme regis harbour', 'Lowestoft Marina', 'exmouth Harbour', 'poole harbour marina', 'Brighton Marina', 'Two Tree Island Slipway', 'Langstone Harbour', 'dover harbour', 'Grimsby Harbour', 'grimsby harbour', 'Langstone Harbour', 'Wallasea Island Moorings', 'Scarborough Harbour', 'Lymington', 'Looe', 'bridlington Harbour', 'Chichester', 'scarborough harbour', 'Lowestoft Marina', 'bridlington harbour', 'poole harbour marina', 'poole harbour marina', 'west mersea harbour', 'West Mersea', 'Sunderland Marina', 'Dover Harbour', 'Poole Harbour', 'watchet harbour marina', 'exmouth Harbour', 'Bembridge', 'poole harbour marina', 'exmouth Harbour', 'exmouth Harbour', 'brighton marina', 'dover harbour', 'Brighton Marina', 'Portishead Marina', 'Langstone Harbour', 'Shoreham', 'weymouth harbour', 'dartmouth harbour', 'Seaton Marina', 'Dartmouth', 'Swanage', 'Swanage Harbour', 'Sunderland Marina', 'Sunderland Marina', 'Whitby', 'Whitby', 'Watchet', 'dover harbour', 'plymouth harbour', 'Brighton Marina', 'Shoreham', 'Watchet', 'Portsmouth Harbour', 'Dover Harbour', 'Newhaven', 'whitby harbour', 'ramsgate harbour', 'whitby harbour', 'hartlepool marina', 'Poole Harbour', 'Whitby', 'whitby harbour', 'brighton marina', 'portsmouth harbour', 'Whitby', 'falmouth harbour', 'Plymouth Harbour', 'chatham marina', 'Newhaven', 'Amble', 'Sunderland Marina', 'Poole Harbour', 'Minehead', 'exmouth harbour', 'exmouth Harbour', 'Shoreham Harbour', 'shoreham harbour', 'Shotley', 'Lymington', 'Amble', 'whitby harbour', 'torquay harbour', 'Paignton Harbour', 'poole harbour marina', 'liverpool marina', 'ramsgate harbour', 'scarborough harbour', 'weymouth harbour', 'ramsgate harbour', 'Brightlingsea Harbour', 'exmouth Harbour', 'Lymington', 'Mevagissey', 'littlehampton harbour', 'Langstone Harbour', 'brixham harbour', 'Langstone Harbour', 'Porthleven', 'Whitby', 'bridlington Harbour', 'poole harbour marina', 'Keyhaven', 'Weymouth Harbour', 'weymouth harbour', 'Lyme Regis', 'Liverpool Marina', 'Liverpool Marina', 'Brightlingsea', 'Langstone Harbour', 'hartlepool marina', 'hartlepool marina', 'Plymouth Harbour', 'Weymouth Harbour', 'ramsgate harbour', 'Weymouth Harbour', 'gosport marina', 'chichester harbour', 'Dartmouth', 'Berwick-upon-Tweed', 'Dungeness', 'Seahouses', 'staithes harbour', 'Torquay Harbour', 'exmouth harbour', 'Weymouth Harbour', 'whitby harbour', 'Looe Harbour', 'Weymouth Harbour', 'ramsgate harbour', 'Lowestoft Marina', 'Langstone Harbour', 'Harwich Harbour', 'Portsmouth Harbour', 'Langstone Harbour', 'hartlepool marina', 'Whitby', 'Whitby', 'whitby harbour', 'Poole Harbour', 'poole harbour marina', 'Walton-on-the-Naze', 'Paignton Harbour', 'liverpool marina', 'whitby harbour', 'Looe', 'Seahouses', 'Amble', 'langstone harbour', 'Newhaven', 'Mevagissey', 'Penzance', 'lymington harbour marina', 'littlehampton harbour', 'brighton marina', 'Amble', 'chichester harbour', 'Falmouth Harbour', 'liverpool marina', 'Portsmouth Harbour', 'Lymington', 'lymington harbour marina', 'Essex Marina', 'burnham-on-crouch marina', 'Langstone Harbour', 'Hamble', 'Yarmouth', 'Lymington', 'Weymouth Harbour', 'ilfracombe harbour', 'newhaven harbour', 'bridlington Harbour', 'bridlington harbour', 'bridlington harbour', 'bridlington Harbour']


assert set(ifcas).issubset(valid_ifcas), 'IFCAs %s invalid' % set(ifcas).difference(valid_ifcas)

results = []
PP = PrintProgress(len(sites))

for i, site in enumerate(sites):
    if ifcas:
        results += [gazlib.lookup(site, ifcas[i], True, include_name_in_output=True)]
    else:
        results += [gazlib.lookup(site, '', True, include_any_ifca=True, include_name_in_output=True)]
    PP.increment()

results = '\n'.join(results)
totextfile(results, 'C:/Users/Graham Monkman/OneDrive/Documents/MMOMapping/data/Data sources and sites/books+mags/map_sites_lookup.csv')
print('Done')
folder_open('C:/Users/Graham Monkman/OneDrive/Documents/MMOMapping/data/Data sources and sites/books+mags')
