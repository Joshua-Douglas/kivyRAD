from kivydesigner.inheritancetrees import InheritanceTrees

## Let's hard code the example files here as strings for now
SIMPLE_PY_1 = \
'''
from kivy import Widget

class SimpleWidget(Widget):
    pass 

class SimpleWidgetChild(SimpleWidget):
    pass

class UnrelatedObject:
    pass
'''

SIMPLE_PY_2 = \
'''
from simplepy1 import SimpleWidget, UnrelatedObject

class UnrelatedChild(UnrelatedObject):
    pass 

class UnrelatedSimpleWidgetChild(SimpleWidgetChild, UnrelatedObject):
    pass 
'''

MODULE_SCOPED_CLASS_PY = \
'''
import simplepy1

class ModuleScopedClass(simplepy1.SimpleWidget):
    pass 

class ModuleScopedClassChild(ModuleScopedClass):
    pass

class UnrelatedObjectScopedChild(simplepy1.UnrelatedObject, ModuleScopedClass):
    pass
'''

EXAMPLE_CUSTOM_TREEVIEW = \
'''
class CustomTreeView(FocusBehavior, TreeView):
    pass
'''

EXAMPLE_CUSTOM_LAYOUT = \
'''
class CustomLayout(Layout):
    pass
'''

def test_add_simple_class():
    tree = InheritanceTrees()
    tree.add_class(__file__, 'SimpleWidget', [])
    assert len(tree) == 1
    cls = tree.get_class('SimpleWidget')
    assert cls.name == 'SimpleWidget'
    assert cls.children == []
    assert cls.parents == []
    assert cls.source_path == __file__

def test_simple_get_subclass():
    tree = InheritanceTrees()
    tree.add_class(__file__, 'SimpleWidget', [])
    tree.add_class(__file__, 'SimpleWidgetChild', ['SimpleWidget'])
    tree.add_class(__file__, 'SimpleWidgetGrandChild1', ['SimpleWidgetChild', 'SharedParent'])
    tree.add_class(__file__, 'SimpleWidgetGrandChild2', ['SimpleWidgetChild', 'SharedParent'])

    assert len(tree) == 5
    
    assert tree.get_subclasses('SimpleWidget') == set(['SimpleWidgetChild', 'SimpleWidgetGrandChild1', 'SimpleWidgetGrandChild2'])
    assert tree.get_subclasses('SimpleWidgetChild') == set(['SimpleWidgetGrandChild1', 'SimpleWidgetGrandChild2'])
    assert tree.get_subclasses('SharedParent') == set(['SimpleWidgetGrandChild1', 'SimpleWidgetGrandChild2'])
    assert tree.get_subclasses('SimpleWidgetGrandChild1') == set()
    assert tree.get_subclasses('SimpleWidgetGrandChild2') == set()

def test_simple_get_superclass():
    tree = InheritanceTrees()
    tree.add_class(__file__, 'SimpleWidget', [])
    tree.add_class(__file__, 'SimpleWidgetChild', ['SimpleWidget'])
    tree.add_class(__file__, 'SimpleWidgetGrandChild1', ['SimpleWidgetChild', 'SharedParent'])
    tree.add_class(__file__, 'SimpleWidgetGrandChild2', ['SimpleWidgetChild', 'SharedParent'])

    assert len(tree) == 5
    
    assert tree.get_superclasses('SimpleWidget') == set()
    assert tree.get_superclasses('SimpleWidgetChild') == set(['SimpleWidget'])
    assert tree.get_superclasses('SharedParent') == set()
    assert tree.get_superclasses('SimpleWidgetGrandChild1') == set(['SimpleWidgetChild', 'SimpleWidget', 'SharedParent'])
    assert tree.get_superclasses('SimpleWidgetGrandChild2') == set(['SimpleWidgetChild', 'SimpleWidget', 'SharedParent'])

def test_simple_get_superclass_reverse():
    '''Same test as test_simple_get_superclass, but with the order of the class addition is 
    reversed to check for order dependence.'''
    tree = InheritanceTrees() 
    tree.add_class(__file__, 'SimpleWidgetGrandChild2', ['SimpleWidgetChild', 'SharedParent'])
    tree.add_class(__file__, 'SimpleWidgetGrandChild1', ['SimpleWidgetChild', 'SharedParent'])
    tree.add_class(__file__, 'SimpleWidgetChild', ['SimpleWidget'])
    tree.add_class(__file__, 'SimpleWidget', [])

    assert len(tree) == 5
    
    assert tree.get_superclasses('SimpleWidget') == set()
    assert tree.get_superclasses('SimpleWidgetChild') == set(['SimpleWidget'])
    assert tree.get_superclasses('SharedParent') == set()
    assert tree.get_superclasses('SimpleWidgetGrandChild1') == set(['SimpleWidgetChild', 'SimpleWidget', 'SharedParent'])
    assert tree.get_superclasses('SimpleWidgetGrandChild2') == set(['SimpleWidgetChild', 'SimpleWidget', 'SharedParent'])

