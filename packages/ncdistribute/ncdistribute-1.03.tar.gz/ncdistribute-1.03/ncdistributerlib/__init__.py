import sys
import os
import os.path
import stat
import zipfile
import modulefinder
from distutils.sysconfig import get_python_lib

"""
The Distributor class makes a python executable zip archive out of a script.

The pubic method is `package(filename)`.

The zipfile will be created in the directory specified in the class attribute `working_directory`.

Any paths included listed in the `excluded paths` attribute will be excluded from the package.  By default
the standard library is excluded.


"""




class Distributor(object):
    working_directory = 'zipdist'
    included_path  = sys.path.extend(['.',])
    
    def __init__(self, exclude_path_list=None):
        self.excluded_paths = [get_python_lib(standard_lib=True), ]
        if exclude_path_list:
            for excl in exclude_path_list:
                self.excluded_paths.append(excl)
    
    def find_libraries(self, filename):
        """
Find all modules uses by a given script.  Exclude any paths listed in `excluded_paths`.

Returns (modulename, module) for each of them.
        """
        M = modulefinder.ModuleFinder()
        M.run_script(filename)
        for k in M.modules.keys():
            #print(k)
            include_this = True
            if M.modules[k].__path__:
                for p in M.modules[k].__path__:
                    for excluded_path in self.excluded_paths:
                        if p.startswith(excluded_path):
                            include_this = False
                            break
                if include_this:
                    #print((k, M.modules[k]))
                    yield (k, M.modules[k])
                
    
    def package(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError
        working_dir = self.working_directory
        working_zip_file = os.path.join(working_dir, os.path.splitext(filename)[0] + '.pyz' + '.zip')
        output_path = os.path.join(working_dir, os.path.splitext(filename)[0] + '.pyz')
        print(output_path)
        if not os.path.exists(working_dir):
            os.mkdir(working_dir)
        
        if os.path.exists(output_path):
            os.remove(output_path)
            
        if os.path.exists(working_zip_file):
            os.remove(working_zip_file)
        
        with zipfile.ZipFile(working_zip_file, 'w', zipfile.ZIP_DEFLATED) as output_zip:
            output_zip.write(filename, '__main__.py')
            for modulename, module in self.find_libraries(filename):
                for path in module.__path__:
                    for dirname, subdirs, files in os.walk(path):
                        for f in files:
                            # could do some filtering here.
                            filename = os.path.join(dirname, f)
                            zipname  = os.path.join(modulename, dirname[len(path)+1:], f)
                            #print(filename, ' ', zipname)
                            output_zip.write(filename, zipname)
                
        
        with open(output_path, 'wb') as output_file:
            output_file.write("#!/usr/bin/env python3\n".encode('ascii'))
            with open(working_zip_file, 'rb') as prepared_zip: 
                data = prepared_zip.read()
                output_file.write(data)
        
        mode = os.stat(output_path)
        os.chmod(output_path, mode.st_mode | stat.S_IEXEC)
        
        if os.path.exists(working_zip_file):
            os.remove(working_zip_file)
        
        