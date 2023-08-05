#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(c) 2014 Brant Faircloth || http://faircloth-lab.org/
All rights reserved.

This code is distributed under a 3-clause BSD license. Please see
LICENSE.txt for more information.

Created on 31 January 2014 12:36 PST (-0800)
"""


import os
import glob
import hashlib

import pdb


class TestGetTruHtReads:
    def test_enough_reads(self, fake_truht_reads):
        assert len(fake_truht_reads) == 2

    def test_correct_file_names(self, fake_truht_reads):
        expected_r1 = set([
            'fake-truht_S1_L001_R1_001.fastq.gz',
            'fake-truht_S2_L001_R1_001.fastq.gz'
        ])
        expected_r2 = set([
            'fake-truht_S1_L001_R2_001.fastq.gz',
            'fake-truht_S2_L001_R2_001.fastq.gz'
        ])
        observed_r1 = []
        observed_r2 = []
        for read in fake_truht_reads:
            observed_r1.extend([os.path.basename(r) for r in read.r1])
            observed_r2.extend([os.path.basename(r) for r in read.r2])
        assert set(observed_r1) == expected_r1
        assert set(observed_r2) == expected_r2


class TestS1SequenceData:
    def test_home_dir(self, s1):
        assert s1.homedir == os.path.join(
            os.path.dirname(__file__),
            "truht/clean/fake-truht1"
            )

    def test_s1_i5(self, s1):
        assert s1.i5 == 'i5-06_F'

    def test_s1_i5a(self, s1):
        assert s1.i5a == 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGTTGGCTGTGTAGATCTCGGTGGTCGCCGTATCATT'

    def test_s1_i5s(self, s1):
        assert s1.i5s == 'AGTTGGCT'

    def test_s1_i5s_revcomp(self, s1):
        assert s1.i5s_revcomp is True

    def test_s1_i7(self, s1):
        assert s1.i7 == 'i7-09_11'

    def test_s1_i7a(self, s1):
        assert s1.i7a == 'GATCGGAAGAGCACACGTCTGAACTCCAGTCACATATGCGCATCTCGTATGCCGTCTTCTGCTTG'

    def test_s1_i7s(self, s1):
        assert s1.i7s == 'ATATGCGC'

    def test_s1_r1_pattern(self, s1):
        assert s1.r1_pattern == """{}_(?:.*)_(R1|READ1|Read1|read1)_\\d+.fastq(?:.gz)*"""

    def test_s1_r2_pattern(self, s1):
        assert s1.r2_pattern == """{}_(?:.*)_(R2|READ2|Read2|read2)_\\d+.fastq(?:.gz)*"""

    def test_s1_se(self, s1):
        assert s1.se is False

    def test_s1_start_name(self, s1):
        assert s1.start_name == 'fake-truht_S1'

    def test_s1_end_name(self, s1):
        assert s1.end_name == 'fake-truht1'


class TestS2SequenceData:
    def test_home_dir(self, s2):
        assert s2.homedir == os.path.join(
            os.path.dirname(__file__),
            "truht/clean/fake-truht2"
            )

    def test_s2_i5(self, s2):
        assert s2.i5 == 'i5-06_F'

    def test_s2_i5a(self, s2):
        assert s2.i5a == 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGTTGGCTGTGTAGATCTCGGTGGTCGCCGTATCATT'

    def test_s2_i5s(self, s2):
        assert s2.i5s == 'AGTTGGCT'

    def test_s2_i5s_revcomp(self, s2):
        assert s2.i5s_revcomp is True

    def test_s2_i7(self, s2):
        assert s2.i7 == 'i7-09_08'

    def test_s2_i7a(self, s2):
        assert s2.i7a == 'GATCGGAAGAGCACACGTCTGAACTCCAGTCACCGTAGGTTATCTCGTATGCCGTCTTCTGCTTG'

    def test_s2_i7s(self, s2):
        assert s2.i7s == 'CGTAGGTT'

    def test_s2_r1_pattern(self, s2):
        assert s2.r1_pattern == """{}_(?:.*)_(R1|READ1|Read1|read1)_\\d+.fastq(?:.gz)*"""

    def test_s2_r2_pattern(self, s2):
        assert s2.r2_pattern == """{}_(?:.*)_(R2|READ2|Read2|read2)_\\d+.fastq(?:.gz)*"""

    def test_s2_se(self, s2):
        assert s2.se is False

    def test_s2_start_name(self, s2):
        assert s2.start_name == 'fake-truht_S2'

    def test_s2_end_name(self, s2):
        assert s2.end_name == 'fake-truht2'


class TestReadTrimmingResults:
    def check_read_files(self, fake_truht_args, hashes, dir):
        files = glob.glob(os.path.join(
            fake_truht_args.output,
            dir,
            "split-adapter-quality-trimmed",
            "*.fastq.gz"
        ))
        for file in files:
            md5 = hashlib.md5(open(file, 'rb').read()).hexdigest()
            print file
            assert md5 == hashes[os.path.basename(file)]

    def test_1_read_trimming(self, fake_truht_args):
        from illumiprocessor.main import main
        main(fake_truht_args)
        fake_truht1 = {
            'adapters.fasta': '5868b3e17fc058bd54cb2f4d8445e289',
            'fake-truht1-READ-singleton.fastq.gz': '9c01c7ea1c5c87be1e1df4eb9ed91372',
            'fake-truht1-READ1.fastq.gz': 'dadf96e04afc519f0e375981b369b925',
            'fake-truht1-READ2.fastq.gz': '1ae68e11567670040c2d48dc5d96d9f7',
        }
        self.check_read_files(fake_truht_args, fake_truht1, "fake-truht1")
        fake_truht2 = {
            'adapters.fasta': '1d5a8f37a1bf503743faeaf0f4263394',
            'fake-truht2-READ-singleton.fastq.gz': 'a02633175b2df700a8c8dc1a48ab67cc',
            'fake-truht2-READ1.fastq.gz': 'e513950c3d7766d04457e67405004ac4',
            'fake-truht2-READ2.fastq.gz': '1e1080a9c3bffb6e308dee1e46c5f2aa'
        }
        self.check_read_files(fake_truht_args, fake_truht2, "fake-truht2")

    def test_2_dir_structure(self, fake_truht_args):
        for dir in ["fake-truht1", "fake-truht2"]:
            dir_list = os.listdir(os.path.join(fake_truht_args.output, dir))
            assert set(dir_list) == set([
                'adapters.fasta',
                'raw-reads',
                'split-adapter-quality-trimmed',
                'stats'
            ])
