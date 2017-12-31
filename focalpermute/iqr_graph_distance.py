# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Generates cumulative probability data from the interquartile ranges based on the distances
For graphing'''
#https://stackoverflow.com/questions/14529838/apply-multiple-functions-to-multiple-groupby-columns

import numpy as _np
import xlwings as _xw
import pandas as _pd

import mediandistance as md

_MATRICES = md.make_matrices()
_OUTFILE = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/iqr_freq/iqr_master.xlsx'

def calc_distances():
    '''() -> void
    calculate this distances between this and directed (linear distances)
    '''
    def calc_dist(df):
        '''(pandas.DataFrame) -> pandas.DataFrame, pandas.DataFrame

        Calculate all the metrics for my distance analysis.

        First dataframe contains the data for each grouped of directed values
        Second dataframe returns the summary values of the first dataframe
        '''
        assert isinstance(df, _pd.DataFrame)

        df.directed = df.directed.apply(float)
        df.this = df.this.apply(float)
        df.frequency = df.frequency.apply(float)
        df['dist'] = df.directed-df.this
        df['dist'] = df.dist.abs()
        df = df.sort_values(by=['directed', 'dist'])
        g_df = df.groupby('directed')
        df['id'] = _np.hstack(g_df.this.expanding().count())

        #cumulative frequency from frequency
        
        #df['propdist'] = g_df.cumdist/g_df.sumdist
        #df['cumdist'] = _np.hstack(g_df.dist.expanding(1).sum())
        #df['sumdist'] = g_df.frequency.transform(lambda x:(x.sum()))

        df['sumfreq'] = g_df.frequency.transform(lambda x: (x.sum()))
        df['cumfreq'] = _np.hstack(g_df.frequency.expanding(1).sum())
        df['propfreq'] = df.cumfreq/df.sumfreq
        df['expected_prop'] = _np.hstack(g_df.this.expanding().count()*(1/len(g_df)))
        df['expected'] = df['sumfreq']*(1/len(g_df))
        #now create a dataframe for the overall data

        g_all = df.groupby('id')

        df_all = _pd.DataFrame(g_all.frequency.aggregate(_np.sum))
        df_all['dist'] = _np.arange(0, len(df_all), 1)
        assert isinstance(df_all, _pd.DataFrame)

        df_all['sumfreq'] = df_all.frequency.sum()
        df_all['cumfreq'] = df_all['frequency'] = df_all.frequency.cumsum()
        df_all['propfreq'] = df_all.cumfreq/df_all.sumfreq
        df_all['expected_prop'] = _np.arange(1/len(df_all), 1.2, 1/len(df_all))
        df_all['expected'] = df['sumfreq']*(1/len(df_all))

        return df, df_all
    
    def save():
        '''save to excel'''
        wb = _xw.Book()

        ws = wb.sheets.add('pam_focal')
        #ws.range('A1').value = pamfuzzy
        #ws.range('N1').value = pamfuzzy_all
        ws.range('A1').value = pamfuzzy_sigma

        ws = wb.sheets.add('pam_crisp')
        #ws.range('A1').value = pamcrisp
        #ws.range('N1').value = pamcrisp_all
        ws.range('A1').value = pamcrisp_sigma

        ws = wb.sheets.add('fmm_focal')
        #ws.range('A1').value = fmmfuzzy
        #ws.range('N1').value = fmmfuzzy_all
        ws.range('A1').value = fmmfuzzy_sigma

        ws = wb.sheets.add('fmm_crisp')
        #ws.range('A1').value = fmmcrisp
        #ws.range('N1').value = fmmcrisp_all
        ws.range('A1').value = fmmcrisp_sigma
        
        ws = wb.sheets.add('info')
        ws.range('A1').value = 'data is IQR frequences in variable _MATRICES, generated from the focalpermute.mediandistance.py\n' \
                                'The processed data as it appears in this spreadsheet was created by focalpermute.iqr_graph_distance.py'
        wb.save(_OUTFILE)
    
    def get_for_plot(df, df_all, step):
        '''pandas.dataframe, pandas.dataframe -> pandas.dataframe
        Get and format the data for plotting
        in sigmaplot
        '''
        assert isinstance(df, _pd.DataFrame)
        df_out = _pd.DataFrame({'x':list(range(0, step))})
        df_out['expected'] = _np.arange(1/step, 1 + 1/step, 1/step)

        step2 = step*step
        z = zip(list(range(0, step2, step)), list(range(0 + step, step2 + step, step)))
        for x in z:
            assert isinstance(x, tuple)
            col1 = 'propfreq' + str(int(x[0]/step))
            s = slice(int(x[0]), int(x[1]))
            df_out[col1] = _np.array(df['propfreq'][s]).astype(float)

        df_out['propfreqall'] = _np.array(df_all['propfreq']).astype(float)
        return df_out


    fmmcrisp = _MATRICES['fmm_freq']['crispDirected_crispMine']
    fmmcrisp, fmmcrisp_all = calc_dist(fmmcrisp)
    fmmcrisp_sigma = get_for_plot(fmmcrisp, fmmcrisp_all, 5)

    fmmfuzzy = _MATRICES['fmm_freq']['focalDirected_focalMine']
    fmmfuzzy, fmmfuzzy_all = calc_dist(fmmfuzzy)
    fmmfuzzy_sigma = get_for_plot(fmmfuzzy, fmmfuzzy_all, 5)

    pamcrisp = _MATRICES['pam_freq']['crispDirected_crispMine']
    pamcrisp, pamcrisp_all = calc_dist(pamcrisp)
    pamcrisp_sigma = get_for_plot(pamcrisp, pamcrisp_all, 4)

    pamfuzzy = _MATRICES['pam_freq']['focalDirected_focalMine']
    pamfuzzy, pamfuzzy_all = calc_dist(pamfuzzy)
    pamfuzzy_sigma = get_for_plot(pamfuzzy, pamfuzzy_all, 5)

    save()
    

if __name__ == "__main__":
    calc_distances()
