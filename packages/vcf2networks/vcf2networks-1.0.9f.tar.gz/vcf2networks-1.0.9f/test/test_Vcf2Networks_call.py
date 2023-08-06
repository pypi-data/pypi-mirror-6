#!/usr/bin/env python
"""
Test multiple call to VCF2Networks, using different parameters, and checking if the programs runs correctly or not.

"""
import subprocess
import unittest
import nose

good_examples = {
    'example1':
        # basic call, including all the default options. 
        'python src/vcf2networks.py  -g data/vcf_filtered/MOGS.recode.vcf -c params/default.yaml -i data/individuals/individuals_annotations.txt',

    'example2':
        # using a different window and distance definition
        'python src/vcf2networks.py  -g data/vcf_filtered/MOGS.recode.vcf -c params/default.yaml     -w 8 -d 2 ',

    'example3': 
        # using PHENOTYPE1 as phenotype
        'python src/vcf2networks.py  -g data/vcf_filtered/MOGS.recode.vcf -c params/default.yaml     -w 12 -p PHENOTYPE1',

    'example4': 
        # using PHENOTYPE1, and subsampling
        'python src/vcf2networks.py  -g data/vcf_filtered/MOGS.recode.vcf -c params/default.yaml     -w 12 -p PHENOTYPE1 --sample 100',

    'example5':
        # testing a compressed file
        'python src/vcf2networks.py  -g data/vcf_filtered/CCR5.recode.vcf.gz -c params/default.yaml  -w 11 -p subpop',

    'example6':
        # subsampling multiple times
        'python src/vcf2networks.py  -g data/vcf_filtered/MOGS.recode.vcf -c params/default.yaml     -w 10 --sample 100 -r 2',

#    'example_fromotherfolder':
#        # calling the script from another folder
#        '(cd ..; python vcf2networks/src/vcf2networks.py  -g vcf2networks/data/vcf_filtered/MOGS.recode.vcf  -c vcf2networks/params/default.yaml -w 11 -s 3 --individuals 100 -p PHENOTYPE1 --individuals_file vcf2networks/data/individuals/individuals_annotations.txt )'
        }


def test_goodcalls():
    for (example_id, example_command) in good_examples.items():
        yield check_goodexample, example_command

def check_goodexample(example_command):
#    print example_command.split()
    print example_command
    subprocess.check_output(example_command.split())

def test_goodcalls_fromotherfolder():
    subprocess.check_output('python vcf2networks/src/vcf2networks.py  -g vcf2networks/data/vcf_filtered/MOGS.recode.vcf  -c vcf2networks/params/default.yaml -w 11 -s 3 --individuals 100 -p PHENOTYPE1 --individuals_file vcf2networks/data/individuals/individuals_annotations.txt'.split(), cwd='..')



#
##class VCFNotSpecified(VCFExistsButInvalid):


bad_examples = {
    'vcffile_exists_but_invalid':
        {
            'cmd': 'python src/vcf2networks.py  -c params/default.yaml  --vcf README.rst   -w 8 -d 2',
            'expected_error': 'Wrong number of columns in the VCF file.'
        },
            
            

    'vcffile_not_specified':
        {
            'cmd': 'python src/vcf2networks.py  -c params/default.yaml  -w 8 -d 2',
            'expected_error' : 'no VCF file provided',
        },

    'vcffile_not_exists':
        {
            'cmd': 'python src/vcf2networks.py  -c params/default.yaml  --vcf sda   -w 8 -d 2',
            'expected_error': 'I can not parse the VCF file provided (sda).'
        },

    'invalid_individuals_file':
        {
            'cmd': 'python src/vcf2networks.py  -c params/default.yaml  --vcf data/vcf_filtered/MOGS.recode.vcf --individuals dasd -w 8 -d 2',
            'expected_error': 'I can not parse the VCF file provided (sda).'
        },
    }

def test_badcalls():
    for (example_id, example_details) in bad_examples.items():
        yield check_badexample, example_details
#
def check_badexample(example_details):
#    print example_details.split()
    print example_details
    with nose.tools.assert_raises(subprocess.CalledProcessError):
        output = subprocess.check_output(example_details['cmd'].split(), stderr=subprocess.STDOUT)
        nose.tools.assert_contains(example_details['expected_error'], output)

#    except:
##        pass












if __name__ == '__main__':
    pass

