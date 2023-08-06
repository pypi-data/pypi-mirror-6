#!/usr/bin/env python
# encoding: utf-8
"""
Mip_Family_Analysis.py

Script for annotating which genetic models that are followed for variants in the mip pipeline.

Created by Måns Magnusson on 2013-01-31.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import argparse
import shelve
from multiprocessing import Manager, JoinableQueue, cpu_count, Lock
from tempfile import NamedTemporaryFile

from datetime import datetime
import pkg_resources

from pprint import pprint as pp

from ped_parser import parser
from Mip_Family_Analysis.Variants import variant_parser
from Mip_Family_Analysis.Models import genetic_models, score_variants
from Mip_Family_Analysis.Utils import variant_consumer, variant_sorter, header_parser, variant_printer

def get_family(args):
    """Return the family"""
    family_type = 'cmms'
    family_file = args.family_file[0]
    
    my_family_parser = parser.FamilyParser(family_file, family_type)
    # Stupid thing but for now when we only look at one family
    return my_family_parser.families.popitem()[1]

def get_header(variant_file):
    """Return a fixed header parser"""
    head = header_parser.HeaderParser(variant_file)
    return head

def add_cmms_metadata(header_object):
    """Add the necessary metadata and header columns that this software operates on."""
    header_object.add_metadata('Individual_rank_score', data_type='Integer', 
        description='This is the correct rank score if the variant only follows the AR_comp model.', 
        dbname='Individual Rank Score'
    )
    header_object.add_metadata('Rank_score', data_type='Integer', 
        description='Rank score of disease casuing potential. Higher the more likely disease casuing.', 
        dbname='Rank Score'
    )
    header_object.add_metadata('Compounds', data_type='String', 
        description='This is the correct rank score if the variant only follows the AR_comp model.', 
        dbname='Individual Rank Score'
    )
    header_object.add_metadata('Inheritance_model', data_type='String', 
        description='Variant inheritance pattern.', 
        dbname='Inheritance Model'
    )
    
    header_object.add_header('Inheritance_model')
    header_object.add_header('Individual_rank_score')
    header_object.add_header('Compounds')
    header_object.add_header('Rank_score')
    return

def print_headers(args, header_object):
    """Print the headers to a results file."""
    lines_to_print = header_object.get_headers_for_print()
    if args.outfile[0]:
        with open(args.outfile[0], 'w') as f: 
            for line in lines_to_print:
                f.write(line + '\n')
    elif not args.silent:
        for line in lines_to_print:
            print line
    return

def main():
    parser = argparse.ArgumentParser(description="Parse different kind of ped files.")
    
    parser.add_argument('family_file', 
        type=str, nargs=1,
        help='A pedigree file. Default is cmms format.'
    )
    parser.add_argument('variant_file', 
        type=str, nargs=1, 
        help='A variant file.Default is vcf format'
    )
    parser.add_argument('-o', '--outfile', 
        type=str, nargs=1, default=[None], 
        help='Specify the path to output, if no file specified the output will be printed to screen.'
    )
    parser.add_argument('--version', 
        action="version", version=pkg_resources.require("Mip_Family_Analysis")[0].version
    )
    parser.add_argument('-v', '--verbose', 
        action="store_true", 
        help='Increase output verbosity.'
    )
    parser.add_argument('-s', '--silent', 
        action="store_true", 
        help='Do not print the variants.'
    )
    parser.add_argument('-ga', '--gene_annotation', 
        type=str, choices=['Ensembl', 'HGNC'], nargs=1, default=['HGNC'], 
        help='What gene annotation should be used, HGNC or Ensembl.'
    )
    parser.add_argument('-pos', '--position', 
        action="store_true", 
        help='If output should be sorted by position. Default is sorted on rank score'
    )
    parser.add_argument('-tres', '--treshold', 
        type=int, nargs=1, 
        help='Specify the lowest rank score to be outputted.'
    )
    args = parser.parse_args()
    
    # Print program version to std err:
    
    print >> sys.stderr, 'Version:', pkg_resources.require("Mip_Family_Analysis")[0].version
        
    # If gene annotation is manually given:
    gene_annotation = args.gene_annotation[0]
    
    start_time_analysis = datetime.now()
    
    # Start by parsing at the pedigree file:
    my_family = get_family(args)
    preferred_models = my_family.models_of_inheritance
        
    # Check the variants:
    
    
    var_file = args.variant_file[0]
    file_name, file_extension = os.path.splitext(var_file)
    
    # Take care of the headers from the variant file:
    head = get_header(var_file)
    
    add_cmms_metadata(head)
    
    # The variant queue is just a queue with splitted variant lines:
    variant_queue = JoinableQueue()
    # The consumers will put their results in the results queue
    results = Manager().Queue()
    
    # Create a temporary file for the variants:
    
    temp_file = NamedTemporaryFile(delete=False)
    
    if args.verbose:
        print 'Temp files:' ,temp_file.name
    
    num_model_checkers = (cpu_count()*2-1)
    
        
    model_checkers = [variant_consumer.VariantConsumer(variant_queue, results, my_family, 
                     args.verbose) for i in xrange(num_model_checkers)]
    
    for w in model_checkers:
        w.start()
    
    var_printer = variant_printer.VariantPrinter(results, temp_file, head, args.verbose)
    var_printer.start()
    
    
    if args.verbose:
        print 'Start parsing the variants ...'
        print ''
        start_time_variant_parsing = datetime.now()    
    
    
    var_parser = variant_parser.VariantFileParser(var_file, variant_queue, head, args.verbose)
    var_parser.parse()
    
    if args.verbose:
        print 'Variants done!. Time to parse variants: ', (datetime.now() - start_time_variant_parsing)
        print ''
            
    for i in xrange(num_model_checkers):
        variant_queue.put(None)
    
    variant_queue.join()
    results.put(None)
    var_printer.join()
    
    if args.verbose:
        print 'Models checked!'
        print 'Start sorting the variants:'
        print ''
        start_time_variant_sorting = datetime.now()
        
    print_headers(args, head)
        
    var_sorter = variant_sorter.FileSort(temp_file, outFile=args.outfile[0], silent=args.silent)
    var_sorter.sort()
    
    os.remove(temp_file.name)
    
    if args.verbose:
        print 'Variants sorted!. Time to sort variants: ', (datetime.now() - start_time_variant_sorting)
        print ''
        print 'Total time for analysis:' , (datetime.now() - start_time_analysis)
    
    # # if not args.outfile:
    # #     if not args.silent:
    # #         with open(results_file, 'r') as f:
    # #             for line in f:
    # #                 print line.rstrip()
    # #     os.remove(results_file)
    


if __name__ == '__main__':
    main()

