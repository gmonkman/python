# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

from gazetteer import gazlib
import gazetteerdb as gazetteerdb
import mmo.name_entities as ne

all = [['Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'North East', 'North East', 'North East', 'North East', 'North West', 'North West', 'North West', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Devon and Severn', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'North West', 'North West', 'North West', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'North West', 'North West', 'North West', 'Eastern', 'Eastern', 'Eastern', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', '', '', '', '', '', '', '', 'North West', '', 'North West', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Kent and Essex', '', ''], ['Kingsand', 'Cawsand', 'Penlee Point', 'Polhawn Cove', 'Portwrinkle', 'Downderry', 'Millendreath Beach', 'Lantivet Bay', 'Pencarrow Head', 'Lantic Bay', 'Talland Bay', 'Looe Island', 'Dodman Point', 'Vault Beach', 'Gorran Haven', 'Chapel Point', 'Port Mellon', 'Pentewan', 'Black Head', 'Trenarren', 'Porthpean', 'Gribbin Head', 'Crinnis and Carlyon', 'Golant', 'Carlyon Bay', 'Polkerris', 'Caerhays Bay', 'Portloe', 'Nare Head', 'Carne Beach', 'Pendower Beach', 'Porth Beach', 'Zone Point', 'Saint Anthonys Head', 'St. Maws', 'Turnaware Point', 'Hemmick Beach', 'Caerhays Beach', 'Trefusis Point', 'Swanpool Beach', 'Rosemullion Head', 'Helford River', 'Nare Point', 'Porthallow', 'Porthoustock', 'Manacle Point', 'Coverack', 'Chynhalls Point', 'Black Head', 'Lizard Point', 'Kennack Sands', 'Cadgwith', 'Housel Bay', 'Polpeor Cove', 'Kynance Cove', 'Mullion Cove', 'Poldhu Cove', 'Church Cove', 'Polurrian Cove', 'Gunwallow Cove', 'Loe Bar', 'Rinsey Head', 'Praa Sands', 'Prussia Cove', 'Perran Sands', 'Lamorna Cove', 'Tater-Du', 'Porthcurno', 'Sennen Cove', 'Whitesand Bay', 'Cape Cornwall', 'Pendeen Watch', 'Portheras Cove', 'Gurnards Head', 'Zennor Head', 'Porthmeor Beach', 'St. Ives', 'Gogrevy Point', 'Navax Point', 'Portreth', 'Porthtowan', 'Chapel Porth', 'St. Agnes Head', 'Trevaunance Cove', 'Trevellas Porth', 'Hanover Cove', 'Cligga Head', 'Droskyn Point', 'Perran Bay', 'Ligger Point', 'Penhale Point', 'Holywell Bay', 'Kelsey Head', 'Porth Joke', 'Crantock', 'Pentire Point', 'Fistral Bay', 'Towan Head', 'Porth Island', 'Watergate Bay', 'Beacon Cove', 'Mawgan Porth', 'Trenance Point', 'Park Head', 'Fistral Beach', 'Little Fistral', 'High Place', 'Atlantic Drain', 'Low Point', 'Spy Cove', 'Leanards Rock', 'Hedge Cove', 'Rocket Pole', 'Pigeon Cove', 'Fly Cellars', 'Newquay Harbour', 'Porthcothan Bay', 'Skate Rock', 'Treyarnon Bay', 'Constantine Bay', 'Boobys Bay', 'Dinas Head', 'Trevose Head', 'Mother Ivys Bay', 'Harlyn Bay', 'Trevone Bay', 'Stepper Point', 'Flat Rock', 'Camel Estuary', 'Dammer Bay', 'Polzeath', 'Pentire Point', 'Rumps Point', 'Carnweather Point', 'Kellan Head', 'Port Isaac', 'Barretts Zawn', 'Tregardock Beach', 'Trebarwith Strand', 'Tintagel Head', 'Bossiney Haven', 'Pentargon', 'Dizzard Point', 'Widemouth Sand', 'Bude Bay', 'Duckpool', 'Welcombe Mouth', 'Marsland Mouth', 'Eddystone Reef', 'Pendennis Point', 'Porthallow', 'The Manacles', 'Trevose Head', 'Hartland Point', 'Cremyll Battery', 'The Island', 'The Merlin', 'Palm Rock', 'Jupiter Point', 'Forder', 'Wearde Quay', 'Cargreen', 'Blackhall Colliery Beach', 'Easington Beach', 'Chemical  Beach', 'Blast Beach', 'Dubmill Point', 'Maryport Harbour', 'Whitehaven Pier', 'Babbacombe Bay', 'Bolt Head', 'Brixham Breakwater', 'Lions Den', 'Erme Estuary', 'Princess Pier', 'Haldon Piers', 'Teign Estuary', 'Pottery Quay', 'Eastern Kings', 'Western Kings', 'Rusty Anchor', 'West Hoe Pier', 'Elphinstone Quay', 'Laira Bridge', 'Old Cellars Beach', 'Hilsea Point', 'Durdle Door', 'Friars Cliff', 'Long Groyne', 'Jerrys Point', 'Ringstead Bay', 'Swanage Pier', 'Golden Cap', 'East Ebb Cove', 'Thorncombe Beacon', 'West Bay', 'Cogden Beach', 'Abbotsbury Castle', 'Ferrybridge', 'Weymouth Bay', 'Dungy Head', 'Brandy Bay', 'Egmont Point', 'Chapmans Rock', 'St Albans Head', 'Dancing  Ledge', 'Anvil Point', 'Durlston Head', 'Perveril Point', 'Swanage Bay', 'Ballard Point', 'Old Harry Rocks', 'The Foreland', 'Studland Bay', 'Shell Bay', 'Inner Poole Patch', 'Outer Poole Patch', 'Redcar Scars', 'Flamborough Head', 'Spurn Head', 'Armchair', 'Breil', 'Bungalows', 'Hammer Rock', 'The Naze', 'Foulness Island', 'Herne Bay', 'Botany Bay', 'Pegwell Bay', 'Sandwich Bay', 'Rye Bay', 'Pevensey Bay', 'Langney Point', 'Sovereign Harbour', 'Selsey Bill', 'St. Catherines Point', 'The Needles', 'Poole Bay', 'Bill of Portland', 'Chesil Beach', 'Lyme Bay', 'West Bay', 'Cliff Road', 'Dovercourt Beach', 'Frinton Wall', 'Halfpenny Pier', 'Wallasea Island', 'Southend Pier', 'Admiralty Pier', 'Old Severn Bridge', 'Hamble Common', 'Hurst Shingle Bank', 'Lepe Beach', 'Weston Shore', 'Bembridge Harbour', 'Chale Bay', 'Stanwood Bay', 'Calshot Castle', 'Hill Head', 'Bramble Bank', 'Calshot Light', 'Titchfield Haven', 'Daedalus', 'Browndown Point', 'Stokes Bay Wreck', 'Stokes Bay Pier', 'Haslar Sea Wall', 'No Mans Land Fort', 'Ryde Pier', 'Kings Quay', 'Old Castle Point', 'West Ryde Middle', 'South Bramble', 'West Bramble', 'South Ryde Middle', 'East Bramble', 'Knoll Shoal', 'Mother Bank', 'North Sturbridge', 'Peel Bank', 'Sowley Beach', 'Thorness Bay', 'Norton Beach', 'Totland Bay', 'Alum Bay', 'Shingle Bank', 'The Nodes', 'Freshwater Bay', 'Compton Bay', 'Hanover Point', 'Bull Rocks', 'Brightstone Bay', 'Atherfield Point', 'Chale Bay', 'Puckaster Cove', 'Steephill Bay', 'Dunose Head', 'Luccombe Bay', 'Horse Ledge', 'Shanklin Pier', 'Lake Beach', 'Sandown Bay', 'Culver Cliffs', 'Whitecliff Bay', 'St Helens Fort', 'Ryde Sands', 'Canford Cliffs', 'Durley Chine', 'Kimmeridge Ledges', 'Kimmeridge Bay', 'Avon Beach', 'Christchurch Harbour', 'Hengist Head', 'Pot Bank', 'Christchurch Bay', 'Hill Head', 'Lee-on-the-solent', 'Browndown Bay', 'Stokes Bay', 'Gilkicker Point', 'Haslar Wall', 'Millenium Pier', 'Warsash Beach', 'Western Shore', 'Rolling Mills Jetty', 'Magazine Lane', 'Dibden Bay', 'Calshot', 'Stone Point', 'Coastguard Cottages', 'Park Shore', 'Pennington Marshes', 'Old Pipeline Outflow', 'Hurst Point', 'Hurst Hole', 'Victoria Pier', 'Clarence Beach', 'South Parade Pier', 'Eastney Beach', 'Outfall Jetty', 'Outfall Pier', 'West Wittering Beach', 'East Wittering Beach', 'Bracklesham Bay', 'West Beach', 'East Beach', 'Porchester Creek', 'Fareham Creek', 'Langstone Harbour', 'Chichester Harbour', 'River Medina', 'Yarmouth Pier', 'Deep Point', 'Penninis Head', 'Porthcressa Beach', 'Beltinge Promenade', 'Dover Breakwater', 'Folkstone Pier', 'Marine Parade', 'Reculver Towers', 'Marine Beach', 'Rossall Point', 'River Wyre', 'Anderby Creek', 'Ingoldmells Point', 'Saltfleet Haven', 'Wolla Bank', 'Perch Rock', 'Red Rocks', 'Seaforth Rocks', 'Blakeney Point', 'North Beach', 'Sea Palling Reefs', 'Robin Hoods Bay', 'Filey Bay', 'Filey Brigg', 'Cloughton Wyke', 'Makro', 'Saltwick Bay', 'Hayburn Wyke', 'Staintondale', 'Holy Island', 'Embleton Bay', 'Craster Skeers', 'Coquet Island', 'Creswell Skeers', 'Alnmouth Bridge', 'Beadnell', 'Cambois Rocks', 'Bog Hall Rocks', 'Craster Harbour', 'Hummersea Scar', 'Saltburn Pier', 'Heugh', 'Heugh Breakwater', 'Staincliff', 'Redcar East Scars', 'North Gare', 'South Gare', 'Taylors Island', 'Bar Point', 'Newfoundland Rocks', 'Giants Castle', 'Peninnis Head', 'Porth Cressa Beach', 'Garrison Hill', 'Newford Island', 'Deep Point', 'Menawethan', 'Daymark', 'Eastern Rocks', 'Maiden Bower', 'Scilly Rock', 'Nundeeps', 'Crim Rocks', 'Hanjague', 'Periglis Cove', 'Long Point', 'Browarth Point', 'Dropnose Point', 'The Bar', 'Hoe Point', 'Horse Point', 'Carnew Point', 'Burnt Island', 'Gull Point', 'Pernagie Point', 'Higher Town Bay', 'The Porth', 'White Island', 'New Grimsby Harbour', 'Merchants Point', 'Tobaccomans Point', 'Crow Point', 'Tresco Flats', 'Lizard Point', 'Shipman Head', 'Hangman Island', 'The Quay', 'Gweal', 'Hell Bay', 'Brean Down', 'Hinkley Point', 'Sand Point', 'Aldeburgh Bay', 'Hollesley Bay', 'Blythe Water', 'Aldeburgh Town Beach', 'Landguard Beach', 'Lowestoft South Pier', 'Orford Beach', 'Sizewell', 'Thorpeness Point', 'Brighton Marina', 'Pett Levels', 'Cliff End', 'Hastings Harbour Arm', 'Hasting Harbour', 'Piddinghoe', 'Tidemills', 'Bracklesham Bay', 'The Looe', 'Pagham Harbour', 'Bognor Rocks', 'Bognor Pier', 'Winter Knoll', 'The Ditches', 'Kingmere Rocks', 'Rock Tow', 'Measors Rock', 'Red Shrave', 'Martello Tower', 'Birling Gap', 'Normans Bay', 'Cooden Beach', 'Coxheath Shoals', 'Rye Harbour', 'Broomhill Sands', 'Roker Pier', 'The Black Middens', 'St Marys Island', 'Whitley Bay Beach', 'Calshot', 'Reculver Towers', 'Morte Point', 'Atherfield', 'Carsluith', 'Cowes', 'Freshwater Bay', 'Hoyle Bank', 'Eype', 'Vale Park', 'Twiss Groyne', 'Canvey Island', 'Magazine Lane', 'Soulseat Reservoir', 'Highshore', 'Victoria Park', 'Society Points', 'Whiting Ness', 'The Crawton', 'North Berwick', 'Fife Ness', 'Inverbervie', 'Breascleit Pier', 'Boddin Point', 'Burrow Head', 'Mambeg', 'Craignure Pier', 'Ardgour', 'Newton Shore', 'Terally Bay', 'Ardwell Back Shore', 'Monreith', 'Old House Point', 'Largs Shingle Point', 'Port Logan', 'Isle of Whithorn Harbour', 'Leffnol Beach', 'The Lhen', 'Mooragh Promenade', 'Green Gate', 'Gansey', 'Stanah', 'Cleveleys', 'Marine Beach', 'Lytham', 'Rossall Point', 'Perch Rock Beach', 'Caldy', 'Seaforth Rocks', 'Otterspool', 'Red Rocks', 'Knab Rock', 'Rhossili Beach', 'Inches Cottages', 'Menara Travel', 'Lighthouse Point', 'Long Rock', 'Coldharbour Sluice', '']]

