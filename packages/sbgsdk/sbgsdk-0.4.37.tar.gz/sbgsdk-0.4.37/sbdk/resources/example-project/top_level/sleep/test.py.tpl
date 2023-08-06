from {project.name}.sleep.wrapper import SleepWrapper


def test_sleep_wrapper():
    params = {{'a': 'some.file'}}
    args = {{'seconds': 2}}
    assert SleepWrapper(params, args).test().a.endswith('some.file')
