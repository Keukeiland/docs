from distutils.dir_util import copy_tree
from shutil import rmtree
from pathlib import Path
from glob import iglob
from git import Repo
import os

languages = {
    'js': [
        "/**",
        "*/",
        True,
        ['.js']
    ],
    'c': [
        "/**",
        "*/",
        True,
        ['.c','.cpp','.h']
    ],
    'python': [
        '"""',
        '"""',
        False,
        ['.py']
    ]
}

PATH = "./build/"

class Docstr:
    def __init__(self, origin):
        self.func = None
        self.desc = None
        self.origin = origin
        self.line = -1
    def __str__(self):
        desc = self.desc.replace("_", "\\_")
        func = self.func.replace("_", "\\_")
        return f"\n## {'.'.join(x for x in self.origin)}\n\n__{self.line}: {func}__\n\n{desc}\n"

def read(path, filename, origin, docstr_open, docstr_close, func_def_after):
    in_str = False
    last_line = None

    strs = []

    with open(path, "rt") as file:
        for number, line in enumerate(file):
            line = line.strip()

            if in_str:
                if line.endswith(docstr_close):
                    in_str = False
                    if func_def_after: tmp.func = next(file).strip()
                    tmp.origin += [item.split('(')[0] for item in tmp.func.split(' ') if "(" in item]
                    strs.append(tmp)
                else:
                    tmp.desc += '\n' + line.strip()
            
            elif line.startswith(docstr_open):
                in_str = True
                tmp = Docstr(origin + [filename])
                if not func_def_after: tmp.func = last_line
                tmp.desc = line[len(docstr_open):].strip()
                tmp.line = number

            last_line = line
    return strs


def process_repo(repo, repo_name, docstr_open, docstr_close, func_def_after, extensions):
    docstrs = {}

    for path in Path('./docs/'+repo_name+'/references/').glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)
    for path in Path('./docs/'+repo_name+'/documentation/').glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)

    Repo.clone_from(repo, PATH + repo_name)

    try: copy_tree(PATH+repo_name+'/docs', './docs/'+repo_name+'/documentation')
    except: pass

    for filepath in iglob(PATH + repo_name + '/**', recursive=True):
        if os.path.isfile(filepath): # If not dir
            dirpath, fileext = os.path.splitext(filepath)
            if fileext in extensions: # If extension is source
                docstrs[filepath] = [
                    read(filepath, filepath.split('/')[-1].split('.')[0], filepath.split('/')[:-1], docstr_open, docstr_close, func_def_after),
                    dirpath + '.md'
                ]

    for item in docstrs:
        item = docstrs[item]
        print(item)
        if not item[0]:
            continue
        name = './docs/'+repo_name+'/references/'+item[1][len(PATH + repo_name + '/'):]
        try: Path(name).parent.mkdir(parents=True, exist_ok=True)
        except: pass
        file = open(name, 'wt')
        print(item[1])
        for docstr in item[0]:
            file.write(str(docstr))
            file.write('\n')
        file.close()


def main():
    for path in Path(PATH).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)

    with open("./repos", 'rt') as file:
        for line in file:
            process_repo(line.strip(), next(file).strip(), *languages[next(file).strip()])

    os.system("mkdocs serve")


if __name__ == "__main__":
    main()