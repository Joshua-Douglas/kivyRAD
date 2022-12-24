from kivydesigner.kivydesigner import inheritancetrees

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

GENERIC_CLASS_PY = \
'''
class GenericClass(Generic[T]):
    pass 

class ConcreteGenericClass(GenericClass[int]):
    pass 

class MultipleGenericClass(GenericClass[T, S, V]):
    pass

class MultipleConcreteGenericClass(MultipleGenericClass[int, str, float]):
    pass

class GenericWidget(Generic[W], Widget):
    pass 

class ConcreteGenericWidget(GenericWidget[bool]):
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

def test_simple_single_parse():
    '''Test parsing a single file with simple inheritance'''
    # Add a simple py file to the test data above
    pass

def test_simple_double_parse():
    '''Test that parsing multiple files in serial will combine
    the inheritance graphs correctly'''
    # Add a file to complement simply py file that will add to 
    # the inheritance graph

def test_parsing_generic_types():
    '''Test that parsing generic types works correctly'''
    pass 

def test_generic_widgets():
    '''Test that widgets with a generic base can be detected'''
    pass 

def test_parsing_module_scoped_types():
    '''Test that parsing module-scoped types works correctly'''
    pass

def test_duplicate_class_names():
    '''Test that parsing duplicate class names works correctly'''
    # This will require modifying the inheritance graph. If duplicate
    # class names are found, the graph will need to be modified to
    # include the file path in the class name.
    pass

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


