from invoke import task

COVERAGE_PARAMS = '--cov-config .coveragerc --cov-report html --cov-report term --cov=travel'

@task
def clean(ctx):
    '''Removes all the cache files'''
    ctx.run('find . -type d -name __pycache__ | xargs rm -rf')
    ctx.run('rm -rf htmlcov')
    ctx.run('rm -rf django_travel.egg-info')
    ctx.run('rm test-travel.db')


@task
def test(ctx):
    '''Run all tests'''
    ctx.run('py.test', pty=True)


@task
def test_cov(ctx):
    '''Runs unit tests with coverage'''
    ctx.run(
        'py.test {}'.format(COVERAGE_PARAMS),
        pty=True
    )

@task
def install(ctx):
    ctx.run('pip install -r requirements/base.txt')


@task
def devel(ctx):
    install(ctx)
    ctx.run('pip install -r requirements/devel.txt')
