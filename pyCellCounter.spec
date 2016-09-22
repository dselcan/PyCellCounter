# -*- mode: python -*-

pccc = Analysis(['pyCellCounter.py'],
             pathex=['.'],
             hookspath=[],
             runtime_hooks=[])

pcca = Analysis(['pyCellAnalyzer.py'],
             pathex=['.'],
             hookspath=[],
             runtime_hooks=[])
			 
pccc.datas += [('icon.ico', 'icon.ico', 'DATA')]
pccc.datas += [('LICENSE', 'LICENSE', 'DATA')]
pcca.datas += [('icon2.ico', 'icon2.ico', 'DATA')]
pcca.datas += [('LICENSE', 'LICENSE', 'DATA')]
			 
			 
pccc_pyz = PYZ(pccc.pure)
pcca_pyz = PYZ(pcca.pure)
			 
pccc_exe = EXE(pccc_pyz,
          pccc.scripts,
          exclude_binaries=True,
          name='pyCellCounter',
          debug=False,
          strip=False,
          upx=True,
          console=False,
		  icon='icon.ico')		 
			 
pcca_exe = EXE(pcca_pyz,
          pcca.scripts,
          exclude_binaries=True,
          name='pyCellAnalyzer',
          debug=False,
          strip=False,
          upx=True,
          console=False,
		  icon='icon2.ico')
		  
pccc_coll = COLLECT(pccc_exe,
               pccc.binaries,
               pccc.zipfiles,
               pccc.datas,
               strip=False,
               upx=True,
               name='pyCellCounter')			  
		  
pcca_coll = COLLECT(pcca_exe,
               pcca.binaries,
               pcca.zipfiles,
               pcca.datas,
               strip=False,
               upx=True,
               name='pyCellAnalyzer')
