import sys, os, glob, subprocess
from collections import OrderedDict

import numpy as np
import scipy.io
import pandas
import seaborn as sns
from nltk.corpus import wordnet as wn

sys.path.insert(0, '../../psychopy_ext')
from psychopy_ext import stats

import base
from base import Base, Shape


class Stefania(Shape):

    def __init__(self, *args, **kwargs):
        super(Stefania, self).__init__(*args, **kwargs)
        self.kwargs = kwargs
        kinds = np.meshgrid(range(6), range(9))
        kinds = [kinds[1], kinds[1], kinds[0], (kinds[0] < 3).astype(int)]
        self.dims = OrderedDict()
        for dim, kind in zip(['px', 'shape', 'category', 'natural-vs-manmade'], kinds):
            self.dims[dim] = kind

    @base._check_force('dis')
    def dissimilarity(self):
        """
        Stefania used correlation in her study, but we'll do euclinean  to keep it consistent with other experiments.
        """
        self.classify()
        self.dis = super(base.Base, self).dissimilarity(self.resps,
                                                   kind='euclidean')
        self.save('dis')

    def mds(self):
        self.dissimilarity()
        path = os.path.join('img', 'png', '*.*')
        ims = sorted(glob.glob(path))
        super(Base, self).mds(self.dis, ims, kind='metric')
        self.show(pref='mds')

    def corr(self):
        super(Stefania, self).corr(['shape', 'category'], subplots=False, **self.kwargs)

    def plot_lin(self):
        xlabel = '%s layer' % self.model_name
        self.lin = self.lin.rename(columns={'layer': xlabel})
        self.plot_single_model(self.lin, subplots=True)

    def filter_imagenet(self):
        if self.filter:
            return self.pred_acc(compute_acc=False)
        else:
            return None

    # def plot_lin(self):
    #     xlabel = '%s layers' % self.model_name
    #     self.lin = self.lin.rename(columns={'layer': xlabel})
    #     colors = sns.color_palette('Set2')[1:len(self.dims)+1]

    #     for (kind, value), color in zip(self.dims.items(), colors):
    #         chance = 1. / len(np.unique(value))
    #         df = self.lin[self.lin.kind==kind]
    #         sns.set_palette([color])
    #         if self.model_name == 'GoogleNet':
    #             g = sns.factorplot(xlabel, 'accuracy', data=df,
    #                               kind='point', markers='None', ci=0)
    #             g.axes.flat[0].set_xticklabels([])

    #             # import matplotlib.lines as mlines
    #             # handles = []
    #             # for mname, color in zip(self.dims.keys(), colors):
    #             #     patch = mlines.Line2D([], [], color=color, label=mname)
    #             #     handles.append(patch)
    #             # g.axes.flat[0].legend(handles=handles, loc='best')
    #         else:
    #             g = sns.factorplot(xlabel, 'accuracy', data=df,
    #                               kind='point')
    #         g.axes.flat[0].axhline(chance, ls='--', c='.2')
    #         g.axes.flat[0].set_ylim([0,1])
    #         sns.plt.title(kind)

    #         self.show(pref='lin_%s' % kind)

    def filter_stim(self):
        with open('names.txt', 'rb') as f:
            lines = f.readlines()
        f = open('names-matched.csv', 'wb')
        for line in lines:
            name = line.strip('\r\n')#.split(',')[0]
            syns = wn.synsets('_'.join(name.split()), pos='n')
            print '~' * 40
            print
            print name
            print
            for n, syn in enumerate(syns):
                print n, '-', syn.definition()
            print
            while True:
                num = raw_input('Which definition is correct? (or type another name to check) ')
                if num == 'q':
                    f.close()
                    sys.exit()
                try:
                    num = int(num)
                except:
                    print
                    print name
                    print
                    syns += wn.synsets(num, pos='n')
                    for n, syn in enumerate(syns):
                        print n, ' - ', syn.definition()
                    print
                else:
                    if num in range(len(syns)):
                        break

            syn = syns[num]
            synid = syn.pos() + str(syn.offset()).zfill(8)
            f.write(','.join([synid, name, syn.definition()]))
        f.close()
                                                                                                                                                                                          
                                                                                                                                                                                                        

    # def pred_acc(self, *args, **kwargs):
    #     self.predict()
    #     synstef = self.synsets_from_csv('names-matched.csv')
    #     df = super(Stefania, self).pred_acc(synstef)
    #     print df[['names', 'kind', 'accuracy', 'imgnames']]
    #     acc = df[df.id==df.imgid].accuracy
    #     acc_exact = acc.sum() / float(df.accuracy.count())
    #     print 'Exact match: {:.2f}'.format(acc_exact)
    #     print 'Exact match or more specific: {:.2f}'.format(df.accuracy.mean())
    #     # return df

