# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''helper to add places'''
from funclib.iolib import PrintProgress
from gazetteer import gazlib

raise NotImplementedError #just stop it rerunning.

sites = ['Aberdovey', 'Abersoch', 'Aberystwyth', 'Amlwch', 'Beaumaris', 'Burry Port', 'Caernarfon', 'Cardigan', 'Cemaes Bay', 'Colwyn Bay', 'Conwy', 'Eyemouth', 'Holyhead', 'Menai Bridge', 'Milford Haven', 'New Quay', 'Penarth', 'Porthmadog', 'Pwllheli', 'Rhyl', 'Saundersfoot', 'St. Davids', 'Swansea', 'Y Felinheli']
countries = ['wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'scotland', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales', 'wales']
xs = [-4.046093, -4.504882, -4.087029, -4.332871, -4.090073, -4.249894, -4.273911, -4.687657, -4.452968, -3.72764, -3.826299, -2.086935, -4.64237, -4.159234, -5.04003, -4.356026, -3.165886, -4.129494, -4.40683, -3.491634, -4.696248, -5.280914, -3.932375, -4.212695]
ys = [52.543964, 52.826061, 52.409824, 53.416584, 53.261208, 51.680012, 53.139549, 52.103722, 53.414932, 53.293182, 53.282871, 55.873768, 53.318939, 53.225346, 51.711197, 52.215828, 51.445423, 52.92355, 52.885914, 53.32148, 51.709435, 51.868591, 51.618343, 53.181053]
source = 'cb_master.xlsx#cb_wales_scotland'

assert len(sites) == len(countries) == len(xs) == len(ys), 'Unmatched list lengths'
sources = [source] * len(sites)

PP = PrintProgress(len(sites))

for i, site in enumerate(sites):
    gazlib.add(sources[i], sites[i], xs[i], ys[i],country=countries[i], unique_only=False)
    PP.increment()

print('Done')
