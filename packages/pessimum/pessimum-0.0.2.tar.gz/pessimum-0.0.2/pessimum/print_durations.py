
class PrintDurations(object):

    def __init__(self, stream, durations):
        self.stream = stream
        self.durations = durations

    def sorted_durations(self):
        return sorted(
            self.durations,
            key=lambda test: test.duration,
            reverse=True
        )

    def print_report(self):
        self.print_header()
        self.print_body()

    def print_body(self, count=10):
        for index, test in enumerate(self.sorted_durations()):
            if index == count: break
            self.write_line("   {0:10.3f}s for {1}".format(
                test.duration, unicode(test.reference)
            ))

    def print_header(self):
        self.write_line("Worst performing tests:")
        self.write_line()

    def write_line(self, string=""):
        self.stream.writeln(string)

