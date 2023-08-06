#!python
from common.subsystem.project.distribution import structured

CMRWebsite = ''

# todo: keywords, classifiers, fix author email, update version,
# get other attributes straight from the core.  determine license.

# fix using .pyc

@structured('WRLC') # .run
def setup(api):
    '''
    Westmetal Configuration::
        project = common.subsystem.project.distribution

    # todo: somehow tag this release as a 'cmr'
    WRLC(project$distribution):
        description: &description 'Runtime-level framework, subsystem, and language library.'
        summary: *description

        copyright: 2011-2014 All rights reserved.

        version: 0.4
        url: 'http://penobscotrobotics.us/cms/page/access-wrlc.htm'

        license: none
        classifiers: []
        keywords: []

        author: Clint Banis
        author-email: cbanis@gmail.com

        include-package-data: true

        # todo: put this all under description structure.
        ignore-packages: true
        ignore-description: true

        document:
            indent($expression): indent
            report::

                by {project[author]}, {environment[copyright]}

                This package contains a Composition Milestone Report (CMR) for:
                    Name: {project[name]}
                    Version: {project[version]}

                For information about a CMR, see:
                    {description.website}

                {description.indented}

                About this project:

                    {long_description}


        customization($method):
            parameters: [appl, client, config] # , +args, ++kwd]
            code::
                try: appl.deleteConfiguration('packages')
                except KeyError: pass

                report = container.document.report.format

                with appl.distributionApi as api:
                    kwd = dict(appl.meta,
                               description = client(api),
                               long_description = appl['description'],
                               application = appl,
                               client = client,
                               project = appl.settings,
                               environment = appl.environment)

                    appl.modifyConfiguration \
                        ('long_description',
                         report(**kwd))

                         '''

    # XXX Don't want to be using io.here, want to be using another
    # folder target, especially because the script will end up using
    # this exported (distribution) package.
    #
    # This is bad because it generates .pyc, thereby polluting our
    # checksum.  I suppose this is ok for _any other project_, but
    # alas, bootstrap.
    #
    # Because this is NOT a distutils command, just try to find landmark.
    from common.data.calc import ProjectHash

    # folder = io.path(__file__).folder

    def findNewest():
        MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        from common.runtime.layer.etc import _daily_time_pattern_base as timestamp

        import re
        pattern = re.compile(r'^wrlc-%s-r(\d+)$' % timestamp)

        newest = None

        for folder in io.here.baseFilter('wrlc-*-r*'):
            a = folder.basename
            m = pattern.match(a)

            if m is not None:
                (month, day, year, revision) = m.groups()
                month = MONTHS.index(month.lower())
                day = int(day)
                year = int(year)
                revision = int(revision)

                encoded = '%04d%02d%02d%08d' % (month, day, year, revision)
                if newest and encoded < newest[0]:
                    continue

                newest = [encoded, folder]

        if newest is None:
            return io.here

        return newest[1]

    from pdb import runcall
    folder = runcall(findNewest)
    hash = ProjectHash.GenerateFromProjectFolder(folder)

    return synthetic(text = hash, website = CMRWebsite,
                     indented = indent(hash)) # XXX indenting signature line...


if __name__ == '__main__':
    setup.main()

