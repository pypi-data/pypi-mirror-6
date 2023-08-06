# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import csv
import json
import pickle
import re

import nibabel as nb


def get_image_info(image_path, get_tr=True):
    """Return the image info readed from the image using Nibabel"""
    img = nb.load(image_path)
    data = {}
    data['voxel_res_x'] = float(img.get_header()['pixdim'][1])
    data['voxel_res_y'] = float(img.get_header()['pixdim'][2])
    data['voxel_res_z'] = float(img.get_header()['pixdim'][3])
    data['shape_x'] = int(img.get_shape()[0])
    data['shape_y'] = int(img.get_shape()[1])
    data['shape_z'] = int(img.get_shape()[2])
    data['shape_t'] = int(img.get_shape()[3]) if len(img.get_shape()) == 4 else None
    data['affine'] = pickle.dumps(img.get_affine().tolist())
    desc = str(img.get_header()['descrip'])
    # Use desc ?
    try:
        if get_tr:
            tr, te = re.findall(
                'TR=(.*)ms.*TE=(.*)ms', desc)[0]
            data['tr'] = float(tr)
            data['te'] = float(te)
    except Exception, e:
        data['tr'] = None
        data['te'] = None

    return data

def import_genes(ref_chr_path, ref_gene_path):
    """Import genes"""
    chromosomes = json.load(open(ref_chr_path))
    ref_gene = []
    for row in csv.reader(open(ref_gene_path), delimiter='\t'):
        gene = {}
        gene['name'] = unicode(row[0])
        gene['gene_id'] = unicode(row[0])
        gene['uri'] = None
        gene['start_position'] = int(row[1])
        gene['stop_position'] = int(row[2])
        gene['chromosome'] = row[3].split('_')[0]
        ref_gene.append(gene)
    return ref_gene

def import_chromosomes(ref_chr_path):
    """Import chromosomes"""
    chromosomes = json.load(open(ref_chr_path))
    chrs = []
    for chr_id in chromosomes:
        chr = {}
        chr['name'] = u'chr%s' % chromosomes[chr_id].upper()
        chr['identifier'] = unicode(chr['name'])
        chrs.append(chr)
    return chrs

def import_snps(ref_chr_path, ref_snp_path):
    """Import snps"""
    chromosomes = json.load(open(ref_chr_path))
    snps = []
    for row in csv.reader(open(ref_snp_path), delimiter='\t'):
        snp = {}
        if row[0] == '0':
            continue
        chr_id = chromosomes[row[0]]
        snp['rs_id'] = unicode(row[1])
        snp['position'] = int(row[3])
        snp['chromosome'] = u'chr%s' % chr_id.upper()
        snps.append(snp)
    return snps
