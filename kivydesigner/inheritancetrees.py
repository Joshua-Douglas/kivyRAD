import ast 
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ClassDefNode:
    name: str
    source_path: str
    parents: list[str]
    children: list[str]

class InheritanceTrees:
    def __init__(self) -> None:
        self.nodes = dict()

    def __len__(self):
        return len(self.nodes)

    def add_class(self, source_path, classname, parent_classnames):
        '''
        Add a class definition and parents to the graph. 
        If the class already exists, update its parents.
        If the parents already exist, update their children.
        Ignore duplicate entries. Enforce that a class can only have one set of parents.
        '''
        class_node = self.get_class(classname)
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
            parent_node = self.get_class(parent_classname)
            if parent_node:
                parent_node.children.append(class_node.name)
            else:
                parent_node = ClassDefNode(parent_classname, '', list(), [class_node.name])
                self.nodes[parent_classname] = parent_node

    def get_class(self, classname):
        return self.nodes.get(classname)

    def get_subclasses(self, classname):
        '''
        Return a list of all subclasses of the given class.
        '''
        class_node = self.get_class(classname)
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
        class_node = self.get_class(classname)
        if class_node:
            superclasses = set(class_node.parents)
            for parent in class_node.parents:
                superclasses.update(self.get_superclasses(parent))
            return superclasses
        return set()

    def get_all_classes(self):
        return self.nodes.keys()

    def remove_class(self, classname):
        '''
        Remove the given class from the graph.
        '''
        class_node = self.get_class(classname)
        if class_node:
            for parent in class_node.parents:
                parent_node = self.get_class(parent)
                parent_node.children.remove(class_node.name)
            for child in class_node.children:
                child_node = self.get_class(child)
                child_node.parents.remove(class_node.name)
            del self.nodes[classname]
    
    def remove_class_and_subclasses(self, classname):
        '''
        Remove the given class and all its subclasses from the graph.
        '''
        for subclass in self.get_subclasses(classname):
            self.remove_class(subclass)
        self.remove_class(classname)
        
    def remove_source(self, source_path):
        '''
        Remove all class definitions from a given source file.
        '''
        cls_to_remove = \
            [(name, node) for (name, node) in self.nodes.items() 
                if node.source_path == source_path]
        for name, node in cls_to_remove:
            if node.source_path != source_path:
                continue
            # 1. Remove all the children that are in the same 
            # source file. Keep children that are in other files,
            # since these other classdefs will rely on this node.
            for child in node.children.copy():
                child_node = self.get_class(child)
                if child_node.source_path == source_path:
                    node.children.remove(child)
            #2. Clear the parent_node's children list of this node.
            for parent in node.parents.copy():
                parent_node = self.get_class(parent)
                if parent_node:
                    parent_node.children.remove(node.name)
                    if parent_node.source_path == source_path:
                        node.parents.remove(parent)
                # If the parent node has no parents or children, then it has 
                # only been encountered in this source file. Remove it.
                    if (len(parent_node.parents) == 0) and (len(parent_node.children) == 0):
                        del self.nodes[parent]
            #3. Clear node parents. The parents must be defined in current source.
            node.parents = []
            #4. If the children list is empty, remove the node.
            if len(node.children) == 0:
                del self.nodes[name]

class InheritanceTreesBuilder(ast.NodeVisitor):
    '''
    Build inheritance graphs from python source code,
    without executing any code by parsing the AST.

    This inheritance tree has several known limitations. None of which should 
    prevent building valid widget trees in the majority of cases:
    - Duplicate class names will can cause errors in the final tree. The 
    parent modules are not known at the time of parsing (without some exhaustive
    searching), so class names are compared using a global namespace. 
    - Generic classes are not well supported.
    - In rare cases, the ClassDef parent declaration may be a function 
    that returns the correct parent type at runtime. Since we are not 
    executing any code, these classes are ignored.
    '''
    def __init__(self) -> None:
        self.current_filepath = None
        self.tree = InheritanceTrees()

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
                
        self.tree.add_class(self.current_filepath, node.name, parents)

    def build(self, file_source, source_filepath=None):
        tree = ast.parse(file_source)
        self.current_filepath = source_filepath
        self.visit(tree)
        self.current_filepath = None
        return self.tree

    def build_from_file(self, filepath):
        try:
            file_source = Path(filepath).read_text()
            return self.build(file_source, filepath)
        except:
            return None

    def build_from_directory(self, directory, file_filter=None):
        for filepath in Path(directory).rglob('**/*.py'):
            if file_filter and file_filter(filepath):
                self.build_from_file(filepath)

    def refresh_source_file(self, filepath):
        '''
        Refresh the inheritance tree by re-parsing a single file.
        '''
        self.tree.remove_source(filepath)
        self.build_from_file(filepath)

    @classmethod
    def kivy_widget_tree(cls):
        '''
        Build a graph of all kivy widgets and app classes.
        Exclude test classes.
        '''
        import kivy
        kivy_root_dir = kivy.__path__[0]
        dirs_to_exclude = (
            Path(kivy_root_dir) / 'tests',
            Path(kivy_root_dir) / 'core',
            Path(kivy_root_dir) / 'graphics',
            Path(kivy_root_dir) / 'input',
            Path(kivy_root_dir) / 'lib'
        )
        builder = cls()
        builder.build_from_directory(kivy.__path__[0], 
            lambda filepath: not any(filepath.is_relative_to(parent) for parent in dirs_to_exclude)) 
            #any(parent in Path(filename).parts for parent in dirs_to_exclude))
        return builder