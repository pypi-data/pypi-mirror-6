from sbgsdk.test import assert_files_identical
from sbgsdk.tests.common import cleanup
from sbgsdk.tests.test_tools.generator import generator
from sbgsdk.tests.test_wrappers import BlueComparator





@cleanup
def test_comparator_sample():
    w = BlueComparator(
        inputs={'inputA': ['hex0.txt', 'hex1.txt', 'hex2.txt', 'hex3.txt']},
        params={'group_by': 'sample'},
    )

    w.inputs.inputA[0].meta.file_type = 'text'
    w.inputs.inputA[0].meta.sample = 'S1'
    w.inputs.inputA[1].meta.file_type = 'text'
    w.inputs.inputA[1].meta.sample = 'S1'
    w.inputs.inputA[2].meta.file_type = 'text'
    w.inputs.inputA[2].meta.sample = 'S2'
    w.inputs.inputA[3].meta.file_type = 'text'
    w.inputs.inputA[3].meta.sample = 'S2'
    w.inputs._save_meta()

    count = 1000
    generator.generate('hex0.txt', count, 'same', 15)
    generator.generate('hex1.txt', count, 'same', 15)
    generator.generate('hex2.txt', count, 'same', 42)
    generator.generate('hex3.txt', count, 'same', 42)
    w.test()

    s1 = filter(lambda x: x.meta.sample == 'S1', w.outputs.output)[0]
    s2 = filter(lambda x: x.meta.sample == 'S2', w.outputs.output)[0]
    assert_files_identical(s1, 'hex0.txt')
    assert_files_identical(s2, 'hex2.txt')


@cleanup
def test_comparator_platform_unit():
    w = BlueComparator(
        inputs={'inputA': ['hex0.txt', 'hex1.txt', 'hex2.txt', 'hex3.txt']},
        params={'group_by': 'platform_unit'},
    )

    w.inputs.inputA[0].meta.file_type = 'text'
    w.inputs.inputA[0].meta.sample = 'S1'
    w.inputs.inputA[0].meta.platform_unit = 'PU1'
    w.inputs.inputA[1].meta.file_type = 'text'
    w.inputs.inputA[1].meta.sample = 'S1'
    w.inputs.inputA[1].meta.platform_unit = 'PU1'
    w.inputs.inputA[2].meta.file_type = 'text'
    w.inputs.inputA[2].meta.sample = 'S1'
    w.inputs.inputA[2].meta.platform_unit = 'PU2'
    w.inputs.inputA[3].meta.file_type = 'text'
    w.inputs.inputA[3].meta.sample = 'S1'
    w.inputs.inputA[3].meta.platform_unit = 'PU2'
    w.inputs._save_meta()

    count = 1000
    generator.generate('hex0.txt', count, 'same', 15)
    generator.generate('hex1.txt', count, 'same', 15)
    generator.generate('hex2.txt', count, 'same', 42)
    generator.generate('hex3.txt', count, 'same', 42)
    w.test()

    s1 = filter(lambda x: x.meta.platform_unit == 'PU1', w.outputs.output)[0]
    s2 = filter(lambda x: x.meta.platform_unit == 'PU2', w.outputs.output)[0]
    assert_files_identical(s1, 'hex0.txt')
    assert_files_identical(s2, 'hex2.txt')


@cleanup
def test_comparator_no_group():
    w = BlueComparator(
        inputs={'inputA': ['hex0.txt', 'hex1.txt']},
        params={'group_by': None},
    )

    w.inputs.inputA[0].meta.file_type = 'text'
    w.inputs.inputA[0].meta.sample = 'S1'
    w.inputs.inputA[0].meta.platform_unit = 'PU1'
    w.inputs.inputA[1].meta.file_type = 'text'
    w.inputs.inputA[1].meta.sample = 'S1'
    w.inputs.inputA[1].meta.platform_unit = 'PU1'
    w.inputs._save_meta()

    count = 1000
    generator.generate('hex0.txt', count, 'same', 15)
    generator.generate('hex1.txt', count, 'same', 15)
    w.test()

    assert_files_identical(w.outputs.output[0], 'hex0.txt')
