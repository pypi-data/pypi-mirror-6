import gffutils
db = gffutils.FeatureDB('dmel-all-no-analysis-r5.54.gff.cleaned.db')
snoRNA_genes = []
for i in db.features_of_type('snoRNA'):
    snoRNA_genes.extend([k.id for k in db.parents(i, level=1, featuretype='gene')])
