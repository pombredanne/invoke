import os
import shutil

from invocations import docs
from invocations.testing import test
from invocations.packaging import vendorize, release

from invoke import ctask as task, run, Collection


@task(name='tree')
def doctree(ctx):
    ctx.run("tree -Ca -I \".git|*.pyc|*.swp|dist|*.egg-info|_static|_build\" docs")

@task
def vendorize_pexpect(ctx, version):
    target = 'invoke/vendor'
    package = 'pexpect'
    vendorize(
        distribution="pexpect-u",
        package=package,
        version=version,
        vendor_dir=target,
        license='LICENSE', # TODO: autodetect this in vendorize
    )
    # Nuke test dir inside package hrrgh
    shutil.rmtree(os.path.join(target, package, 'tests'))

docs = Collection.from_module(docs)
docs.add_task(doctree)
ns = Collection(test, vendorize, release, docs, vendorize_pexpect)
