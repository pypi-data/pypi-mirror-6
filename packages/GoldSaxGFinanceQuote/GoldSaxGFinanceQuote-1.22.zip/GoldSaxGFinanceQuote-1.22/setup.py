from distutils.core import setup
setup(
        name = 'GoldSaxGFinanceQuote',
        packages = ['GoldSaxGFinanceQuote'], # this must be the same as the name above
        version = '1.22',
        description = 'Auto aggregation, parsing of FIXML, FPML, XML, Json, FIX messages realtime data for storage, analytics to the GoldSaxEngine-****Markets or any other engine. This can be used by any Trader, Market Maker, a Retail Investor, Instituitional Investor, Hedge Fund Managers, and Asset Managers.',
        author = 'Vance King Saxbe. A',
        author_email = 'vsaxbe@yahoo.com',
        url = 'https://github.com/VanceKingSaxbeA/GoldSaxGFinanceQuote.git',   # use the URL to the github repo
        download_url = 'https://github.com/VanceKingSaxbeA/GoldSaxGFinanceQuote/archive/master.zip', # I'll explain this in a second
        keywords = ['FIX','FIXML','FPML','XML','JSON','AutoFetch Quotes', 'Automated Trading', 'Algorithmic Trading', 'Financial Markets', 'Hedge Funds', 'Asset Managers', 'investors'], # arbitrary keywords
        classifiers = ['Development Status :: 5 - Production/Stable','Intended Audience :: Financial and Insurance Industry','Intended Audience :: Information Technology','Intended Audience :: Science/Research','License :: OSI Approved :: Python Software Foundation License','Programming Language :: Python :: 2.7'],
    )