ifcas = [s.lower() for s in all[0]]
valid_ifcas = []
valid_ifcas = set(list(ne.IFCAS) + [''])
assert set(ifcas).issubset(valid_ifcas), 'IFCAs %s invalid' % set(ifcas).difference(valid_ifcas)
sites = [['Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'Cornwall', 'North East', 'North East', 'North East', 'North East', 'North West', 'North West', 'North West', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Devon and Severn', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Southern', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'Kent and Essex', 'North West', 'North West', 'North West', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'North West', 'North West', 'North West', 'Eastern', 'Eastern', 'Eastern', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'North East', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Isles of Scilly', 'Devon and Severn', 'Devon and Severn', 'Devon and Severn', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Eastern', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Sussex', 'Northumberland', 'Northumberland', 'Northumberland', 'Northumberland', '', '', '', '', '', '', '', 'North West', '', 'North West', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Kent and Essex', '', ''], ['Kingsand', 'Cawsand', 'Penlee Point', 'Polhawn Cove', 'Portwrinkle', 'Downderry', 'Millendreath Beach', 'Lantivet Bay', 'Pencarrow Head', 'Lantic Bay', 'Talland Bay', 'Looe Island', 'Dodman Point', 'Vault Beach', 'Gorran Haven', 'Chapel Point', 'Port Mellon', 'Pentewan', 'Black Head', 'Trenarren', 'Porthpean', 'Gribbin Head', 'Crinnis and Carlyon', 'Golant', 'Carlyon Bay', 'Polkerris', 'Caerhays Bay', 'Portloe', 'Nare Head', 'Carne Beach', 'Pendower Beach', 'Porth Beach', 'Zone Point', 'Saint Anthonys Head', 'St. Maws', 'Turnaware Point', 'Hemmick Beach', 'Caerhays Beach', 'Trefusis Point', 'Swanpool Beach', 'Rosemullion Head', 'Helford River', 'Nare Point', 'Porthallow', 'Porthoustock', 'Manacle Point', 'Coverack', 'Chynhalls Point', 'Black Head', 'Lizard Point', 'Kennack Sands', 'Cadgwith', 'Housel Bay', 'Polpeor Cove', 'Kynance Cove', 'Mullion Cove', 'Poldhu Cove', 'Church Cove', 'Polurrian Cove', 'Gunwallow Cove', 'Loe Bar', 'Rinsey Head', 'Praa Sands', 'Prussia Cove', 'Perran Sands', 'Lamorna Cove', 'Tater-Du', 'Porthcurno', 'Sennen Cove', 'Whitesand Bay', 'Cape Cornwall', 'Pendeen Watch', 'Portheras Cove', 'Gurnards Head', 'Zennor Head', 'Porthmeor Beach', 'St. Ives', 'Gogrevy Point', 'Navax Point', 'Portreth', 'Porthtowan', 'Chapel Porth', 'St. Agnes Head', 'Trevaunance Cove', 'Trevellas Porth', 'Hanover Cove', 'Cligga Head', 'Droskyn Point', 'Perran Bay', 'Ligger Point', 'Penhale Point', 'Holywell Bay', 'Kelsey Head', 'Porth Joke', 'Crantock', 'Pentire Point', 'Fistral Bay', 'Towan Head', 'Porth Island', 'Watergate Bay', 'Beacon Cove', 'Mawgan Porth', 'Trenance Point', 'Park Head', 'Fistral Beach', 'Little Fistral', 'High Place', 'Atlantic Drain', 'Low Point', 'Spy Cove', 'Leanards Rock', 'Hedge Cove', 'Rocket Pole', 'Pigeon Cove', 'Fly Cellars', 'Newquay Harbour', 'Porthcothan Bay', 'Skate Rock', 'Treyarnon Bay', 'Constantine Bay', 'Boobys Bay', 'Dinas Head', 'Trevose Head', 'Mother Ivys Bay', 'Harlyn Bay', 'Trevone Bay', 'Stepper Point', 'Flat Rock', 'Camel Estuary', 'Dammer Bay', 'Polzeath', 'Pentire Point', 'Rumps Point', 'Carnweather Point', 'Kellan Head', 'Port Isaac', 'Barretts Zawn', 'Tregardock Beach', 'Trebarwith Strand', 'Tintagel Head', 'Bossiney Haven', 'Pentargon', 'Dizzard Point', 'Widemouth Sand', 'Bude Bay', 'Duckpool', 'Welcombe Mouth', 'Marsland Mouth', 'Eddystone Reef', 'Pendennis Point', 'Porthallow', 'The Manacles', 'Trevose Head', 'Hartland Point', 'Cremyll Battery', 'The Island', 'The Merlin', 'Palm Rock', 'Jupiter Point', 'Forder', 'Wearde Quay', 'Cargreen', 'Blackhall Colliery Beach', 'Easington Beach', 'Chemical  Beach', 'Blast Beach', 'Dubmill Point', 'Maryport Harbour', 'Whitehaven Pier', 'Babbacombe Bay', 'Bolt Head', 'Brixham Breakwater', 'Lions Den', 'Erme Estuary', 'Princess Pier', 'Haldon Piers', 'Teign Estuary', 'Pottery Quay', 'Eastern Kings', 'Western Kings', 'Rusty Anchor', 'West Hoe Pier', 'Elphinstone Quay', 'Laira Bridge', 'Old Cellars Beach', 'Hilsea Point', 'Durdle Door', 'Friars Cliff', 'Long Groyne', 'Jerrys Point', 'Ringstead Bay', 'Swanage Pier', 'Golden Cap', 'East Ebb Cove', 'Thorncombe Beacon', 'West Bay', 'Cogden Beach', 'Abbotsbury Castle', 'Ferrybridge', 'Weymouth Bay', 'Dungy Head', 'Brandy Bay', 'Egmont Point', 'Chapmans Rock', 'St Albans Head', 'Dancing  Ledge', 'Anvil Point', 'Durlston Head', 'Perveril Point', 'Swanage Bay', 'Ballard Point', 'Old Harry Rocks', 'The Foreland', 'Studland Bay', 'Shell Bay', 'Inner Poole Patch', 'Outer Poole Patch', 'Redcar Scars', 'Flamborough Head', 'Spurn Head', 'Armchair', 'Breil', 'Bungalows', 'Hammer Rock', 'The Naze', 'Foulness Island', 'Herne Bay', 'Botany Bay', 'Pegwell Bay', 'Sandwich Bay', 'Rye Bay', 'Pevensey Bay', 'Langney Point', 'Sovereign Harbour', 'Selsey Bill', 'St. Catherines Point', 'The Needles', 'Poole Bay', 'Bill of Portland', 'Chesil Beach', 'Lyme Bay', 'West Bay', 'Cliff Road', 'Dovercourt Beach', 'Frinton Wall', 'Halfpenny Pier', 'Wallasea Island', 'Southend Pier', 'Admiralty Pier', 'Old Severn Bridge', 'Hamble Common', 'Hurst Shingle Bank', 'Lepe Beach', 'Weston Shore', 'Bembridge Harbour', 'Chale Bay', 'Stanwood Bay', 'Calshot Castle', 'Hill Head', 'Bramble Bank', 'Calshot Light', 'Titchfield Haven', 'Daedalus', 'Browndown Point', 'Stokes Bay Wreck', 'Stokes Bay Pier', 'Haslar Sea Wall', 'No Mans Land Fort', 'Ryde Pier', 'Kings Quay', 'Old Castle Point', 'West Ryde Middle', 'South Bramble', 'West Bramble', 'South Ryde Middle', 'East Bramble', 'Knoll Shoal', 'Mother Bank', 'North Sturbridge', 'Peel Bank', 'Sowley Beach', 'Thorness Bay', 'Norton Beach', 'Totland Bay', 'Alum Bay', 'Shingle Bank', 'The Nodes', 'Freshwater Bay', 'Compton Bay', 'Hanover Point', 'Bull Rocks', 'Brightstone Bay', 'Atherfield Point', 'Chale Bay', 'Puckaster Cove', 'Steephill Bay', 'Dunose Head', 'Luccombe Bay', 'Horse Ledge', 'Shanklin Pier', 'Lake Beach', 'Sandown Bay', 'Culver Cliffs', 'Whitecliff Bay', 'St Helens Fort', 'Ryde Sands', 'Canford Cliffs', 'Durley Chine', 'Kimmeridge Ledges', 'Kimmeridge Bay', 'Avon Beach', 'Christchurch Harbour', 'Hengist Head', 'Pot Bank', 'Christchurch Bay', 'Hill Head', 'Lee-on-the-solent', 'Browndown Bay', 'Stokes Bay', 'Gilkicker Point', 'Haslar Wall', 'Millenium Pier', 'Warsash Beach', 'Western Shore', 'Rolling Mills Jetty', 'Magazine Lane', 'Dibden Bay', 'Calshot', 'Stone Point', 'Coastguard Cottages', 'Park Shore', 'Pennington Marshes', 'Old Pipeline Outflow', 'Hurst Point', 'Hurst Hole', 'Victoria Pier', 'Clarence Beach', 'South Parade Pier', 'Eastney Beach', 'Outfall Jetty', 'Outfall Pier', 'West Wittering Beach', 'East Wittering Beach', 'Bracklesham Bay', 'West Beach', 'East Beach', 'Porchester Creek', 'Fareham Creek', 'Langstone Harbour', 'Chichester Harbour', 'River Medina', 'Yarmouth Pier', 'Deep Point', 'Penninis Head', 'Porthcressa Beach', 'Beltinge Promenade', 'Dover Breakwater', 'Folkstone Pier', 'Marine Parade', 'Reculver Towers', 'Marine Beach', 'Rossall Point', 'River Wyre', 'Anderby Creek', 'Ingoldmells Point', 'Saltfleet Haven', 'Wolla Bank', 'Perch Rock', 'Red Rocks', 'Seaforth Rocks', 'Blakeney Point', 'North Beach', 'Sea Palling Reefs', 'Robin Hoods Bay', 'Filey Bay', 'Filey Brigg', 'Cloughton Wyke', 'Makro', 'Saltwick Bay', 'Hayburn Wyke', 'Staintondale', 'Holy Island', 'Embleton Bay', 'Craster Skeers', 'Coquet Island', 'Creswell Skeers', 'Alnmouth Bridge', 'Beadnell', 'Cambois Rocks', 'Bog Hall Rocks', 'Craster Harbour', 'Hummersea Scar', 'Saltburn Pier', 'Heugh', 'Heugh Breakwater', 'Staincliff', 'Redcar East Scars', 'North Gare', 'South Gare', 'Taylors Island', 'Bar Point', 'Newfoundland Rocks', 'Giants Castle', 'Peninnis Head', 'Porth Cressa Beach', 'Garrison Hill', 'Newford Island', 'Deep Point', 'Menawethan', 'Daymark', 'Eastern Rocks', 'Maiden Bower', 'Scilly Rock', 'Nundeeps', 'Crim Rocks', 'Hanjague', 'Periglis Cove', 'Long Point', 'Browarth Point', 'Dropnose Point', 'The Bar', 'Hoe Point', 'Horse Point', 'Carnew Point', 'Burnt Island', 'Gull Point', 'Pernagie Point', 'Higher Town Bay', 'The Porth', 'White Island', 'New Grimsby Harbour', 'Merchants Point', 'Tobaccomans Point', 'Crow Point', 'Tresco Flats', 'Lizard Point', 'Shipman Head', 'Hangman Island', 'The Quay', 'Gweal', 'Hell Bay', 'Brean Down', 'Hinkley Point', 'Sand Point', 'Aldeburgh Bay', 'Hollesley Bay', 'Blythe Water', 'Aldeburgh Town Beach', 'Landguard Beach', 'Lowestoft South Pier', 'Orford Beach', 'Sizewell', 'Thorpeness Point', 'Brighton Marina', 'Pett Levels', 'Cliff End', 'Hastings Harbour Arm', 'Hasting Harbour', 'Piddinghoe', 'Tidemills', 'Bracklesham Bay', 'The Looe', 'Pagham Harbour', 'Bognor Rocks', 'Bognor Pier', 'Winter Knoll', 'The Ditches', 'Kingmere Rocks', 'Rock Tow', 'Measors Rock', 'Red Shrave', 'Martello Tower', 'Birling Gap', 'Normans Bay', 'Cooden Beach', 'Coxheath Shoals', 'Rye Harbour', 'Broomhill Sands', 'Roker Pier', 'The Black Middens', 'St Marys Island', 'Whitley Bay Beach', 'Calshot', 'Reculver Towers', 'Morte Point', 'Atherfield', 'Carsluith', 'Cowes', 'Freshwater Bay', 'Hoyle Bank', 'Eype', 'Vale Park', 'Twiss Groyne', 'Canvey Island', 'Magazine Lane', 'Soulseat Reservoir', 'Highshore', 'Victoria Park', 'Society Points', 'Whiting Ness', 'The Crawton', 'North Berwick', 'Fife Ness', 'Inverbervie', 'Breascleit Pier', 'Boddin Point', 'Burrow Head', 'Mambeg', 'Craignure Pier', 'Ardgour', 'Newton Shore', 'Terally Bay', 'Ardwell Back Shore', 'Monreith', 'Old House Point', 'Largs Shingle Point', 'Port Logan', 'Isle of Whithorn Harbour', 'Leffnol Beach', 'The Lhen', 'Mooragh Promenade', 'Green Gate', 'Gansey', 'Stanah', 'Cleveleys', 'Marine Beach', 'Lytham', 'Rossall Point', 'Perch Rock Beach', 'Caldy', 'Seaforth Rocks', 'Otterspool', 'Red Rocks', 'Knab Rock', 'Rhossili Beach', 'Inches Cottages', 'Menara Travel', 'Lighthouse Point', 'Long Rock', 'Coldharbour Sluice', '']][1]
sites = [s.lower() for s in sites]

results = ""

for i, site in enumerate(sites):
    rows = gazlib.lookup(site, ifcas[i])
    sources = []; ifc = []
    for row in rows:
        sources += row.source
        ifc += rows.ifca

        
    prefix = '\n%s' % site
    results += ''.join([prefix, '\t%s\t%s' % (sources, ifc)])
    z = 1




