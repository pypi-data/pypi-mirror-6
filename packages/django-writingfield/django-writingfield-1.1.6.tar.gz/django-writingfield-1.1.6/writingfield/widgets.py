from django.forms import Textarea


class FullScreenTextarea(Textarea):

    def __init__(self, attrs=None):
        # defaults
        default_attrs = {'class': 'fullscreen'}

        # save original class before smashing it up
        try:
            original_class = attrs['class']
        except (KeyError, TypeError):
            original_class = None

        # update attrs with defaults, or set to default
        try:
            attrs.update(default_attrs)
        except AttributeError:
            attrs = default_attrs

        # make sure fullscreen is always in attrs
        if original_class:
            attrs['class'] += ' {}'.format(original_class)

        # call the super
        super(FullScreenTextarea, self).__init__(attrs)

    class Media:
        css = {
            'screen': (
                '//fonts.googleapis.com/css?family=Roboto',
                'writingfield/writingfield.css',)
        }
        js = (
            'writingfield/mousetrap.min.js',
            'writingfield/writingfield.js',
        )
