from .main import Test


class Inheritance(Test):

    def TEMPLATE_CONTEXT_PROCESSORS(self):
        return super(Inheritance, self).TEMPLATE_CONTEXT_PROCESSORS() + (
            'tests.settings.base.test_callback',)
