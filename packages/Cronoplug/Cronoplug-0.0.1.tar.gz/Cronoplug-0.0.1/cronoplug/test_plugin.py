from nose.tools import *

from cronoplug.plugin import Plugin, from_fs

import io
import zipfile

import tempfile

def test_base():
    bio = io.BytesIO()
    with Plugin(bio, "Test Plugin") as plg:
        plg.add_file(name = 'main.lua',
                     content = b'I am covered in bees.')
    zp = zipfile.ZipFile(bio, 'r')
    with zp.open('main.lua') as f:
        content = f.read()
        assert content == b'I am covered in bees.'

def test_info():
    bio = io.BytesIO()
    with Plugin(bio, "Test Plugin") as plg:
        pass
    zp = zipfile.ZipFile(bio, 'r')
    info = zp.getinfo('main.lua')
    assert info.comment == b"Test Plugin"

def test_source():
    bio = io.BytesIO()
    src = io.BytesIO(b"I'm on a boat")
    with Plugin(bio, "Test Plugin", lambda f: src) as plg:
        plg.import_file('boat.txt')
    zp = zipfile.ZipFile(bio, 'r')
    with zp.open('boat.txt') as f:
        content = f.read()
        assert content == b"I'm on a boat"

@raises(KeyError)
def test_source_error():
    bio = io.BytesIO()
    with Plugin(bio, "Test Plugin", lambda f: None) as plg:
        plg.import_file('pony.txt')

def test_import_from_mfest():
    bio = io.BytesIO()
    manifest = """
files:
  - bees.txt
"""
    manifestsrc = io.BytesIO(manifest.encode('utf-8'))
    beessrc = io.BytesIO("Covered in bees.".encode('utf-8'))
    def get_file(x):
        return {"manifest.yaml": manifestsrc,
                "bees.txt": beessrc}.get(x, None)
    with Plugin(bio, "Test Plugin", get_file) as plg:
        plg.import_from_manifest()
    zp = zipfile.ZipFile(bio, 'r')
    with zp.open('bees.txt') as f:
        content = f.read()
        assert content == "Covered in bees.".encode('utf-8')

@raises(KeyError)
def test_import_no_mfest():
    bio = io.BytesIO()
    with Plugin(bio, "Test Plugin", lambda x: None) as plg:
        plg.import_from_manifest()

@raises(ValueError)
def test_import_bad_mfest():
    bio = io.BytesIO()
    manifest = "["
    manifestsrc = io.BytesIO(manifest.encode('utf-8'))
    with Plugin(bio, "Test Plugin", lambda x: manifestsrc) as plg:
        plg.import_from_manifest()

def test_import_fs():
    manifestcontents = """
files:
  - eyes.txt
"""
    with tempfile.TemporaryDirectory() as dpath:
        with open("{}/manifest.yaml".format(dpath), 'w') as f:
            f.write(manifestcontents)
        with open("{}/eyes.txt".format(dpath), 'w') as f:
            f.write("Death gravy.")
        bio = io.BytesIO()
        with Plugin(bio, "Test Plugin", from_fs(dpath)) as plg:
            plg.import_from_manifest()
        zp = zipfile.ZipFile(bio, 'r')
        with zp.open('eyes.txt') as f:
            content = f.read()
            assert content == "Death gravy.".encode('utf-8')


