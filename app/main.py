# External libraries
from git import Repo # pip install gitpython
# Common libraries
from distutils.dir_util import copy_tree
from shutil import rmtree
from pathlib import Path
from glob import iglob
import os

# Set constants
BUILD_DIR = "./build/" # Dir to store repos whilst building documentation
DOC_DIRS = ['docs','_docs'] # Directory names containing documentation in repos
# Docstring formats for languages in format:
#   [<docstring open seq>,
#   <docstring close seq>,
#   <docstring line markup>,
#   <bool if func def after docstring>,
#   <list of file extensions>]
LANGUAGES = {
    'js': [
        "/**",
        "*/",
        "* ",
        True,
        ['.js']
    ],
    'c': [
        "/**",
        "*/",
        "* ",
        True,
        ['.c','.cpp','.h']
    ],
    'python': [
        '"""',
        '"""',
        "",
        False,
        ['.py']
    ]
}



class Docstr:
    """ Stores information of a Docstring
        and stringifies to a MarkDown formatted
        version of said information.
    """
    def __init__(self, origin):
        self.func = None # Function name
        self.desc = None # The actual docstring
        self.origin = origin # Function origin path
        self.line = -1 # Starting line of docstring
    def __str__(self):
        # Escape MarkDown syntax in function names
        desc = self.desc.replace("_", "\\_") 
        func = self.func.replace("_", "\\_")
        # Convert self to MarkDown
        return f"\n## {'.'.join(x for x in self.origin if x)}\n\n__{self.line}: {func}__\n\n{desc}\n"

def read(path, filename, origin, docstr_open, docstr_close, docstr_markup, func_def_after):
    in_str = False
    last_line = None

    strs = []
    tmp = None
    with open(path, "rt") as file:
        for number, line in enumerate(file):
            line = line.strip()

            if in_str:
                if line.endswith(docstr_close):
                    in_str = False
                    if func_def_after:
                        try: tmp.func = next(file).strip()
                        except StopIteration: tmp.func = ''
                    tmp.origin += [item.split('(')[0] for item in tmp.func.split(' ') if "(" in item]
                    strs.append(tmp)
                else:
                    tmp.desc += '\n' + line.strip().lstrip(docstr_markup).replace('<','`').replace('>','`')
            
            elif line.startswith(docstr_open):
                in_str = True
                tmp = Docstr(origin + [filename])
                if not func_def_after: tmp.func = last_line
                tmp.desc = line[len(docstr_open):].strip()
                tmp.line = number

            last_line = line
    return strs


def process_repo(repo, repo_name, docstr_open, docstr_close, docstr_markup, func_def_after, extensions):
    docstrs = {}

    # Delete previously generated docs
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

    # Clone the repo
    Repo.clone_from(repo, BUILD_DIR + repo_name)

    # Copy all dirs containing documentation to repo/documentation
    for root, dirs, _ in os.walk(BUILD_DIR+repo_name):
        for d in dirs:
            if d in DOC_DIRS:
                try: copy_tree(root+'/'+d, './docs/'+repo_name+'/documentation'+root[len(BUILD_DIR+repo_name):])
                except: pass

    for filepath in iglob(BUILD_DIR + repo_name + '/**', recursive=True):
        # Skip documentation dirs
        if any(d in filepath for d in DOC_DIRS):
            continue
        # If file
        if os.path.isfile(filepath):
            # If extension is source code
            dirpath, fileext = os.path.splitext(filepath)
            if fileext in extensions:
                # Generate and store MarkDown-ed Docstring
                docstrs[filepath] = [
                    read(filepath, filepath.split('/')[-1].split('.')[0], filepath.split('/')[2:-1], docstr_open, docstr_close, docstr_markup, func_def_after),
                    dirpath + '.md'
                ]

    # Store all docstrings to documentation folders
    for item in docstrs:
        item = docstrs[item]
        if not item[0]:
            continue
        # Create parent dirs
        name = './docs/'+repo_name+'/references/'+item[1][len(BUILD_DIR + repo_name + '/'):]
        try: Path(name).parent.mkdir(parents=True, exist_ok=True)
        except: pass
        # Write the files
        with open(name, 'wt') as file:
            for docstr in item[0]:
                file.write(str(docstr))
                file.write('\n')



def main():
    # Clean build dir
    for path in Path(BUILD_DIR).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)

    # Read config file
    with open("./repos", 'rt') as file:
        for line in file:
            # Convert repo to documentation
            process_repo(line.strip(), next(file).strip(), *LANGUAGES[next(file).strip()])

    # Start MKDocs server
    os.system("mkdocs serve")


if __name__ == "__main__":
    main()