def gen_alpha(**kwargs):
    for fn in sorted(glob.glob('img/*.jpg')):
        fname = os.path.basename(fn)
        newname = fname.split('.')[0] + '.png'
        newfname = os.path.join('img/png', newname)
        fuzz = '3%'
        # if fname == 'hopStim_054.jpg':
        #     fuzz = '5%'
        # else:
        #     fuzz = '10%'
        subprocess.call(('convert {} -alpha set -channel RGBA -fuzz ' + fuzz +
                        ' -fill none -floodfill +0+0 white -blur 1x1 {}').format(fn, newfname).split())

def gen_sil(**kwargs):
    for fn in sorted(glob.glob('img/*.jpg')):
        fname = os.path.basename(fn)
        newname = fname.split('.')[0] + '.png'
        newfname = os.path.join('img/sil_new', newname)
        fuzz = '3%'
        subprocess.call(('convert {} -alpha set -channel RGBA -fuzz ' + fuzz +
                        ' -fill none -floodfill +0+0 white -blur 1x1 '
                        '-alpha extract -negate {}').format(fn, newfname).split())

def corr_models(mods1_dis, mods2_dis):
    df = []
    for mods1_label, mods1_data in mods1_dis.items():
        inds = np.triu_indices(mods1_data.shape[0], k=1)
        for mods2_label, mods2_data in mods2_dis.items():
            corr = np.corrcoef(mods1_data[inds], mods2_data[inds])[0,1]
            df.append([mods1_label, mods2_label, corr])
    df = pandas.DataFrame(df, columns=['perception', 'models', 'correlation'])
    df = stats.factorize(df)
    sns.factorplot('perception', 'correlation', 'models',
                   data=df, kind='bar')
    return df

def corrplot(mod_dis):
    df_model = []
    for label, data in mod_dis.items():
        inds = np.triu_indices(data.shape[0], k=1)
        df_model.append(data[inds])

    df_model = pandas.DataFrame(np.array(df_model).T,
                                columns=mod_dis.keys())

    sns.corrplot(df_model)

def corr_neural_model_avg(neural_dis, mod_dis):
    df = []
    avg = [['pixelwise',
            ('BA17', 'BA18', 'TOS', 'postPPA',
            'LOTCobject', 'LOTCface')],

            ['shape',
            ('LOTCbody', 'LOTChand',
            'VOTCobject', 'VOTCbody/face')],

            ['animate/inanimate',
            ('LOTCobject', 'LOTCface', 'LOTCbody', 'LOTChand',
            'VOTCobject', 'VOTCbody/face')],

            ['nat/artifact', ('IPS', 'SPL',
             'IPL', 'DPFC')]
           ]

    for a, rois in avg:
        for mod_label, mod_data in mod_dis.items():
            for k in xrange(neural_dis.values()[0].shape[-1]):
                nd_avg = []
                for neural_label, neural_data in neural_dis.items():
                    if neural_label in rois:
                        nd_avg.append(neural_data[:,:,k])
                nd_avg = np.average(nd_avg, axis=0)

                inds = np.triu_indices(nd_avg.shape[0], k=1)
                corr = np.corrcoef(nd_avg[inds],
                                   mod_data[inds])[0,1]

                df.append([a, mod_label, k, corr])
    df = pandas.DataFrame(df, columns=['neural', 'model',
                                       'subjid', 'correlation'])
    df = stats.factorize(df)
    sns.factorplot('neural', 'correlation', 'model', data=df, kind='bar')
    return df

