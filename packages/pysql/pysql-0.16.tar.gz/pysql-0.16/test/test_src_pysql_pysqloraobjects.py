import unittest

class TestOraObject(unittest.TestCase):
    def test_getCopy(self):
        assert False # TODO: implement your test here

    def test_getDDL(self):
        assert False # TODO: implement your test here

    def test_getFullName(self):
        assert False # TODO: implement your test here

    def test_getName(self):
        assert False # TODO: implement your test here

    def test_getOwner(self):
        assert False # TODO: implement your test here

    def test_getType(self):
        assert False # TODO: implement your test here

    def test_guessInfos(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

    def test_setName(self):
        assert False # TODO: implement your test here

    def test_setOwner(self):
        assert False # TODO: implement your test here

    def test_setType(self):
        assert False # TODO: implement your test here

class TestOraSegment(unittest.TestCase):
    def test_getTablespace(self):
        assert False # TODO: implement your test here

class TestOraTabular(unittest.TestCase):
    def test_getComment(self):
        assert False # TODO: implement your test here

    def test_getNumberOfColumns(self):
        assert False # TODO: implement your test here

    def test_getRowCount(self):
        assert False # TODO: implement your test here

    def test_getTableColumns(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraDatafile(unittest.TestCase):
    def test_getAllocatedBytes(self):
        assert False # TODO: implement your test here

    def test_getFreeBytes(self):
        assert False # TODO: implement your test here

    def test_getTablespace(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraDBLink(unittest.TestCase):
    def test_getRemoteHost(self):
        assert False # TODO: implement your test here

    def test_getRemoteUser(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraDirectory(unittest.TestCase):
    def test_getPath(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraIndex(unittest.TestCase):
    def test_getIndexedColumns(self):
        assert False # TODO: implement your test here

    def test_getProperties(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraMaterializedView(unittest.TestCase):
    def test_getSQL(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraStoredObject(unittest.TestCase):
    def test_getSQL(self):
        assert False # TODO: implement your test here

    def test_getSQLAsList(self):
        assert False # TODO: implement your test here

    def test_setSQL(self):
        assert False # TODO: implement your test here

class TestOraProcedure(unittest.TestCase):
    def test_getSource(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraFunction(unittest.TestCase):
    def test_getSource(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraPackage(unittest.TestCase):
    def test_getProcedures(self):
        assert False # TODO: implement your test here

    def test_getSource(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraPackageBody(unittest.TestCase):
    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraSequence(unittest.TestCase):
    def test_getLast(self):
        assert False # TODO: implement your test here

    def test_getMax(self):
        assert False # TODO: implement your test here

    def test_getMin(self):
        assert False # TODO: implement your test here

    def test_getStep(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraSynonym(unittest.TestCase):
    def test_getTarget(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraTable(unittest.TestCase):
    def test_getIndexedColumns(self):
        assert False # TODO: implement your test here

    def test_getPrimaryKeys(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraTablespace(unittest.TestCase):
    def test_getAllocatedBytes(self):
        assert False # TODO: implement your test here

    def test_getDatafiles(self):
        assert False # TODO: implement your test here

    def test_getFreeBytes(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

    def test_updateDatafileList(self):
        assert False # TODO: implement your test here

class TestOraTrigger(unittest.TestCase):
    def test_getBody(self):
        assert False # TODO: implement your test here

    def test_getEvent(self):
        assert False # TODO: implement your test here

    def test_getStatus(self):
        assert False # TODO: implement your test here

    def test_getTable(self):
        assert False # TODO: implement your test here

    def test_getTriggerType(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

    def test_updateTable(self):
        assert False # TODO: implement your test here

class TestOraUser(unittest.TestCase):
    def test_getDefaultTablespace(self):
        assert False # TODO: implement your test here

    def test_getTempTablespace(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

class TestOraView(unittest.TestCase):
    def test_getSQL(self):
        assert False # TODO: implement your test here

    def test_object_initialization(self):
        assert False # TODO: implement your test here

    def test_setSQL(self):
        assert False # TODO: implement your test here

if __name__ == '__main__':
    unittest.main()
