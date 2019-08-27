# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''This scripts calculates probability of getting survey results as extreme as those observed'''
import numpy as np
import random
import funclib.pandaslib as pandaslib
import funclib.iolib as iolib
import funclib.baselib as baselib
CSV = 'C:/temp/survey_validate_overall.py.csv'


TEST_NR = 1000000
IFCA = ['northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'northumberland', 'north east', 'north east', 'north east', 'north east', 'north east', 'north east', 'north west', 'isles of scilly', 'isles of scilly', 'isles of scilly', 'isles of scilly', 'eastern', 'eastern', 'eastern', 'eastern', 'eastern', 'devon and severn', 'devon and severn', 'devon and severn', 'devon and severn', 'devon and severn', 'devon and severn', 'cornwall', 'cornwall', 'cornwall', 'cornwall', 'cornwall', 'north west', 'north west', 'sussex', 'sussex', 'sussex', 'sussex', 'sussex', 'kent and essex', 'kent and essex', 'kent and essex', 'kent and essex', 'kent and essex', 'kent and essex', 'kent and essex', 'kent and essex', 'southern', 'southern', 'southern', 'southern', 'southern', 'southern', 'north west', 'north west', 'north east', 'north east', 'north east', 'north east', 'north east', 'north east']
OUR_RANK = [3, 2, 3, 2, 2, 3, 2, 2, 2, 2, 3, 2, 3, 2, 2, 2, 3, 3, 1, 3, 1, 2, 3, 2, 3, 3, 3, 3, 3, 3, 3, 1, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 2, 1, 3, 3, 3, 3, 1, 3, 1, 2]
SURVEY_RANK = [3, 2, 3, 3, 2, 2, 3, 3, 3, 2, 2, 2, 3, 3, 3, 1, 1, 3, 1, 3, 1, 2, 3, 2, 1, 1, 1, 3, 2, 3, 3, 3, 3, 1, 3, 2, 1, 3, 1, 3, 3, 3, 3, 3, 1, 2, 3, 3, 3, 3, 3, 3, 2, 1, 2, 2, 2, 3, 2, 3, 3, 3, 3, 3, 3, 1, 3, 3, 2, 3, 1, 2]

DISTANCES = [abs(OUR_RANK[i] - x) for i, x in enumerate(SURVEY_RANK)]
MEAN_DISTANCE = sum(DISTANCES)/len(DISTANCES)


def calc_dist(rank):
    '''(list) -> list, list
    calculate mean distance by ifca'''
    dist = [abs(OUR_RANK[i] - x) for i, x in enumerate(rank)] #list of abs distances
    d = {'ifca':IFCA, 'dist':dist}
    df = pandaslib.df_from_dict(d)
    gb = pandaslib.GroupBy(df, ['ifca'], ['dist'], np.mean)
    assert isinstance(gb, pandaslib.GroupBy)     
    df_means = gb.execute()
    ifcas = list(gb.result.index)
    means = baselib.list_flatten(gb.result.dist.values.tolist())
    assert len(ifcas) == len(means)
    return ifcas, means



def main():
    '''main'''
    actual_ifcas, actual_mean_distances = calc_dist(SURVEY_RANK)
    ifca_raw = {'cornwall':[], 'devon and severn':[], 'eastern':[], 'isles of scilly':[], 'kent and essex':[], 'north east':[], 'north west':[], 'northumberland':[], 'southern':[], 'sussex':[]}
    ifca_closer_agreement = {'cornwall':[], 'devon and severn':[], 'eastern':[], 'isles of scilly':[], 'kent and essex':[], 'north east':[], 'north west':[], 'northumberland':[], 'southern':[], 'sussex':[]}

    all_raw = []
    all_closer_agreement = []
    PP = iolib.PrintProgress(TEST_NR)
    for _ in range(TEST_NR):
        rank = [random.choice([1, 2, 3]) for x in range(len(OUR_RANK))]
        for ifca, mean in zip(*calc_dist(rank)):
            ifca_raw[ifca].append(mean)
            ifca_closer_agreement[ifca].append(1 if actual_mean_distances[actual_ifcas.index(ifca)] > mean else 0)
        
        #Now do the overall
        means = [abs(OUR_RANK[i] - x) for i, x in enumerate(rank)]
        m = sum(means)/len(means)
        all_raw.append(m) #the random overall calculated mean distance value
        all_closer_agreement.append(1 if m < MEAN_DISTANCE else 0) #1 if the random calculated value is closer than ours
        PP.increment()
    #expected_mean_distance is 3/9*0 + 4/9*1 + 2/9*2 = 0.889
    output = [['ifca', 'actual_mean_distance', 'expected_mean_distance', 'empirical_mean_distance', 'n', 'closer_n', 'p']]
    #the empirical mean distances differ do not converge to the theoretical because the disttribution of the distances of the original sequence
    #is dependent on the sequence itself.
    for k, v in ifca_closer_agreement.items():
        output.append([k, actual_mean_distances[actual_ifcas.index(k)], 0.889, sum(ifca_raw[k])/len(ifca_raw[k]), TEST_NR, v.count(1), v.count(1)/TEST_NR])

    #add the overall record
    f = all_closer_agreement.count(1)
    output.append(['all', MEAN_DISTANCE, 0.889, sum(all_raw)/len(all_raw), TEST_NR, f, f/TEST_NR])
    iolib.writecsv(CSV, output, inner_as_rows=False)
    print('\nResults saved to: %s' % CSV)






if __name__ == "__main__":
    main()
