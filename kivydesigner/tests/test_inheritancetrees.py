from kivydesigner.inheritancetrees import InheritanceTrees, InheritanceTreesBuilder
from kivydesigner.tests.common import test_output_dir
from pathlib import Path

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

def test_tree_builder_simple():
    '''Test parsing a single file with simple inheritance'''
    builder = InheritanceTreesBuilder()
    builder.build(SIMPLE_PY_1)
    tree = builder.tree
    assert len(tree) == 4
    assert tree.get_subclasses('Widget') == {'SimpleWidget', 'SimpleWidgetChild'}
    assert tree.get_subclasses('SimpleWidget') == {'SimpleWidgetChild'}
    assert tree.get_subclasses('SimpleWidgetChild') == set()
    assert tree.get_subclasses('UnrelatedObject') == set()

    assert tree.get_superclasses('Widget') == set()
    assert tree.get_superclasses('SimpleWidget') == {'Widget'}
    assert tree.get_superclasses('SimpleWidgetChild') == {'SimpleWidget', 'Widget'}
    assert tree.get_superclasses('UnrelatedObject') == set()

def test_serial_building_from_string():
    '''Test that parsing multiple files in serial will combine
    the inheritance graphs correctly'''
    builder = InheritanceTreesBuilder()
    builder.build(SIMPLE_PY_2) 
    builder.build(SIMPLE_PY_1)     
    tree = builder.tree               

    assert tree.get_subclasses('Widget') == {'SimpleWidget', 'SimpleWidgetChild', 'UnrelatedSimpleWidgetChild'}
    assert tree.get_subclasses('SimpleWidget') == {'SimpleWidgetChild', 'UnrelatedSimpleWidgetChild'}
    assert tree.get_subclasses('SimpleWidgetChild') == {'UnrelatedSimpleWidgetChild'}
    assert tree.get_subclasses('UnrelatedObject') == {'UnrelatedChild', 'UnrelatedSimpleWidgetChild'}
    assert tree.get_subclasses('UnrelatedChild') == set()
    assert tree.get_subclasses('UnrelatedSimpleWidgetChild') == set()

    assert tree.get_superclasses('Widget') == set()
    assert tree.get_superclasses('SimpleWidget') == {'Widget'}
    assert tree.get_superclasses('SimpleWidgetChild') == {'SimpleWidget', 'Widget'}
    assert tree.get_superclasses('UnrelatedObject') == set()
    assert tree.get_superclasses('UnrelatedChild') == {'UnrelatedObject'}
    assert tree.get_superclasses('UnrelatedSimpleWidgetChild') == {'SimpleWidgetChild', 'SimpleWidget', 'Widget', 'UnrelatedObject'}

RELATIVE_LAYOUT_CHILDREN = {'SandboxContent', 'ColorPicker', 'EffectWidget', 'FileChooserController', 
      'FileChooserListView', 'FileChooserIconView', 'FileChooser', 'ConsoleAddonBreadcrumbView', 'ConsoleAddonWidgetTreeView',
      'Console', 'Screen'}

def test_widget_search():
    '''Test that searching for widgets and apps works correctly'''
    kivy_builder = InheritanceTreesBuilder.kivy_widget_tree()
    SANDBOX_CONTENT_CHILDREN = set()
    EFFECT_WIDGET_CHILDREN = set() 
    FILECHOOSER_CONTROLLER_CHILDREN = {'FileChooserListView', 'FileChooserIconView', 'FileChooser'}
    
    assert RELATIVE_LAYOUT_CHILDREN == kivy_builder.tree.get_subclasses('RelativeLayout')
    assert SANDBOX_CONTENT_CHILDREN == kivy_builder.tree.get_subclasses('SandboxContent')
    assert EFFECT_WIDGET_CHILDREN == kivy_builder.tree.get_subclasses('EffectWidget')
    assert FILECHOOSER_CONTROLLER_CHILDREN == kivy_builder.tree.get_subclasses('FileChooserController')

def test_removing_single_class():
    kivy_tree = InheritanceTreesBuilder.kivy_widget_tree().tree

    kivy_tree.remove_class('RelativeLayout')

    assert kivy_tree.get_class('RelativeLayout') is None
    assert kivy_tree.get_subclasses('RelativeLayout') == set()
    for child in RELATIVE_LAYOUT_CHILDREN:
        assert 'RelativeLayout' not in kivy_tree.get_superclasses(child)

