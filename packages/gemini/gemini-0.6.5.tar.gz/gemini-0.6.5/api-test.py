#!/usr/bin/env python
import sys

from gemini import GeminiQuery
from gemini import gemini_constants as const
from gemini import gemini_subjects as subjects

database = sys.argv[1]


gq = GeminiQuery(database)
query = "SELECT variant_id, chrom, start, end, \
                    ref, alt, gene, impact, gts, gt_types, \
                    gt_ref_depths, gt_alt_depths \
         FROM variants"

families = subjects.get_families(database)

gq.run(query)
smp2idx = gq.sample_to_idx
idx = smp2idx['NA12878']

for family in families:
    print family.father_name, family.mother_name, [str(child.name) for child in family.children]

for row in gq:
    if row['gt_types'][idx] == const.HET:
        print row, row['gts'][idx]

