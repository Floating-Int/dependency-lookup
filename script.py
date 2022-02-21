import sys
import os
import ast
import importlib
from distutils.sysconfig import get_python_lib  # get pip package path


class ImportFinder(ast.NodeVisitor):
    def __init__(self):
        self.imports = []

    # @override
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)

    # @override
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append(node.module)

    @classmethod
    def parse_imports(cls, source):
        tree = ast.parse(source)
        visitor = cls()
        visitor.visit(tree)
        return visitor.imports


class Program:

    def __init__(self):
        # check if a file is supplied
        if len(sys.argv) <= 1:
            # print("[Error] No file supplied!")
            # return
            # -- DEBUG START
            sys.argv.append(r".\file.py")
            # -- DEBUG END
        elif not os.path.exists(sys.argv[1]):
            print("[Error] File does not exist:", sys.argv[1])
            return
        # get source
        self.fpath = sys.argv[1]  # pass local var in recursive search
        self.cwd = os.getcwd()
        if not os.path.isabs(self.fpath):
            self.fpath = os.path.join(self.cwd, self.fpath)
        # get libs paths
        self.path_builtin_modules = get_python_lib()
        self.path_site_packages = [path for path in sys.path if (
            os.path.isdir(path) and path.endswith("lib"))][0]
        # get content of libs
        self.builtin_files = sys.builtin_module_names
        self.builtin_modules = os.listdir(self.path_builtin_modules)
        self.site_packages = os.listdir(self.path_site_packages)
        self.locations = {}  # {path: [libs, ...]} pairs
        # for path in sys.path:
        #     self.locations[path] = []
        #     if os.path.isdir(path):
        #         self.locations[path] += os.listdir(path)  # add list
        self.results = set()
        # print("===")
        # print(*self.builtin_files, sep="\n")
        # print("===")
        # print(*self.builtin_modules, sep="\n")
        # print("===")
        # print(*self.site_packages, sep="\n")
        # print("===")

    @staticmethod
    def to_fname(full_fname):
        return full_fname.split(".")[0]  # 'file.py' -> 'file'

    def run(self):
        depth = 0
        relpath = "."
        self.recursive(self.fpath, relpath, depth)

    def recursive(self, fpath, relpath, depth):
        # edit fpath each turn unless end
        file = open(fpath, "r")
        source = file.read()
        imports = ImportFinder.parse_imports(source)
        for lib in imports:
            self.results.add(lib)  # add to set
            if lib in self.builtin_files:
                # is builtin, like 'sys' (end)
                print(1, "-" * depth + lib)
                continue  # don't start recursive search in 'lib'
            elif lib in map(self.to_fname, self.builtin_modules):
                # is site-package
                print(2, "-" * depth + lib)
            else:
                # check if lib exists
                if lib in map(self.to_fname, self.site_packages):
                    # is builtin lib
                    print(3, "-" * depth + lib)
                    fpath = os.path.join(
                        'C:\\Users\\Knut-Olai\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages', lib + ".py")
                    # print(fpath)
                    # nest recursive
                    #self.recursive(fpath, relpath, depth + 1)
                else:
                    # is relative
                    print(4, "-" * depth + lib)
                    lib_relpath = lib.replace(".", "\\")
                    if os.path.isdir(os.path.join(self.cwd, relpath, lib_relpath)):
                        # is relative file with nav
                        # print("fold")
                        #print(os.path.join(self.cwd, relpath, lib_relpath))
                        # return
                        relpath = os.path.join(relpath, lib_relpath)
                        # os.sep.join(...) = "\\".join(...) ( str.join(...) )
                        # elif (os.path.isdir(os.path.join(self.cwd, os.sep.join(lib.split(".")[:-1])))
                        #       and os.path.join(self.cwd, os.sep.join(lib.split(".")[:-1])) != self.cwd + os.sep):
                        # is relative folder with nav
                        # print(os.path.join(
                        #     self.cwd, os.sep.join(lib.split(".")[:-1])))
                        # print("file")
                        fpath = os.path.join(
                            self.cwd,
                            relpath,
                            lib_relpath + "\\__init__.py"
                        )
                        # print("A")
                    else:
                        # print("B")
                        # print(relpath)
                        relpath = os.path.join(
                            relpath, os.sep.join(lib.split(".")[:-1]))
                        # print(os.sep.join(lib.split(".")[:-1]))
                        # print(relpath)
                        # print("file")
                        fpath = os.path.join(
                            self.cwd,
                            relpath,
                            lib_relpath + ".py"
                        )
                    # print(relpath)
                    # print(fpath)
                    # relpath = os.path.join(relpath, lib.replace(".", "\\"))
                    # nest recursive
                    self.recursive(fpath, relpath, depth + 1)


if __name__ == "__main__":
    # C:\Users\Knut-Olai\AppData\Local\Programs\Python\Python39\lib
    print("-- Debug start --")
    # main()
    program = Program()
    program.run()
    #print(*program.locations.keys(), sep="\n")
    # print("== Libs ==")
    # print(*program.results, sep="\n")
    print("-- Debug end --")