def test_classdef_path():
    '''Test that the source file path is correct set for newly added classes,
    but left empty for unknown classes.
    '''
    tree = InheritanceTrees()
    tree.add_class('first_source', 'SimpleWidget', ['UnknownPathParent'])
    tree.add_class('second_source', 'SimpleWidgetChild', ['SimpleWidget'])

    assert len(tree) == 3
    assert tree.get_class('SimpleWidget').source_path == 'first_source'
    assert tree.get_class('SimpleWidgetChild').source_path == 'second_source'
    assert tree.get_class('UnknownPathParent').source_path == ''

def test_add_simple_class_with_parent():
    tree = InheritanceTrees()
    tree.add_class(__file__, 'SimpleWidgetChild', ['SimpleWidget'])
    assert len(tree) == 2
    parent = tree.get_class('SimpleWidget')
    child = tree.get_class('SimpleWidgetChild')
    assert parent.name == 'SimpleWidget'
    assert parent.parents == []
    assert parent.children == [child.name]
    assert parent.source_path == ''

    assert child.name == 'SimpleWidgetChild'
    assert child.parents == [parent.name]
    assert child.children == []
    assert child.source_path == __file__

def test_add_simple_class_with_parents_and_children():
    tree = InheritanceTrees()
    tree.add_class(__file__, 'SimpleWidgetChild', ['SimpleWidget', 'AnotherParent'])
    tree.add_class(__file__, 'SimpleWidgetGrandChild', ['SimpleWidgetChild', 'RandomDifferentParent'])

    assert len(tree) == 5
    top_parent1 = tree.get_class('SimpleWidget')
    top_parent2 = tree.get_class('AnotherParent')
    child = tree.get_class('SimpleWidgetChild')
    middle_parent = tree.get_class('RandomDifferentParent')
    grandchild = tree.get_class('SimpleWidgetGrandChild')

    for cls in (top_parent1, top_parent2, middle_parent):
        assert cls.source_path == ''

    for cls in (child, grandchild):
        assert cls.source_path == __file__

    for top_parent in (top_parent1, top_parent2, middle_parent):
        assert top_parent.parents == []

    assert top_parent1.children == [child.name]
    assert top_parent2.children == [child.name]
    assert middle_parent.children == [grandchild.name]

    assert child.parents == [top_parent1.name, top_parent2.name]
    assert child.children == [grandchild.name]

    assert grandchild.parents == [child.name, middle_parent.name]
    assert grandchild.children == []

def test_parsing_module_scoped_types():
    '''Test that parsing module-scoped types works correctly'''
    tree = InheritanceTrees()
    tree.add_class(__file__, 'SimpleWidgetChild', ['parentmodule.SimpleWidget', 'anothermodule.AnotherParent'])
    tree.add_class(__file__, 'SimpleWidgetGrandChild', ['SimpleWidgetChild', 'RandomDifferentParent'])
    pass

def test_duplicate_class_names():
    '''Test that parsing duplicate class names works correctly'''
    # This will require modifying the inheritance graph. If duplicate
    # class names are found, the graph will need to be modified to
    # include the file path in the class name.
    pass

def test_generic_widgets_simple():
    '''Test that generic base classes are captured, using their example
    typevar symbols. Note that this is not a robust solution for detecting
    generic base classes, but it is a start.'''
    tree = InheritanceTrees()
    tree.add_class(__file__, 'GenericParent', ['Generic[T]'])
    tree.add_class(__file__, 'ConcreteChild1', ['GenericParent[bool]', 'RandomDifferentParent'])
    tree.add_class(__file__, 'ConcreteChild2', ['GenericParent[int]', 'RandomDifferentParent'])

    assert len(tree) == 7

    # Subclass search fails for GenericParent, because it is captured in the tree without
    # a typevar symbol. This is a limitation of the current implementation, and is due to 
    # the fact that the AST does not differentiate between concrete and generic base classes
    # e.g. (GenericParent[bool] vs GenericParent[T])
    assert tree.get_subclasses('Generic[T]') == set(['GenericParent'])
    assert tree.get_subclasses('GenericParent') == set()

def test_building_from_string():
    '''Test parsing a single file with simple inheritance'''
    # Add a simple py file to the test data above
    pass

def test_serial_building_from_string():
    '''Test that parsing multiple files in serial will combine
    the inheritance graphs correctly'''
    # Add a file to complement simply py file that will add to 
    # the inheritance graph

def test_source_file_update():
    '''Test that updating a source file will update the inheritance graph'''
    pass

def test_widget_search():
    '''Test that searching for widgets and apps works correctly'''
    pass

def test_known_kivy_widget_classes():
    '''Scan the current kivy installation and verify that our 
    hode coded list of known kivy widgets and App classes is correct.'''
    pass 

def test_building_from_directory():
    '''Test that building an inheritance graph from a directory works correctly'''
    # Create a temporary directory
    # Write our hard coded py files to it 
    # scan the directory and build the inheritance graph
    # Verify that it matches our manually built graph
    pass


