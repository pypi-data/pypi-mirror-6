from nose.plugins import Plugin

class PluginShim(Plugin):

    def beforeTest(self, test):
        self.before_test(test)

    def afterTest(self, test):
        self.after_test(test)

    def setOutputStream(self, stream):
        self.set_output_stream(stream)

    def raise_not_implemented_error(self):
        raise NotImplementedError(
            "Override this in the subclass"
        )

    def before_test(self, test):
        self.raise_not_implemented_error()

    def after_test(self, test):
        self.raise_not_implemented_error()

    def set_output_stream(self, stream):
        self.raise_not_implemented_error()
