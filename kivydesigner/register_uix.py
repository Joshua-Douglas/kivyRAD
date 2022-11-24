from kivy.factory import Factory

# Register each of the custom widgets, to ensure they are available
# to the kvlang builder

Factory.register('RootWidget', module='kivydesigner.kivydesigner')
Factory.register('IconButton', module='kivydesigner.uix.iconbutton')
Factory.register('Toolbar', module='kivydesigner.uix.toolbar')
Factory.register('FileToolbarGroup', module='kivydesigner.uix.toolbar')
Factory.register('KivyVisualizer', module='kivydesigner.uix.kivyvisualizer')