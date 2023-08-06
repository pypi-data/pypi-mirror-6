"""
Taxa Report
"""

import functools
import logging
import mgkit.plots
import mgkit.snps.funcs
import mgkit.snps.filter
import mgkit.snps.mapper
import matplotlib.pyplot as plt

LOG = logging.getLogger(__name__)

try:
    import seaborn as sns
    LOG.debug("Seaborn is installed, using it.")
except ImportError:
    pass

import string

template = """
Basic report
============

Taxa
----

.. figure:: $taxa_pdf
    :scale: 50%

    Variation among the taxa found at the $rank level

.. csv-table::
    :file: $taxa_csv

eggNOG
------

.. figure:: $eggnog_pdf
    :scale: 50%

    Variation of eggNOG categories

.. csv-table::
    :file: $eggnog_csv

"""


EGGNOG_COLOURS = {
    'INFORMATION STORAGE AND PROCESSING': '#E41A1C',
    'CELLULAR PROCESSES AND SIGNALING': '#377EB8',
    'METABOLISM': '#4DAF4A',
    'POORLY CHARACTERIZED': '#984EA3'
}


def get_rank_dataframe(snp_data, taxonomy, min_num=3, rank='order'):

    taxon_func = functools.partial(
        mgkit.snps.mapper.map_taxon_id_to_rank,
        taxonomy=taxonomy,
        rank=rank
    )

    filters = mgkit.snps.filter.get_default_filters(taxonomy)

    dataframe = mgkit.snps.funcs.combine_sample_snps(
        snp_data,
        min_num,
        filters,
        taxon_func=taxon_func,
        gene_func=None,
        index_type='taxon'
    )

    return dataframe


def get_mapping_dataframe(snp_data, taxonomy, gene_map, min_num=3):

    gene_func = functools.partial(
        mgkit.snps.mapper.map_gene_id,
        gene_map=gene_map
    )

    filters = mgkit.snps.filter.get_default_filters(taxonomy)

    dataframe = mgkit.snps.funcs.combine_sample_snps(
        snp_data,
        min_num,
        filters,
        taxon_func=None,
        gene_func=gene_func,
        index_type='gene'
    )

    return dataframe


def plot_taxa_boxplot(dataframe, taxonomy, ax, log_scale=True, fonts=None):

    porder = mgkit.snps.funcs.order_ratios(dataframe.T)

    pcolor = mgkit.plots.get_taxon_colors_new(porder, taxonomy)

    label_map = dict(
        (taxon_id, taxonomy[taxon_id].s_name) for taxon_id in porder
    )

    mgkit.plots.boxplot_dataframe(
        dataframe,
        porder,
        ax,
        label_map=label_map,
        data_colours=pcolor,
        fonts=fonts
    )
    if log_scale:
        ax.set_yscale('symlog')

    ax.grid(True)


def plot_categories_boxplot(dataframe, ax, map_names=None, map_colours=None,
                            fonts=None):

    porder = mgkit.snps.funcs.order_ratios(dataframe.T)

    mgkit.plots.boxplot_dataframe(
        dataframe,
        porder,
        ax,
        label_map=map_names,
        data_colours=map_colours,
        fonts=fonts
    )

    ax.grid(True)


#tabella: usare direttiva csv-table con :file:
#dataframe.to_csv con float_format='%.2f'


def get_single_figure(dpi=300, figsize=(10, 20)):
    fig = plt.figure(dpi=dpi, figsize=figsize)
    ax = fig.add_subplot(111)
    return fig, ax


def test_report(a, tx, ko_cat):

    df = get_mapping_dataframe(a, tx, gene_map=ko_cat)

    fig, ax = get_single_figure()

    plot_categories_boxplot(df, ax, map_colours=EGGNOG_COLOURS)

    cat_pdf = 'test-cat.png'

    fig.tight_layout()
    fig.savefig(cat_pdf)

    df['mean'] = df.mean(axis=1)

    df.sort(axis=0, ascending=False, columns=['mean'])

    cat_csv = 'test-cat.csv'

    df.to_csv(cat_csv, float_format='%.2f')

    df = get_rank_dataframe(a, tx, rank='order')

    fig, ax = get_single_figure(figsize=(30, 50))

    plot_taxa_boxplot(df, tx, ax)

    taxa_pdf = 'test-taxa.png'

    fig.tight_layout()
    fig.savefig(taxa_pdf)

    df['mean'] = df.mean(axis=1)

    df.sort(axis=0, ascending=False, columns=['mean'])

    taxa_csv = 'test-taxa.csv'

    df[:10].to_csv(taxa_csv, float_format='%.2f')

    f = open('test.rst', 'w')

    tmp = string.Template(template)

    f.write(
        tmp.substitute(
            taxa_pdf=taxa_pdf,
            taxa_csv=taxa_csv,
            eggnog_csv=cat_csv,
            eggnog_pdf=cat_pdf,
            rank='order'
        )
    )
    f.close()

def test_data():
    import cPickle as pickle
    import mgkit
    a = pickle.load(open('rfi_snp_blast_set.pickle','rb'))
    tx = mgkit.taxon.UniprotTaxonomy('data/taxonomy_full.pickle')
    import mgkit.mappings.eggnog
    import mgkit.utils.dictionary
    eg = mgkit.mappings.eggnog.Kegg2NogMapper('data/eggnog.pickle')

    ko_cat = mgkit.utils.dictionary.combine_dict(
        eg.get_ko_map(),
        mgkit.utils.dictionary.reverse_mapping(
            mgkit.mappings.eggnog.EGGNOG_CAT_MAP
        )
    )

    return a, tx, ko_cat