def corr_neural_model(neural_dis, mod_dis):
    df = []

    for mod_label, mod_data in mod_dis.items():
        for k in xrange(neural_dis.values()[0].shape[-1]):
            nd_avg = []
            for neural_label, neural_data in neural_dis.items():
                inds = np.triu_indices(mod_data.shape[0], k=1)
                corr = np.corrcoef(neural_data[:,:,k][inds],
                                   mod_data[inds])[0,1]

                df.append([neural_label, mod_label, k, corr])
    df = pandas.DataFrame(df, columns=['neural', 'model',
                                       'subjid', 'correlation'])
    df = stats.factorize(df)
    sns.factorplot('neural', 'correlation', 'model', data=df, kind='bar')
    return df

def compare_lin(**kwargs):
    lin = base.compare(Stefania, 'linear_clf', 'lin', **kwargs)
    g = sns.factorplot('model', 'accuracy', col='kind', data=lin,
                        kind='bar', color='steelblue')
    chances = [1./len(np.unique(val)) for val in Stefania().dims.values()]
    for ax, chance in zip(g.axes.flat, chances):
        ax.axhline(chance, ls='--', c='.2')
    base.show(pref='lin', **kwargs)

# def lin_all(**kwargs):
#     deep = ['CaffeNet fc6', 'HMO', 'Places fc6', 'GoogleNet loss3/classifier']
#     base.lin_all(Stefania, deep, kind='shape', dims=Stefania(**kwargs).dims, **kwargs)

#     deep = ['CaffeNet fc8', 'HMO', 'Places fc8', 'GoogleNet loss3/classifier']
#     base.lin_all(Stefania, deep, kind='category', dims=Stefania(**kwargs).dims, **kwargs)

#     deep = ['CaffeNet fc8', 'HMO', 'Places fc8', 'GoogleNet loss3/classifier']
#     base.lin_all(Stefania, deep, kind='natural/manmade', dims=Stefania(**kwargs).dims, **kwargs)

# def corr_deep(model_name='', **kwargs):
#     models1 = ['px', 'shape', 'category']
#     dims = OrderedDict([(l,d.ravel()) for l,d in Stefania(**kwargs).dims.items()])
#     base.corr_deep(models1, model_name=model_name, dims=dims, **kwargs)

# def corr_all(**kwargs):
#     dims = OrderedDict([(l,d.ravel()) for l,d in Stefania(**kwargs).dims.items()])

#     deep = ['CaffeNet', 'Places', 'HMO', 'VGG-19', 'GoogleNet']
#     orange = sns.color_palette('Set2', 8)[1]
#     base.corr_all('shape', deep, dims=dims, color=orange, **kwargs)

#     deep = ['CaffeNet', 'Places', 'HMO', 'VGG-19', 'GoogleNet']
#     purple = sns.color_palette('Set2', 8)[2]
#     base.corr_all('category', deep, dims=dims, color=purple, **kwargs)

def corr_all(**kwargs):
    if kwargs['subset'] == 'sil':
        base.DEEP = ['CaffeNet', 'VGG-19', 'GoogleNet']
    base.compare_all(Stefania, kind='corr', subplots=True, **kwargs)

def corr_all_layers(**kwargs):
    base.DEEP = ['CaffeNet', 'VGG-19', 'GoogleNet']
    colors = sns.color_palette('Set2')[1:3]
    base.corr_all_layers(Stefania, kinds=['shape', 'category'], colors=colors,
                         ylim=[-.1,1], **kwargs)

def lin_all(**kwargs):
    base.compare_all(Stefania, kind='lin', subplots=True, **kwargs)

def run(**kwargs):
    getattr(Stefania(**kwargs), kwargs['func'])()
