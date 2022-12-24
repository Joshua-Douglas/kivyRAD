import ast 
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ClassDefNode:
    name: str
    source_path: str
    parents: list[str]
    children: list[str]

class InheritanceGraphs:
    def __init__(self) -> None:
        self.nodes = dict()

    def add_classdef(self, source_path, classname, parent_classnames):
        '''
        Add a class definition and parents to the graph. 
        If the class already exists, update its parents.
        If the parents already exist, update their children.
        Ignore duplicate entries. Enforce that a class can only have one set of parents.
        '''
        class_node = self.nodes.get(classname)
        if class_node:
            if len(class_node.parents) == 0:
                class_node.parents = parent_classnames
            elif class_node.parents == parent_classnames:
                # Duplicate entry. Ignore and exit. 
                return
            else:
                raise Exception("Class already exists with different parents.")
        else:
            class_node = ClassDefNode(classname, source_path, parent_classnames, list())
            self.nodes[classname] = class_node

        for parent_classname in parent_classnames:
            parent_node = self.nodes.get(parent_classname)
            if parent_node:
                parent_node.children.append(class_node.name)
            else:
                parent_node = ClassDefNode(parent_classname, source_path, list(), [class_node.name])
                self.nodes[parent_classname] = parent_node

    def get_subclasses(self, classname):
        '''
        Return a list of all subclasses of the given class.
        '''
        class_node = self.nodes.get(classname)
        if class_node:
            subclasses = set(class_node.children)
            for child in class_node.children:
                subclasses.update(self.get_subclasses(child))
            return subclasses
        return set()

    def get_superclasses(self, classname):
        '''
        Return a list of all superclasses of the given class.
        '''
        class_node = self.nodes.get(classname)
        if class_node:
            subclasses = set(class_node.parents)
            for parent in class_node.parents:
                subclasses.update(self.get_subclasses(parent))
            return subclasses
        return set()

    def get_all_classes(self):
        return self.nodes.keys()

    def remove_class(self, classname):
        '''
        Remove the given class from the graph.
        '''
        class_node = self.nodes.get(classname)
        if class_node:
            for parent in class_node.parents:
                parent_node = self.nodes.get(parent)
                parent_node.children.remove(class_node)
            for child in class_node.children:
                child.parents.remove(class_node)
            del self.nodes[classname]
    
    def remove_class_and_subclasses(self, classname):
        '''
        Remove the given class and all its subclasses from the graph.
        '''
        self.remove_class(classname)
        for subclass in self.get_subclasses(classname):
            self.remove_class(subclass)


class InheritanceGraphsBuilder(ast.NodeVisitor):
    '''
    Build inheritance graphs from python source code,
    without executing any code by parsing the AST.
    '''

    def __init__(self) -> None:
        self.current_filepath = None
        self.graphs = InheritanceGraphs()

    def visit_ClassDef(self, node):
        parents = list()
        for base in node.bases:
            if isinstance(base, ast.Name):
                # Standard base class declaration
                parents.append(base.id)
            elif isinstance(base, ast.Attribute):
                # Parent of form module.Class
                parents.append(base.attr)
            elif isinstance(base, ast.Subscript):
                # Generic Parent of form Generic[T1,...,Tn]
                if isinstance(base.slice, ast.Name):
                    type_params = [base.slice.id]
                elif isinstance(base.slice, ast.Tuple):
                    type_params = [e.id for e in base.slice.elts]
                elif isinstance(base.slice, ast.Constant):
                    type_params = [base.slice.value]
                else:
                    raise Exception("Unknown subscript type: " + str(type(base.slice)))
                parents.append(base.value.id + "[" + ",".join(type_params) + "]")
            elif isinstance(base, ast.Call):
                # Call classdef bases not supported.
                # Our goals is to avoid executing any code, and
                # we can't determine the return value of a Call
                # node without execution.
                pass
            else:
                raise Exception("Unknown base type: " + str(type(base)))
                
        self.graphs.add_classdef(self.current_filepath, node.name, parents)

    def build(self, file_source, source_filepath=None):
        tree = ast.parse(file_source)
        self.current_filepath = source_filepath
        self.visit(tree)
        self.current_filepath = None
        return self.graphs

    def build_from_file(self, filepath):
        try:
            file_source = Path(filepath).read_text()
            return self.build(file_source, filepath)
        except:
            return None

    def build_from_directory(self, directory):
        for filepath in Path(directory).rglob('**/*.py'):
            self.build_from_file(filepath)