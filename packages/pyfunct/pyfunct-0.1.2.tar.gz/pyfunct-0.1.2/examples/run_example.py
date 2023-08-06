import nose
import time
import os

from nose.plugins import Plugin


css = """
body{
    background: #f5f5f5;
}

.test-result{
    background: rgb(231, 231, 231);
    color: rgb(231, 42, 42);
    padding: 10px 35px;
    border-radius: 15px;
    text-align: center;
    margin-top: 20px;
}

.test-result img{
    width: 350px;
    height: auto;
}

.test-result.error{
    color: rgb(231, 42, 42);
}

.test-result.failure{
    color: rgb(255, 133, 0);
}

.test-result p{
    color: black;
    font-weight: bold
}

.container{
    width: 800px;
    margin: 0 auto;
}
"""


class PyfunctReport(Plugin):

    name = 'pyfunct-report'
    score = 2  # run late

    def __init__(self):
        super(PyfunctReport, self).__init__()
        self.html_report = '<html><style>%s</style><body><div class="container"><h1>Error report - Screenshots</h1>' % css

    def options(self, parser, env=os.environ):
        super(PyfunctReport, self).options(parser, env=env)

    def addError(self, test, err):
        self.html_report += '<div class="test-result error">'
        self.html_report += '<h2>Error (%s)</h2>' % test
        self._handle_failure(test, err)
        self.html_report += '</div>'

    def addFailure(self, test, err):
        self.html_report += '<div class="test-result failure">'
        self.html_report += '<h2>Failure (%s)</h2>' % test
        self._handle_failure(test, err)
        self.html_report += '</div>'

    def finalize(self, result):
        self.html_report += '</html>'
        with open('/tmp/pyfunct_error_report.html', 'w') as _f:
            _f.write(self.html_report)

    def _handle_failure(self, test, err):
        for i, browser in enumerate(test.test.browsers):
            self.html_report += '<p>Browser %s</p>' % (i + 1)
            screenshot_path = '/tmp/screen_err_%s.png' % int(time.time())
            browser._browser.driver.save_screenshot(screenshot_path)
            self.html_report += '<a href="%s"><img src="%s"/></a>' % (screenshot_path, screenshot_path)

if __name__ == '__main__':
    nose.main(module='examples', addplugins=[PyfunctReport()])
