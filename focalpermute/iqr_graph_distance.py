# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Generates cumulative probability data from the interquartile ranges based on the distances
For graphing'''

import numpy as _np
import xlwings as _xw

import mediandistance as md

_MATRICES = md.make_matrices()


def calc_distances():
    '''() -> void
    calculate this distances between this and directed (linear distances)
    '''
    fmmcrisp = _MATRICES['fmm_freq']['crispDirected_crispMine']
    fmmcrisp.directed = fmmcrisp.directed.apply(float)
    fmmcrisp.this = fmmcrisp.this.apply(float)
    fmmcrisp['dist'] = fmmcrisp.directed-fmmcrisp.this
    fmmcrisp['dist'] = fmmcrisp.dist.abs()
    fmmcrisp = fmmcrisp.sort_values(by=['directed', 'dist'])
    gfmmcrisp = fmmcrisp.groupby('directed')
    a = gfmmcrisp.frequency.expanding(1).sum()
    b = gfmmcrisp.dist.expanding(1).sum()
    fmmcrisp['cumfreq'] = _np.hstack([a[0], a[1], a[2], a[3], a[4]])
    fmmcrisp['cumdist'] = _np.hstack([b[0], b[1], b[2], b[3], b[4]])
    fmmcrisp.to_csv('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/iqr_freq/fmm_crispDirected_crispMine.csv')

    fmmfuzzy = _MATRICES['fmm_freq']['focalDirected_focalMine']
    fmmfuzzy.directed = fmmfuzzy.directed.apply(float)
    fmmfuzzy.this = fmmfuzzy.this.apply(float)
    fmmfuzzy['dist'] = fmmfuzzy.directed-fmmfuzzy.this
    fmmfuzzy['dist'] = fmmfuzzy.dist.abs()
    fmmfuzzy = fmmfuzzy.sort_values(by=['directed', 'dist'])
    gfmmfuzzy = fmmfuzzy.groupby('directed')
    a = gfmmfuzzy.frequency.expanding(1).sum()
    b = gfmmfuzzy.dist.expanding(1).sum()
    fmmfuzzy['cumfreq'] = _np.hstack([a[0], a[1], a[2], a[3], a[4]])
    fmmfuzzy['cumdist'] = _np.hstack([b[0], b[1], b[2], b[3], b[4]])
    fmmfuzzy.to_csv('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/iqr_freq/fmm_focalDirected_focalMine.csv')

    pamcrisp = _MATRICES['pam_freq']['crispDirected_crispMine']
    pamcrisp.directed = pamcrisp.directed.apply(float)
    pamcrisp.this = pamcrisp.this.apply(float)
    pamcrisp['dist'] = pamcrisp.directed-pamcrisp.this
    pamcrisp['dist'] = pamcrisp.dist.abs()
    pamcrisp = pamcrisp.sort_values(by=['directed', 'dist'])
    gpamcrisp = pamcrisp.groupby('directed')
    a = gpamcrisp.frequency.expanding(1).sum()
    b = gpamcrisp.dist.expanding(1).sum()
    pamcrisp['cumfreq'] = _np.hstack([a[0], a[1], a[2], a[3]])
    pamcrisp['cumdist'] = _np.hstack([b[0], b[1], b[2], b[3]])
    pamcrisp.to_csv('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/iqr_freq/pam_crispDirected_crispMine.csv')

    pamfuzzy = _MATRICES['pam_freq']['focalDirected_focalMine']
    pamfuzzy.directed = pamfuzzy.directed.apply(float)
    pamfuzzy.this = pamfuzzy.this.apply(float)
    pamfuzzy['dist'] = pamfuzzy.directed-pamfuzzy.this
    pamfuzzy['dist'] = pamfuzzy.dist.abs()
    pamfuzzy = pamfuzzy.sort_values(by=['directed', 'dist'])
    gpamfuzzy = pamfuzzy.groupby('directed')
    a = gpamfuzzy.frequency.expanding(1).sum()
    b = gpamfuzzy.dist.expanding(1).sum()
    pamfuzzy['cumfreq'] = _np.hstack([a[0], a[1], a[2], a[3], a[4]])
    pamfuzzy['cumdist'] = _np.hstack([b[0], b[1], b[2], b[3], b[4]])
    pamfuzzy.to_csv('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/iqr_freq/pam_focalDirected_focalMine.csv')

    wb = _xw.Book()
    ws = wb.sheets.add('fmm_crisp')
    ws.range('A1').value = fmmcrisp

    ws = wb.sheets.add('fmm_focal')
    ws.range('A1').value = fmmfuzzy

    ws = wb.sheets.add('pam_crisp')
    ws.range('A1').value = pamcrisp

    ws = wb.sheets.add('pam_focal')
    ws.range('A1').value = pamfuzzy

    wb.save('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/iqr_freq/iqr_master.xlsx')
    

if __name__ == "__main__":
    calc_distances()
    print('Done')
