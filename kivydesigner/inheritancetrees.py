import ast 
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ClassDefNode:
    name: str
    source_path: str
    parents: list[str]
    children: list[str]
    def is_empty(self):
        return len(self.parents) == 0 and len(self.children) == 0

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
        for class_node in self.nodes.values():
            if class_node.source_path == source_path:
                for parent in class_node.parents:
                    parent_node = self.get_class(parent)
                    parent_node.children.remove(class_node.name)
                class_node.parents = []
                class_node.source_path = ''

        empty_nodes = [name for name, node in self.nodes.items() if node.is_empty()]
        for node in empty_nodes:
            del self.nodes[node]

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
        for pathitem in Path(directory).glob('*'):
            if file_filter and file_filter(pathitem):
                print(pathitem)
                if pathitem.is_dir():
                    self.build_from_directory(pathitem, file_filter)
                elif pathitem.is_file() and pathitem.suffix == ".py":
                    self.build_from_file(pathitem)

    def refresh_source_file(self, filepath):
        '''
        Refresh the inheritance tree by re-parsing a single file.
        '''
        self.tree.remove_source(filepath)
        self.build_from_file(filepath)

    @classmethod
    def empty(cls):
        '''
        Return an empty inheritance tree.
        '''
        return cls().tree

    @classmethod
    def kivy_widget_tree(cls):
        '''
        Build a graph of all kivy widgets and app classes.
        Exclude test classes.
        '''
        builder = cls()
        tree = builder.tree 
        # We could search kivy.__path__ for all kivy widgets, but
        # this takes about 0.3-0.4 seconds, and is more error prone than 
        # just hardcoding the list of widgets. A test case is available
        # to ensure the list is up to date.
        tree.add_class('', 'App', ['EventDispatcher'])
        tree.add_class('', 'ProxyImage', ['Image'])
        tree.add_class('', 'Image', ['Widget'])
        tree.add_class('', 'TreeViewProperty', ['BoxLayout', 'TreeViewNode'])
        tree.add_class('', 'BoxLayout', ['Layout'])
        tree.add_class('', 'ConsoleButton', ['Button'])
        tree.add_class('', 'Button', ['ButtonBehavior', 'Label'])
        tree.add_class('', 'ConsoleToggleButton', ['ToggleButton'])
        tree.add_class('', 'ToggleButton', ['ToggleButtonBehavior', 'Button'])
        tree.add_class('', 'ConsoleLabel', ['Label'])
        tree.add_class('', 'Label', ['Widget'])
        tree.add_class('', 'ConsoleAddonSeparator', ['Widget'])
        tree.add_class('', 'Widget', ['WidgetBase'])
        tree.add_class('', 'ConsoleAddonBreadcrumbView', ['RelativeLayout'])
        tree.add_class('', 'RelativeLayout', ['FloatLayout'])
        tree.add_class('', 'TreeViewWidget', ['Label', 'TreeViewNode'])
        tree.add_class('', 'ConsoleAddonWidgetTreeImpl', ['TreeView'])
        tree.add_class('', 'TreeView', ['Widget'])
        tree.add_class('', 'ConsoleAddonWidgetTreeView', ['RelativeLayout'])
        tree.add_class('', 'Console', ['RelativeLayout'])
        tree.add_class('', 'WidgetTree', ['TreeView'])
        tree.add_class('', 'Inspector', ['FloatLayout'])
        tree.add_class('', 'FloatLayout', ['Layout'])
        tree.add_class('', 'JoyCursor', ['Widget'])
        tree.add_class('', 'KvViewerApp', ['App'])
        tree.add_class('', 'AccordionItem', ['FloatLayout'])
        tree.add_class('', 'Accordion', ['Widget'])
        tree.add_class('', 'ActionButton', ['Button', 'ActionItem'])
        tree.add_class('', 'ActionPrevious', ['BoxLayout', 'ActionItem'])
        tree.add_class('', 'ActionToggleButton', ['ActionItem', 'ToggleButton'])
        tree.add_class('', 'ActionLabel', ['ActionItem', 'Label'])
        tree.add_class('', 'ActionCheck', ['ActionItem', 'CheckBox'])
        tree.add_class('', 'CheckBox', ['ToggleButtonBehavior', 'Widget'])
        tree.add_class('', 'ActionSeparator', ['ActionItem', 'Widget'])
        tree.add_class('', 'ActionDropDown', ['DropDown'])
        tree.add_class('', 'DropDown', ['ScrollView'])
        tree.add_class('', 'ActionGroup', ['ActionItem', 'Button'])
        tree.add_class('', 'ActionOverflow', ['ActionGroup'])
        tree.add_class('', 'ActionView', ['BoxLayout'])
        tree.add_class('', 'ContextualActionView', ['ActionView'])
        tree.add_class('', 'ActionBar', ['BoxLayout'])
        tree.add_class('', 'MainWindow', ['FloatLayout'])
        tree.add_class('', 'AnchorLayout', ['Layout'])
        tree.add_class('', 'Layout', ['Widget'])
        tree.add_class('', 'BubbleButton', ['Button'])
        tree.add_class('', 'BubbleContent', ['GridLayout'])
        tree.add_class('', 'GridLayout', ['Layout'])
        tree.add_class('', 'Bubble', ['GridLayout'])
        tree.add_class('', 'Camera', ['Image'])
        tree.add_class('', 'Carousel', ['StencilView'])
        tree.add_class('', 'StencilView', ['Widget'])
        tree.add_class('', 'Example1', ['App'])
        tree.add_class('', 'CodeInput', ['CodeNavigationBehavior', 'TextInput'])
        tree.add_class('', 'TextInput', ['FocusBehavior', 'Widget'])
        tree.add_class('', 'CodeInputTest', ['App'])
        tree.add_class('', 'ColorWheel', ['Widget'])
        tree.add_class('', 'ColorPicker', ['RelativeLayout'])
        tree.add_class('', 'ColorPickerApp', ['App'])
        tree.add_class('', 'ScrollView', ['StencilView'])
        tree.add_class('', 'EffectWidget', ['RelativeLayout'])
        tree.add_class('', 'FileChooserProgressBase', ['FloatLayout'])
        tree.add_class('', 'FileChooserProgress', ['FileChooserProgressBase'])
        tree.add_class('', 'FileChooserLayout', ['FloatLayout'])
        tree.add_class('', 'FileChooserListLayout', ['FileChooserLayout'])
        tree.add_class('', 'FileChooserIconLayout', ['FileChooserLayout'])
        tree.add_class('', 'FileChooserController', ['RelativeLayout'])
        tree.add_class('', 'FileChooserListView', ['FileChooserController'])
        tree.add_class('', 'FileChooserIconView', ['FileChooserController'])
        tree.add_class('', 'FileChooser', ['FileChooserController'])
        tree.add_class('', 'FileChooserApp', ['App'])
        tree.add_class('', 'GestureSurface', ['FloatLayout'])
        tree.add_class('', 'AsyncImage', ['Image'])
        tree.add_class('', 'ModalView', ['AnchorLayout'])
        tree.add_class('', 'PageLayout', ['Layout'])
        tree.add_class('', 'Popup', ['ModalView'])
        tree.add_class('', 'ProgressBar', ['Widget'])
        tree.add_class('', 'RecycleBoxLayout', ['RecycleLayout', 'BoxLayout'])
        tree.add_class('', 'RecycleLayout', ['RecycleLayoutManagerBehavior', 'Layout'])
        tree.add_class('', 'RecycleGridLayout', ['RecycleLayout', 'GridLayout'])
        tree.add_class('', 'RstVideoPlayer', ['VideoPlayer'])
        tree.add_class('', 'VideoPlayer', ['GridLayout'])
        tree.add_class('', 'RstDocument', ['ScrollView'])
        tree.add_class('', 'RstTitle', ['Label'])
        tree.add_class('', 'RstParagraph', ['Label'])
        tree.add_class('', 'RstTerm', ['AnchorLayout'])
        tree.add_class('', 'RstBlockQuote', ['GridLayout'])
        tree.add_class('', 'RstLiteralBlock', ['GridLayout'])
        tree.add_class('', 'RstList', ['GridLayout'])
        tree.add_class('', 'RstListItem', ['GridLayout'])
        tree.add_class('', 'RstListBullet', ['Label'])
        tree.add_class('', 'RstSystemMessage', ['GridLayout'])
        tree.add_class('', 'RstWarning', ['GridLayout'])
        tree.add_class('', 'RstNote', ['GridLayout'])
        tree.add_class('', 'RstImage', ['Image'])
        tree.add_class('', 'RstAsyncImage', ['AsyncImage'])
        tree.add_class('', 'RstDefinitionList', ['GridLayout'])
        tree.add_class('', 'RstDefinition', ['GridLayout'])
        tree.add_class('', 'RstFieldList', ['GridLayout'])
        tree.add_class('', 'RstFieldName', ['Label'])
        tree.add_class('', 'RstFieldBody', ['GridLayout'])
        tree.add_class('', 'RstFootnote', ['GridLayout'])
        tree.add_class('', 'RstFootName', ['Label'])
        tree.add_class('', 'RstGridLayout', ['GridLayout'])
        tree.add_class('', 'RstTable', ['GridLayout'])
        tree.add_class('', 'RstEntry', ['GridLayout'])
        tree.add_class('', 'RstTransition', ['Widget'])
        tree.add_class('', 'RstEmptySpace', ['Widget'])
        tree.add_class('', 'RstDefinitionSpace', ['Widget'])
        tree.add_class('', 'SandboxContent', ['RelativeLayout'])
        tree.add_class('', 'Sandbox', ['FloatLayout'])
        tree.add_class('', 'TestButton', ['Button'])
        tree.add_class('', 'Scatter', ['Widget'])
        tree.add_class('', 'ScatterPlane', ['Scatter'])
        tree.add_class('', 'ScatterLayout', ['Scatter'])
        tree.add_class('', 'ScatterPlaneLayout', ['ScatterPlane'])
        tree.add_class('', 'Screen', ['RelativeLayout'])
        tree.add_class('', 'ScreenManager', ['FloatLayout'])
        tree.add_class('', 'TestApp', ['App'])
        tree.add_class('', 'ScrollViewApp', ['App'])
        tree.add_class('', 'SettingSpacer', ['Widget'])
        tree.add_class('', 'SettingItem', ['FloatLayout'])
        tree.add_class('', 'SettingBoolean', ['SettingItem'])
        tree.add_class('', 'SettingString', ['SettingItem'])
        tree.add_class('', 'SettingPath', ['SettingItem'])
        tree.add_class('', 'SettingColor', ['SettingItem'])
        tree.add_class('', 'SettingNumeric', ['SettingString'])
        tree.add_class('', 'SettingOptions', ['SettingItem'])
        tree.add_class('', 'SettingTitle', ['Label'])
        tree.add_class('', 'SettingsPanel', ['GridLayout'])
        tree.add_class('', 'InterfaceWithSidebar', ['BoxLayout'])
        tree.add_class('', 'InterfaceWithSpinner', ['BoxLayout'])
        tree.add_class('', 'ContentPanel', ['ScrollView'])
        tree.add_class('', 'Settings', ['BoxLayout'])
        tree.add_class('', 'SettingsWithSidebar', ['Settings'])
        tree.add_class('', 'SettingsWithSpinner', ['Settings'])
        tree.add_class('', 'SettingsWithTabbedPanel', ['Settings'])
        tree.add_class('', 'SettingsWithNoMenu', ['Settings'])
        tree.add_class('', 'InterfaceWithNoMenu', ['ContentPanel'])
        tree.add_class('', 'InterfaceWithTabbedPanel', ['FloatLayout'])
        tree.add_class('', 'MenuSpinner', ['BoxLayout'])
        tree.add_class('', 'MenuSidebar', ['FloatLayout'])
        tree.add_class('', 'SettingSidebarLabel', ['Label'])
        tree.add_class('', 'SettingsApp', ['App'])
        tree.add_class('', 'Slider', ['Widget'])
        tree.add_class('', 'SliderApp', ['App'])
        tree.add_class('', 'SpinnerOption', ['Button'])
        tree.add_class('', 'Spinner', ['Button'])
        tree.add_class('', 'SplitterStrip', ['Button'])
        tree.add_class('', 'Splitter', ['BoxLayout'])
        tree.add_class('', 'SplitterApp', ['App'])
        tree.add_class('', 'StackLayout', ['Layout'])
        tree.add_class('', 'Switch', ['Widget'])
        tree.add_class('', 'TabbedPanelHeader', ['ToggleButton'])
        tree.add_class('', 'TabbedPanelItem', ['TabbedPanelHeader'])
        tree.add_class('', 'TabbedPanelStrip', ['GridLayout'])
        tree.add_class('', 'StripLayout', ['GridLayout'])
        tree.add_class('', 'TabbedPanelContent', ['FloatLayout'])
        tree.add_class('', 'TabbedPanel', ['GridLayout'])
        tree.add_class('', 'Selector', ['ButtonBehavior', 'Image'])
        tree.add_class('', 'TextInputCutCopyPaste', ['Bubble'])
        tree.add_class('', 'TextInputApp', ['App'])
        tree.add_class('', 'TreeViewLabel', ['Label', 'TreeViewNode'])
        tree.add_class('', 'Video', ['Image'])
        tree.add_class('', 'VideoApp', ['App'])
        tree.add_class('', 'VideoPlayerVolume', ['Image'])
        tree.add_class('', 'VideoPlayerPlayPause', ['Image'])
        tree.add_class('', 'VideoPlayerStop', ['Image'])
        tree.add_class('', 'VideoPlayerProgressBar', ['ProgressBar'])
        tree.add_class('', 'VideoPlayerPreview', ['FloatLayout'])
        tree.add_class('', 'VideoPlayerAnnotation', ['Label'])
        tree.add_class('', 'VKeyboard', ['Scatter'])
        tree.add_class('', 'RecycleView', ['RecycleViewBehavior', 'ScrollView'])
        return builder