def test_removing_subclasses():
    kivy_tree = InheritanceTreesBuilder.kivy_widget_tree().tree

    kivy_tree.remove_class_and_subclasses('RelativeLayout')

    assert kivy_tree.get_class('RelativeLayout') is None
    assert kivy_tree.get_subclasses('RelativeLayout') == set()
    for child in RELATIVE_LAYOUT_CHILDREN:
        assert kivy_tree.get_class(child) == None

def test_known_kivy_widget_classes():
    '''Scan the current kivy installation and verify that our 
    hode coded list of known kivy widgets and App classes is correct.'''
    def get_actual_kivy_widget_tree():
        import kivy
        kivy_root_dir = kivy.__path__[0]
        dirs_to_exclude = (
            Path(kivy_root_dir) / 'tests',
            Path(kivy_root_dir) / 'core',
            Path(kivy_root_dir) / 'graphics',
            Path(kivy_root_dir) / 'input',
            Path(kivy_root_dir) / 'lib'
        )
        builder = InheritanceTreesBuilder()
        builder.build_from_directory(kivy.__path__[0], 
            lambda filepath: not any(filepath.is_relative_to(parent) for parent in dirs_to_exclude)) 
        return builder.tree

    # actual_tree generated by scanning the current kivy installation
    # expected_tree generated using hard coded list of known kivy widgets and App classes
    actual_tree = get_actual_kivy_widget_tree()
    expected_tree = InheritanceTreesBuilder.kivy_widget_tree().tree

    actual_widgets = actual_tree.get_subclasses('Widget')
    actual_apps = actual_tree.get_subclasses('App')

    expected_widgets = expected_tree.get_subclasses('Widget')
    expected_apps = expected_tree.get_subclasses('App')
    assert actual_widgets == expected_widgets
    assert actual_apps == expected_apps

def test_parsing_module_scoped_types():
    '''Test that parsing module-scoped types works correctly'''
    MODULE_SCOPED_CLASS_PY_1 = \
'''
class SimpleWidget1:
    pass 

class SimpleWidget2:
    pass
'''
    MODULE_SCOPED_CLASS_PY_2 = \
'''
import simplepy1

class SimpleChild1(simplepy1.SimpleWidget1):
    pass 

class SimpleGrandchild1(SimpleChild1):
    pass

class CommonChild(simplepy1.SimpleWidget2, SimpleChild1):
    pass
'''
    builder = InheritanceTreesBuilder()
    builder.build(MODULE_SCOPED_CLASS_PY_2)
    builder.build(MODULE_SCOPED_CLASS_PY_1)
    tree = builder.tree

    assert len(tree) == 5
    assert tree.get_subclasses('SimpleWidget1')  == {'SimpleChild1', 'SimpleGrandchild1', 'CommonChild'}
    assert tree.get_subclasses('SimpleWidget2')  == {'CommonChild'}
    assert tree.get_subclasses('SimpleChild1')  == {'SimpleGrandchild1', 'CommonChild'}

    assert tree.get_superclasses('SimpleChild1') == {'SimpleWidget1'}
    assert tree.get_superclasses('CommonChild') == {'SimpleWidget1', 'SimpleWidget2', 'SimpleChild1'}
    assert tree.get_superclasses('SimpleGrandchild1') == {'SimpleWidget1', 'SimpleChild1'}

SIMPLE_PY_1_UPDATED = \
'''
from kivy import Widget

class SimpleWidget(NewRootWidget):
    pass 

class SimpleWidgetChild(SimpleWidget):
    pass

class UnrelatedObject:
    pass
'''

def test_source_file_update(test_output_dir):
    '''Test that updating a source file will update the inheritance graph'''
    import os
    with open(os.path.join(test_output_dir, 'simplepy1.py'), 'w') as f:
        f.write(SIMPLE_PY_1)
    with open(os.path.join(test_output_dir, 'simplepy2.py'), 'w') as f:
        f.write(SIMPLE_PY_2)

    builder = InheritanceTreesBuilder()
    builder.build_from_file(os.path.join(test_output_dir, 'simplepy1.py'))
    builder.build_from_file(os.path.join(test_output_dir, 'simplepy2.py'))

    tree = builder.tree
    assert tree.get_subclasses('Widget') == {'SimpleWidget', 'SimpleWidgetChild', 'UnrelatedSimpleWidgetChild'}

    with open(os.path.join(test_output_dir, 'simplepy1.py'), 'w') as f:
        f.write(SIMPLE_PY_1_UPDATED)
    builder.refresh_source_file(os.path.join(test_output_dir, 'simplepy1.py'))

    assert tree.get_subclasses('NewRootWidget') == {'SimpleWidget', 'SimpleWidgetChild', 'UnrelatedSimpleWidgetChild'}
    assert tree.get_class('Widget') is None
    