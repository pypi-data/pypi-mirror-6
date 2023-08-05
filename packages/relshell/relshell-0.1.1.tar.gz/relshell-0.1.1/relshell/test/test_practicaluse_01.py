# -*- coding: utf-8 -*-
from nose.tools import *
import os
import tempfile
import re
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.shelloperator import ShellOperator


n_tmpfile = 0


def setup():
    global n_tmpfile
    n_tmpfile = _get_num_tmpfile()


def teardown():
    global n_tmpfile
    eq_(_get_num_tmpfile(), n_tmpfile, 'Number of relshell tmpfile is not changed during test')


def _get_num_tmpfile():
    return len([tmp for tmp in os.listdir(tempfile.gettempdir()) if tmp.startswith('relshell-') and tmp.endswith('.batch')])


def _simple_recdef():
    return RecordDef([{'name': 'text', 'type': 'STRING'}])


def _simple_int_recdef():
    return RecordDef([{'name': 'age', 'type': 'INT'}])


def _diff_out_recdef():
    return RecordDef([
        {'name': 'position',
         'type': 'STRING',
        },
        {'name': 'diff',
         'type': 'STRING',
        },
    ])


def _awk_in_recdef():
    return RecordDef([
        {'name': 'person',
         'type': 'STRING',
        },
        {'name': 'age',
         'type': 'INT',
        },
    ])


def _create_batch():
    rdef = _simple_recdef()
    return Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4'),
    ))


def _create_batch_diff_in():
    rdef = _simple_recdef()
    return Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2xx'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4yy'),
    ))


def _create_batch_awk_in():
    rdef = _awk_in_recdef()
    return Batch((
        Record(rdef, 'tanaka', 48),
        Record(rdef, 'suzuki', 25),
        Record(rdef, 'satoh',  32),
    ))


def test_output_2in_1out():
    batch0 = _create_batch()
    batch1 = _create_batch_diff_in()

    op = ShellOperator(
        'diff IN_BATCH0 IN_BATCH1 > OUT_BATCH',
        out_record_def=_diff_out_recdef(),
        success_exitcodes=(0, 1),
        out_col_patterns={
            'position': re.compile(r'''
                # diff position
                (
                    \d (,\d)? [acd] \d (,\d)?
                )
            ''', re.VERBOSE | re.MULTILINE),

            'diff': re.compile(r'''
                # diff content
                (
                    (^[<>] .*?$\n)+
                    (
                        ^---$\n
                        (^> .*?$\n)*
                    )?
                )
            ''', re.VERBOSE | re.MULTILINE)
        }
    )
    out_batch = op.run(in_batches=(batch0, batch1))
    eq_(out_batch,
        Batch((
            Record(
                _diff_out_recdef(),
                '2c2',
'''< test2
---
> test2xx
''',
            ),

            Record(
                _diff_out_recdef(),
                '4c4',
'''< test4
---
> test4yy
''',
            ),
        ))
    )


def test_output_2col_in():
    op = ShellOperator(
        'awk \'{print "age:" $2}\' < IN_BATCH0 > OUT_BATCH',
        out_record_def   = _simple_recdef(),
        out_col_patterns = {'text': re.compile(r'^.+$', re.MULTILINE)},
    )
    batch_person_age = _create_batch_awk_in()
    batch_age        = op.run(in_batches=(batch_person_age, ))
    eq_(batch_age,
        Batch((
            Record(_simple_recdef(), 'age:48'),
            Record(_simple_recdef(), 'age:25'),
            Record(_simple_recdef(), 'age:32'),
        ))
    )


def test_awk_perl():
    op_awk = ShellOperator(
        'awk \'{print $2}\' < IN_BATCH0 > OUT_BATCH',
        out_record_def   = _simple_int_recdef(),
        out_col_patterns = {'age': re.compile(r'^.+$', re.MULTILINE)},
    )
    batch_person_age = _create_batch_awk_in()
    batch_age        = op_awk.run(in_batches=(batch_person_age, ))

    op_perl = ShellOperator(
        'perl -e \'my $sum = 0; while(<STDIN>) { $sum += $_ } print $sum;\' < IN_BATCH0 > OUT_BATCH',
        out_record_def   = _simple_int_recdef(),
        out_col_patterns = {'age': re.compile(r'^.+$', re.MULTILINE)},
    )
    batch_age_sum = op_perl.run(in_batches=(batch_age, ))
    eq_(batch_age_sum,
        Batch((
            Record(_simple_int_recdef(), 48 + 25 + 32),
        )))
