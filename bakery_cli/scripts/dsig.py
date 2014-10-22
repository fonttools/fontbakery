from fontTools import ttLib
from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord


def create(fontpath):
    font = ttLib.TTFont(fontpath)

    newDSIG = ttLib.newTable("DSIG")
    newDSIG.ulVersion = 1
    newDSIG.usFlag = 1
    newDSIG.usNumSigs = 1
    sig = SignatureRecord()
    sig.ulLength = 20
    sig.cbSignature = 12
    sig.usReserved2 = 0
    sig.usReserved1 = 0
    sig.pkcs7 = '\xd3M4\xd3M5\xd3M4\xd3M4'
    sig.ulFormat = 1
    sig.ulOffset = 20
    newDSIG.signatureRecords = [sig]
    font.tables["DSIG"] = newDSIG

    font.save(fontpath + '.fix')
