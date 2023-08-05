#!/usr/bin/env python
# encoding: utf-8
"""
genetic_models.py

Genetic models take a family object with individuals and variants and annotates for each variant which models they follow in this family.

The following models are checked:

- Autosomal Dominant(AD)
- Autosomal Dominant De Novo(AD_DN)
- Autosomal Recessive(AR)
- Autosomal Recessive De Novo(AR_DN)
- Autosomal Recesive Compound.

In this model a variant must imply affected status, otherwise it can not be dominant. All sick has to be ay least heterozygote for the variant and all healthy can not have it.

We will assume that each individual that we have information about is present among the individual in self.family.individuals.


is the individual sick?

    - If the individual is homozygote alternative then AD/AD-denovo and AR/AR-denovo are ok

    - If the individual is is heterozygote then AD/AD-denovo are ok but AR/AR-denovo are not ok

    - If the individual is homozygote reference no model is ok

    - If the individual has no call all models are ok



is the individual healthy?

    - If the individual is homozygote alternative then no model is ok

    - If the individual is heterozygote then AR/AR-denove are ok but AD/AD-denovo are not ok

    - If the individual is homozygote referense all models are ok

    - If there is no call all models are ok



is there no known phenotype?

    - All models are ok for all variants



Created by Måns Magnusson on 2013-02-12.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import os
import sys
from datetime import datetime
from pprint import pprint as pp

from Mip_Family_Analysis.Variants import genotype
from Mip_Family_Analysis.Utils import pair_generator

def check_genetic_models(variant_batch, family, verbose = False, proc_name = None):
    #A variant batch is a dictionary on the form {gene_id: {variant_id:variant_dict}}
    # Start by getting the genotypes for each variant:
    for gene in variant_batch:
        for variant_id in variant_batch[gene]:
            genotypes = {}
            for individual in family.individuals:
                gt_info = variant_batch[gene][variant_id]['IDN:'+individual.individual_id].split(':')[1].split('=')[1]
                individual_genotype = genotype.Genotype(GT=gt_info)
                genotypes[individual.individual_id] = individual_genotype
            variant_batch[gene][variant_id]['Genotypes'] = genotypes
    
    # Now check the genetic models:
    for gene in variant_batch:
        compound_candidates = []
        compound_pairs = []
        # We look at compounds only when variants are in genes:
        if gene != '-':
            # First remove all variants that can't be compounds to reduce the number of lookup's:
            compound_candidates = check_compound_candidates(variant_batch[gene], family)
            # print compound_candidates
            if len(compound_candidates) > 1:
            # Now check the compound candidates:
                compound_pairs = check_compound(compound_candidates, family)
        
        for variant_id in variant_batch[gene]:
            variant_batch[gene][variant_id]['Inheritance_model'] = {'X' : True, 'X_dn' : True, 'AD' : True, 'AD_denovo' : True, 
                                            'AR_hom' : True, 'AR_hom_denovo' : True, 'AR_compound' : False}
            variant_batch[gene][variant_id]['Compounds'] = {}
            # Only check X-linked for the variants in the X-chromosome:
            # For X-linked we do not need to check the other models
            if variant_batch[gene][variant_id]['Chromosome'] == 'X':
                check_X(variant_batch[gene][variant_id], family)
                variant_batch[gene][variant_id]['Inheritance_model']['AD'] = False
                variant_batch[gene][variant_id]['Inheritance_model']['AD_denovo'] = False
                variant_batch[gene][variant_id]['Inheritance_model']['AR_hom'] = False
                variant_batch[gene][variant_id]['Inheritance_model']['AR_hom_denovo'] = False
            else:
                variant_batch[gene][variant_id]['Inheritance_model']['X'] = False
                variant_batch[gene][variant_id]['Inheritance_model']['X_dn'] = False
            # Check the dominant model:
                check_dominant(variant_batch[gene][variant_id], family)
            # Check the recessive model:
                check_recessive(variant_batch[gene][variant_id], family)
            
        if len(compound_pairs) > 0:
            for pair in compound_pairs:
                variant_pair = []
                for variant in pair:
                    variant_pair.append(variant)
                # Add the compound pair id to each variant    
                variant_batch[gene][variant_pair[0]]['Compounds'][variant_pair[1]] = 0
                variant_batch[gene][variant_pair[1]]['Compounds'][variant_pair[1]] = 0
                variant_batch[gene][variant_pair[0]]['Inheritance_model']['AR_compound'] = True
                variant_batch[gene][variant_pair[1]]['Inheritance_model']['AR_compound'] = True
    
    # for gene in variant_batch:
    #     for variant_id in variant_batch[gene]:
    #         del variant_batch[gene][variant_id]['Genotypes']
            
    return variant_batch

def check_compound_candidates(variants, family):
    """Sort out the compound candidates, this function is used to reduce the number of potential candidates."""
    #Make a copy of the dictionary to not change the original one. {variant_id:variant_dict}
    comp_candidates = dict((variant_id, variants[variant_id]) for variant_id in variants)
    
    for individual in family.individuals:
        individual_variants = {}
        for variant_id in variants:
            individual_genotype = variants[variant_id]['Genotypes'].get(individual.individual_id, genotype.Genotype())
            # If an individual is affected:
            if individual.affected():
                # It has to be heterozygote for the variant to be a candidate
                if not individual_genotype.heterozygote:
                    if variant_id in comp_candidates:
                        del comp_candidates[variant_id]
                else:
                    individual_variants[variant_id] = ''
            else:#If individual is healthy or not known
                if individual_genotype.homo_alt:
                    if variant_id in comp_candidates:
                        del comp_candidates[variant_id]
                elif individual_genotype.heterozygote:
                    individual_variants[variant_id] = ''
        #If the individual is sick then all potential compound candidates of a gene must exist in that individual.
        if individual.affected():
            if len(individual_variants) > 1:
                for variant_id in comp_candidates:
                    if variant_id not in individual_variants:
                        del comp_candidates[variant_id]
            else:
                # If a sick individual dont have any compounds pairs there are no compound candidates.
                comp_candidates = {}
        # else:
        #     #If an individual is healthy and have compound pairs they can not be deleterious:
        #     if len(individual_variants) > 1:
        #         for variant_id in individual_variants:
        #             if variant_id in comp_candidates:
        #                 del comp_candidates[variant_id]
    # This is a dictionary like {variant_id: {ind_id: genotype_object}}
    return comp_candidates

def check_compound(variants, family):
    """Check which variants in the list that follow the compound heterozygous model. 
    We need to go through all variants and sort them into their corresponding genes 
    to see which that are candidates for compound heterozygotes first. 
    The cheapest way to store them are in a hash table. After this we need to go
     through all pairs, if both variants of a pair is found in a healthy individual
      the pair is not a deleterious compound heterozygote."""
                
    true_variant_pairs = []
        
    # Returns a generator with all possible pairs for this individual, the pairs are python sets:
    my_pairs = pair_generator.Pair_Generator(variants.keys())
    for pair in my_pairs.generate_pairs():
        true_variant_pairs.append(pair)
        variant_pair = []
        for variant in pair:
            variant_pair.append(variant)
        variant_1 = variant_pair[0]
        variant_2 = variant_pair[1]
    # Check in all individuals what genotypes that are in the trio based of the individual picked.
        for individual in family.individuals:
            genotype_1 = variants[variant_1]['Genotypes'].get(individual.individual_id, genotype.Genotype())
            genotype_2 = variants[variant_2]['Genotypes'].get(individual.individual_id, genotype.Genotype())
            # If the individual is not sick and have both variants it can not be compound
            if individual.phenotype != 2:
                if genotype_1.has_variant and genotype_2.has_variant:
                    true_variant_pairs.remove(pair)
                    break
            else:# The case where the individual is affected
                mother_id = individual.mother
                mother_genotype_1 = variants[variant_1]['Genotypes'].get(mother_id, genotype.Genotype())
                mother_genotype_2 = variants[variant_2]['Genotypes'].get(mother_id, genotype.Genotype())
                mother_phenotype = family.get_phenotype(mother_id)
                
                father_id = individual.father
                father_genotype_1 = variants[variant_1]['Genotypes'].get(father_id, genotype.Genotype())
                father_genotype_2 = variants[variant_2]['Genotypes'].get(father_id, genotype.Genotype())
                father_phenotype = family.get_phenotype(father_id)
                # If a parent has both variants and is unaffected it can not be a compound.
                # This will change when we get the phasing information.
                if ((mother_genotype_1.heterozygote and mother_genotype_2.heterozygote and mother_phenotype == 1) or (father_genotype_1.heterozygote and father_genotype_2.heterozygote and father_phenotype == 1)):
                    true_variant_pairs.remove(pair)
                    break
    return true_variant_pairs

def check_X(variant, family):
    """Check if the variant follows the x linked patter of inheritance in this family."""
    for individual in family.individuals:
        # Get the genotype for this variant for this individual
        individual_genotype = variant['Genotypes'].get(individual.individual_id, genotype.Genotype())
    
        # The case where the individual is healthy
        if individual.phenotype == 1:
        #The case where the individual is a male
            if individual.sex == 1:
                if individual_genotype.has_variant:
        # If the individual is healthy, male and have a variation it can not be x-linked.
                    variant['Inheritance_model']['X'] = False
        
            #The case where the individual is a female
            elif individual.sex == 2:
                # If the individual is HEALTHY, female and is homozygote alternative it can not be x - linked.
                if individual_genotype.homo_alt:
                    variant['Inheritance_model']['X'] = False
                    variant['Inheritance_model']['X_dn'] = False
    
        # The case when the individual is sick
        elif individual.phenotype == 2:
        #If the individual is sick and homozygote ref it can not be x-linked
            if individual_genotype.homo_ref:
                variant['Inheritance_model']['X'] = False
                variant['Inheritance_model']['X_dn'] = False
            elif individual_genotype.has_variant:
                check_parents('X', individual, variant, family)
        # Else if phenotype is unknown we can not say anything about the model

def check_dominant(variant, family):
    """Check if the variant follows the dominant pattern in this family."""
    for individual in family.individuals: 
        # Check in all individuals what genotypes that are in the trio based of the individual picked.
        individual_genotype = variant['Genotypes'].get(individual.individual_id, genotype.Genotype())
        if individual.phenotype == 1:# The case where the individual is healthy
            if individual_genotype.has_variant:
                # If the individual is healthy and have a variation on one or both alleles it can not be dominant.
                variant['Inheritance_model']['AD'] = False
                variant['Inheritance_model']['AD_denovo'] = False
        elif individual.phenotype == 2:
            # The case when the individual is sick
            if individual_genotype.homo_ref:
                variant['Inheritance_model']['AD'] = False
                variant['Inheritance_model']['AD_denovo'] = False
            else: 
            # Now the ind is sick and have a variant ≠ ref, check parents for de novo
                check_parents('dominant', individual, variant, family)
            # Else if phenotype is unknown we can not say anything about the model

def check_recessive(variant, family):
    """Check if the variant follows the autosomal recessive pattern in this family."""
    for individual in family.individuals:
        individual_genotype = variant['Genotypes'].get(individual.individual_id, genotype.Genotype())
        # The case where the individual is healthy:
        if individual.phenotype == 1:
        # If the individual is healthy and homozygote alt the model is broken.
            if individual_genotype.homo_alt:
                variant['Inheritance_model']['AR_hom'] = False
                variant['Inheritance_model']['AR_hom_denovo'] = False
        # The case when the individual is sick:
        elif individual.phenotype == 2:
        # In the case of a sick individual it must be homozygote alternative for compound heterozygote to be true.
        # Also, we can not exclude the model if no call.
            if individual_genotype.homo_ref or individual_genotype.heterozygote:
                variant['Inheritance_model']['AR_hom'] = False
                variant['Inheritance_model']['AR_hom_denovo'] = False
            else:
            #Models are followed but we need to check the parents to see if de novo is followed or not.
                check_parents('recessive', individual, variant, family)
                
def check_parents(model, individual, variant, family):
    """Check if information in the parents can tell us if model is de novo or not. Model in ['recessive', 'compound', 'dominant']."""
    sex = individual.sex
    individual_genotype = variant['Genotypes'].get(individual.individual_id, genotype.Genotype())

    mother_id = individual.mother
    mother_genotype = variant['Genotypes'].get(mother_id, genotype.Genotype())
    mother_phenotype = family.get_phenotype(mother_id)

    father_id = individual.father
    father_genotype = variant['Genotypes'].get(father_id, genotype.Genotype())
    father_phenotype = family.get_phenotype(father_id)


    if model == 'recessive':
        # If any of the parents doesent exist de novo will be true as the model is specified
        if mother_id != '0' and father_id != '0':
        # If both parents have the variant or if one of the parents are homozygote alternative, the de novo model is NOT followed, otherwise de novo is true.
            if ((mother_genotype.homo_alt or father_genotype.homo_alt) or 
                (mother_genotype.has_variant and father_genotype.has_variant)):
                variant['Inheritance_model']['AR_hom_denovo'] = False
        if variant['Inheritance_model']['AR_hom_denovo']:# If de novo is true then the it is only de novo
            variant['Inheritance_model']['AR_hom'] = False
                
    elif model == 'dominant':
    # If one of the parents have the variant on any form the de novo model is NOT followed.
        if mother_genotype.has_variant or father_genotype.has_variant:
            variant['Inheritance_model']['AD_denovo'] = False
        if variant['Inheritance_model']['AD_denovo']:# If variant is ad de novo then it is not ad
            variant['Inheritance_model']['AD'] = False
            
    elif model == 'X':
        #If the individual is a male:
        if sex == 1:
        #If any of the parents have the variant it is not dn
            if mother_genotype.has_variant or father_genotype.has_variant:
                variant['Inheritance_model']['X_dn'] = False
        #If female 
        elif sex == 2:
            #If 
            if individual_genotype.homo_alt:
                if ((mother_genotype.homo_alt or father_genotype.homo_alt) 
                    or (mother_genotype.has_variant and father_genotype.has_variant)):
                    variant['Inheritance_model']['X_dn'] = False
            elif individual_genotype.heterozygote:
                if mother_genotype.has_variant or father_genotype.has_variant:
                    variant['Inheritance_model']['X_dn'] = False
        if variant['Inheritance_model']['X_dn']:
            variant['Inheritance_model']['X'] = False          
    

def main():
    pass


if __name__ == '__main__':
    main()

