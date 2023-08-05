# -------------------------------------------------------------------------
# C3PO - Coupling Capsule using CGNS/Python for OpenPalm
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------

# to be run with:
# export C3GENDOC
# C3GENDOC=1 sphinx-build -c doc -b html doc build/html 
# in the parent directory of this file

extensions = ['sphinx.ext.autodoc']
master_doc='index'
project = u'C3PO'
copyright = u'2013-, Marc Poinot'
version = '0'
release = '0.1'
unused_docs = ['license.txt']
source_suffix = '.txt'

pygments_style = 'sphinx'
html_title = "pyC3PO"
html_use_index = True

latex_paper_size = 'a4'
latex_font_size = '10pt'
latex_documents = [
  ("pyC3PO",
   'index.tex',
   u'pyC3PO - Coupling Capsule using CGNS/Python for OpenPalm Manual',
   u'Marc Poinot',
   'manual',False),
]
latex_use_parts = False
latex_use_modindex = True

autodoc_member_order='bysource'
autodoc_default_flags=['members', 'undoc-members']

# --- last line
