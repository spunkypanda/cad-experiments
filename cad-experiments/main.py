import ezdxf
from ezdxf.addons.dxf2code import entities_to_code, block_to_code

doc = ezdxf.readfile('files/first.dxf')
msp = doc.modelspace()
source = entities_to_code(msp)

# create source code for a block definition

# block_source = block_to_code(doc.block_records['TWOBYFOUR'])
block_source = block_to_code(doc.blocks['TWOBYFOUR'])

# merge source code objects
source.merge(block_source)

with open('source.py', mode='wt') as f:
    f.write(source.import_str())
    f.write('\n\n')
    f.write(source.code_str())
    f.write('\n')

