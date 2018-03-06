from invoke import task

COVERAGE_PARAMS = '--cov-config .coveragerc --cov-report html --cov-report term --cov=travel'

@task
def clean(ctx):
    '''Removes all the cache files'''
    ctx.run('find . -type d -name __pycache__ | xargs rm -rf')
    ctx.run('rm -rf htmlcov django_travel.egg-info .cache test-travel.db .coverage')


@task
def test(ctx, verbose=False):
    '''Run all tests'''
    ctx.run('py.test{}'.format(' -vv' if verbose else '', pty=True))


@task
def test_cov(ctx):
    '''Runs unit tests with coverage'''
    ctx.run(
        'py.test {} && open htmlcov/index.html'.format(COVERAGE_PARAMS),
        pty=True
    )


@task
def install(ctx):
    ctx.run('pip install -r requirements/base.txt')


@task
def devel(ctx):
    install(ctx)
    ctx.run('pip install -r requirements/devel.txt')
