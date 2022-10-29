from kivy.factory import Factory

# Register each of the custom widgets, to ensure they are available
# to the kvlang builder

Factory.register('IconButton', module='uix.iconbutton')
Factory.register('Toolbar', module='uix.toolbar')
Factory.register('FileToolbarGroup', module='uix.toolbar')
Factory.register('KivyVisualizer', module='uix.kivyvisualizer')