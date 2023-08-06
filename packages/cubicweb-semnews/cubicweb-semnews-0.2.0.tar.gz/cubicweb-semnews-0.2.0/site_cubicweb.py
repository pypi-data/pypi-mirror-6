

###############################################################################
### SOURCE TYPES ##############################################################
###############################################################################

options = (
    ('articles-lang',
     {'type' : 'string',
      'default': 'fr',
      'help': 'Language of the articles to be used (e.g. in startup view).',
      'group': 'semnews', 'level': 2,
      }),
    ('articles-dataviz-limit',
     {'type' : 'int',
      'default': 40,
      'help': 'Number of articles to be used for some dataviz views.',
      'group': 'semnews', 'level': 2,
      }),
    ('startup-day-limit',
     {'type' : 'int',
      'default': 3,
      'help': 'Number of days to be used for the startup view.',
      'group': 'semnews', 'level': 2,
      }),
    ('startup-influent-limit',
     {'type' : 'int',
      'default': 12,
      'help': 'Number of influent entities to be shown in startup page.',
      'group': 'semnews', 'level': 2,
      }),
    ('semnews-lexicon-file',
     {'type' : 'string',
      'help': 'A file to be used for lexicon creation, tab separated (url, name).',
      'group': 'semnews', 'level': 1,
      }),
    ('nerdy-at-insertion',
     {'type': 'yn',
      'default' : False,
      'help': 'process nerdy at insertion',
      'group' : 'semnews', 'level': 1,
      }),
    )
