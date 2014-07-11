
import sqlite3

from unittest import TestCase
from unittest.mock import Mock, MagicMock
from logging import info, warning, error

class TestEveDB(TestCase):

	def test_LoadBlueprint(self):
		cursor = Mock()
		cursor.fetchall = Mock(return_value = [(34, 2730), (35, 214), (36, 303), (37, 4), (38, 2), (39, 2)])
		cursor.fetchone = Mock(return_value = (939, 592, 'Navitas Blueprint'))
		bp = LoadBlueprint(cursor, 939, None)
		self.assertEqual(len(bp.GetOutputs()), 1)
		self.assertEqual(len(bp.GetInputs()), 6)

class BluePrint:
	def __init__(self, aId, aName, aGroup, aInputs, aOutput):
		self.schemaId = aId
		self.name = aName
		self.inputs = aInputs
		self.output = aOutput
		self.group = aGroup

	def GetOutputs(self):
		return [self.output]

	def GetInputs(self):
		return self.inputs

	def GetName(self):
		return self.name

	def GetChild(self, row):
		return None

	def GetChildCount(self):
		return 0

	def GetIndexOfChild(self, aChild):
		return 0

	def GetParent(self):
		return self.group


class Refine:
	def __init__(self, aId, aName, aGroup, aInput, aOutputs):
		self.schemaId = aId
		self.name = aName
		self.input = aInput
		self.outputs = aOutputs
		self.group = aGroup

	def GetOutputs(self):
		return self.outputs

	def GetInputs(self):
		return [self.input]

	def GetName(self):
		return self.name

	def GetChild(self, row):
		return None

	def GetChildCount(self):
		return 0

	def GetIndexOfChild(self, aChild):
		return 0

	def GetParent(self):
		return self.group

def LoadRefine(aCursor, aTypeId, aGroup):
	
	aCursor.execute("SELECT materialTypeID, quantity "
		"FROM invTypeMaterials "
		"WHERE typeID = ? ",	(aTypeId,))
	rows = aCursor.fetchall()

	outputs = [row[0] for row in rows]

	aCursor.execute("SELECT typeName "
		"FROM invTypes t "
		"WHERE typeID = ? ", (aTypeId,))
	row = aCursor.fetchone()

	return Refine(aTypeId, row[0], aGroup, aTypeId, outputs)


def LoadBlueprint(aCursor, aBlueprintId, aGroup):
	
	aCursor.execute("SELECT tm.materialTypeID, quantity "
		"FROM invTypeMaterials tm, invBlueprintTypes bt "
		"WHERE tm.typeID = bt.productTypeID "
		"AND bt.blueprintTypeID = ?", (aBlueprintId,))
	rows = aCursor.fetchall()

	inputs = [row[0] for row in rows]
	aCursor.execute("SELECT blueprintTypeID, productTypeID, typeName "
		"FROM invBlueprintTypes bt, invTypes t "
		"WHERE blueprintTypeID = ? "
		"AND bt.blueprintTypeID = t.typeID;", (aBlueprintId,))
	row = aCursor.fetchone()

	return BluePrint(row[0], row[2], aGroup, inputs, row[1])
	
