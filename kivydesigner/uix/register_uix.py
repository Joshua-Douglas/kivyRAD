from kivy.factory import Factory

# Register each of the custom widgets, to ensure they are available
# to the kvlang builder

Factory.register('IconButton', module='kivydesigner.uix.iconbutton')
Factory.register('Toolbar', module='toolbar')
Factory.register('FileToolbarGroup', module='toolbar')
Factory.register('KivyVisualizer', module='kivyvisualizer')