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
        # self.builtin_modules = os.listdir(self.path_builtin_modules)
        # self.site_packages = os.listdir(self.path_site_packages)
        self.locations = {}  # {path: [libs, ...]} pairs
        for path in sys.path:
            self.locations[path] = []
            if os.path.isdir(path):
                self.locations[path] += os.listdir(path)  # add list
        self.results = []
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
        file = open(fpath, "r", errors="ignore")
        #print("-", fpath)
        source = file.read()
        imports = ImportFinder.parse_imports(source)
        for lib in imports:
            if lib in self.results:
                return

            if lib in self.builtin_files:
                print("StdF", "-" * depth + lib)

            else:

                for path, libs in self.locations.items():
                    if lib in libs:
                        self.results.append(lib)  # add to list
                        # if lib module
                        print("Fold", "-" * depth + lib)
                        #print("-", path)
                        fpath = os.path.join(path, lib + "\\__init__.py")
                        self.recursive(fpath, relpath, depth + 1)
                        # break
                    elif lib + ".py" in libs:
                        self.results.append(lib)  # add to list
                        # is lib file
                        print("File", "-" * depth + lib)
                        #print("-", path)
                        fpath = os.path.join(path, lib + ".py")
                        self.recursive(fpath, relpath, depth + 1)
                        # break

            # nest recursive
            #self.recursive(fpath, relpath, depth + 1)
        file.close()


if __name__ == "__main__":
    # C:\Users\Knut-Olai\AppData\Local\Programs\Python\Python39\lib
    print("-- Debug start --")
    # main()
    program = Program()
    program.run()
    print("===")
    print(*program.results, sep="\n")
    # print("== Libs ==")
    # print(*program.results, sep="\n")
    print("-- Debug end --")
