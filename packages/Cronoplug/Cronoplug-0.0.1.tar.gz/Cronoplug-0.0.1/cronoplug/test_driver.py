import cronoplug.driver as drv

import tempfile
import zipfile
import os

def test_argparse():
    generator_called = 0
    def fake_generator(srcdir, dstfile, plugin_name):
        nonlocal generator_called
        assert srcdir == "ponygravity"
        assert dstfile == "death star"
        assert plugin_name == "Pony Mann"
        generator_called += 1
    drv.cronoplug(["ponygravity", "death star", "-n", "Pony Mann"],
                  generate = fake_generator)
    assert generator_called == 1

def test_argparse_longhand():
    generator_called = 0
    def fake_generator(srcdir, dstfile, plugin_name):
        nonlocal generator_called
        assert srcdir == "ponygravity"
        assert dstfile == "death star"
        assert plugin_name == "Pony Mann"
        generator_called += 1
    drv.cronoplug(["ponygravity", "death star", "--name", "Pony Mann"],
                  generate = fake_generator)
    assert generator_called == 1

def test_argparse_implicit_name():
    generator_called = 0
    def fake_generator(srcdir, dstfile, plugin_name):
        nonlocal generator_called
        assert srcdir == "ponygravity"
        assert dstfile == "death star"
        assert plugin_name == "ponygravity"
        generator_called += 1
    drv.cronoplug(["ponygravity", "death star"],
                  generate = fake_generator)
    assert generator_called == 1

def test_generate():
    with tempfile.TemporaryDirectory() as tdir:
        with open('{}/manifest.yaml'.format(tdir), 'w') as f:
            f.write("files:\n  - bees.txt\n")
        with open('{}/bees.txt'.format(tdir), 'wb') as f:
            f.write("Bees.".encode('utf-8'))
        (tfile, tfilename) = tempfile.mkstemp()
        os.close(tfile)
        try:
            drv.generate_plugin(tdir, tfilename, "Eye Bees")
            with open(tfilename, 'rb') as tfile:
                zp = zipfile.ZipFile(tfile, 'r')
                with zp.open('bees.txt') as f:
                    content = f.read()
                    assert content == 'Bees.'.encode('utf-8')
        finally:
            os.unlink(tfilename)

