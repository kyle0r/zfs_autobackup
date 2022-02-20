from basetest import *


class TestZfsCheck(unittest2.TestCase):

    def setUp(self):
        pass

    def test_blockhash(self):
        #make VERY sure this works correctly under all circumstances.

        # sha1 sums of files, (bs=4096)
        # da39a3ee5e6b4b0d3255bfef95601890afd80709  empty
        # 642027d63bb0afd7e0ba197f2c66ad03e3d70de1  partial
        # 3c0bf91170d873b8e327d3bafb6bc074580d11b7  whole
        # 2e863f1fcccd6642e4e28453eba10d2d3f74d798  whole2
        # 959e6b58078f0cfd2fb3d37e978fda51820473ff  whole_whole2
        # 309ffffba2e1977d12f3b7469971f30d28b94bd8  whole_whole2_partial


        self.assertEqual(
            list(block_hash("tests/data/empty", count=1)),
            []
        )

        self.assertEqual(
            list(block_hash("tests/data/partial", count=1)),
            [(0, "642027d63bb0afd7e0ba197f2c66ad03e3d70de1")]
        )

        self.assertEqual(
            list(block_hash("tests/data/whole", count=1)),
            [(0, "3c0bf91170d873b8e327d3bafb6bc074580d11b7")]
        )

        self.assertEqual(
            list(block_hash("tests/data/whole_whole2", count=1)),
            [
                (0, "3c0bf91170d873b8e327d3bafb6bc074580d11b7"),
                (1, "2e863f1fcccd6642e4e28453eba10d2d3f74d798")
            ]
        )

        self.assertEqual(
            list(block_hash("tests/data/whole_whole2_partial", count=1)),
            [
                (0, "3c0bf91170d873b8e327d3bafb6bc074580d11b7"), #whole
                (1, "2e863f1fcccd6642e4e28453eba10d2d3f74d798"), #whole2
                (2, "642027d63bb0afd7e0ba197f2c66ad03e3d70de1")  #partial
            ]
        )

        self.assertEqual(
            list(block_hash("tests/data/whole_whole2_partial", count=2)),
            [
                (0, "959e6b58078f0cfd2fb3d37e978fda51820473ff"), #whole_whole2
                (1, "642027d63bb0afd7e0ba197f2c66ad03e3d70de1")  #partial
            ]
        )

        self.assertEqual(
            list(block_hash("tests/data/whole_whole2_partial", count=10)),
            [
                (0, "309ffffba2e1977d12f3b7469971f30d28b94bd8"), #whole_whole2_partial
            ])


    def test_volume(self):
        prepare_zpools()

        shelltest("zfs create -V200M test_source1/vol")
        shelltest("zfs snapshot test_source1/vol@test")

        with OutputIO() as buf:
            with redirect_stdout(buf):
                self.assertFalse(ZfsCheck("test_source1/vol@test".split(" "),print_arguments=False).run())

            print(buf.getvalue())
            self.assertEqual("""0	2c2ceccb5ec5574f791d45b63c940cff20550f9a
1	2c2ceccb5ec5574f791d45b63c940cff20550f9a
""", buf.getvalue())


    def test_filesystem(self):
        prepare_zpools()

        shelltest("cp tests/data/whole /test_source1/testfile")
        shelltest("zfs snapshot test_source1@test")

        with OutputIO() as buf:
            with redirect_stdout(buf):
                self.assertFalse(ZfsCheck("test_source1@test".split(" "), print_arguments=False).run())

            print(buf.getvalue())
            self.assertEqual("""testfile	0	3c0bf91170d873b8e327d3bafb6bc074580d11b7
""", buf.getvalue())
