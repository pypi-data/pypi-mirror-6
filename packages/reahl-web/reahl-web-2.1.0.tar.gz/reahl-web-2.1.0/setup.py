from setuptools import setup
setup(
    name='reahl-web',
    version=u'2.1.0',
    description='The core Reahl web framework',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis package contains the core of the Reahl framework.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.messages', 'reahl.web', 'reahl.web_dev', 'reahl.web.static', 'reahl.web_dev.inputandvalidation', 'reahl.web_dev.widgets', 'reahl.web_dev.appstructure', 'reahl.web_dev.advanced', 'reahl.web.static.jquery', 'reahl.web_dev.advanced.subresources'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=[u'reahl-component>=2.1,<2.2', u'reahl-interfaces>=2.1,<2.2', u'slimit>=0.8,<0.9', u'cssmin>=0.1,<0.2', u'BeautifulSoup>=3.2,<3.3', u'webob>=1.2,<1.3', u'Babel>=0.9,<0.10'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.1,<2.2', u'reahl-stubble>=2.1,<2.2', u'reahl-sqlalchemysupport>=2.1,<2.2', u'reahl-web-elixirimpl>=2.1,<2.2', u'reahl-domain>=2.1,<2.2', u'reahl-dev>=2.1,<2.2', u'reahl-webdev>=2.1,<2.2'],
    test_suite=u'reahl.web_dev',
    entry_points={
        'reahl.translations': [
            u'reahl-web = reahl.messages'    ],
        u'reahl.configspec': [
            u'config = reahl.web.egg:WebConfig'    ],
        u'reahl.attachments.css': [
            u'0:reahl/web/reahl.labelledinput.css = reahl',
            u'1:reahl/web/reahl.labeloverinput.css = reahl',
            u'2:reahl/web/reahl.menu.css = reahl',
            u'3:reahl/web/reahl.hmenu.css = reahl',
            u'4:reahl/web/reahl.slidingpanel.css = reahl',
            u'5:reahl/web/reahl.runningonbadge.css = reahl'    ],
        u'reahl.attachments.any': [
            u'0:reahl/web/static/runningon.png = reahl'    ],
        u'reahl.attachments.js': [
            u'0:reahl/web/reahl.hashchange.js = reahl',
            u'1:reahl/web/reahl.ajaxlink.js = reahl',
            u'2:reahl/web/reahl.form.js = reahl',
            u'3:reahl/web/reahl.textinput.js = reahl',
            u'4:reahl/web/reahl.cueinput.js = reahl',
            u'5:reahl/web/reahl.labeloverinput.js = reahl',
            u'6:reahl/web/reahl.fileuploadli.js = reahl',
            u'7:reahl/web/reahl.fileuploadpanel.js = reahl',
            u'8:reahl/web/reahl.popupa.js = reahl',
            u'9:reahl/web/reahl.slidingpanel.js = reahl'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        u'reahl.persistlist': [
            u'0 = reahl.web.pager:SequentialPageIndex'    ],
                 },
    extras_require={}
)
