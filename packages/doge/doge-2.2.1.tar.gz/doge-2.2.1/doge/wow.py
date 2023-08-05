"""
Words and static data

Please extend this file with more lvl=100 shibe wow.

"""


KNOWN_PROCESSES = (
    # wow shells and terminals and etc
    'urxvt', 'tmux', 'fish', 'ssh', 'mutt', 'screen', 'mosh-client',
    'Terminal', 'sh', 'bash', 'zsh', 'tcsh', 'csh',

    # pretty browsers
    'chromium', 'luakit', 'uzbl-core', 'firefox', 'jumanji', 'chrome',
    'thunderbird', 'Safari', 'Google Chrome', 'iceweasel',

    # many wms
    'awesome', 'beryl', 'blackbox', 'bspwm', 'compiz', 'dwm',
    'enlightenment', 'herbstluftwm', 'fluxbox', 'fvwm', 'i3', 'icewm',
    'kwin', 'metacity', 'musca', 'openbox', 'pekwm', 'ratpoison',
    'scrotwm', 'wmaker', 'wmfs', 'wmii', 'xfwm4', 'xmonad',
    'gnome-shell', 'devilspie2',

    # such services and daemons
    'mpd', 'nginx', 'dzen2', 'systemd', 'lighttpd', 'prosody',
    'mongod', 'postgres', 'mysqld', 'redis-server', 'php-fpm',
    'sendmail', 'irssi', 'screen', 'neo4j', 'httpd', 'Flux', 'Dropbox',
    'VirtualBox', 'VirtualBoxVM', 'tmux', 'xflux', 'weechat', 'xen',
    'apache', 'sshd',

    # programming languages
    'ruby', 'python', 'java', 'php', 'node', 'erlang', 'perl',

    # so editors
    'emacs', 'vim', 'nano', 'gedit', 'sublime_text', 'subl',

    # very talk
    'HipChat', 'Mail',

    # wow cluster
    'pbs_sched', 'pbs_mom', 'mpirun', 'sgeexecd', 'slurmd',
)

PREFIXES = (
    'wow', 'such', 'very', 'so much', 'many', 'lol', 'beautiful',
    'all the', 'the', 'most', 'very much', 'pretty', 'so',
)

# Please keep in mind that this particular shibe is a terminal hax0r shibe,
# and the words added should be in that domain
WORDS = (
    'computer', 'hax0r', 'code', 'data', 'internet', 'server',
    'hacker', 'terminal', 'doge', 'shibe', 'program', 'free software',
    'web scale', 'monads', 'git', 'daemon', 'loop', 'pretty', 'uptime',
    'thread safe', 'posix',
)

SUFFIXES = (
    'wow', 'lol', 'hax', 'plz', 'lvl=100'
)

# A subset of the 255 color cube with the darkest colors removed. This is
# suited for use on dark terminals. Lighter colors are still present so some
# colors might be semi-unreadabe on lighter backgrounds.
#
# If you see this and use a light terminal, a pull request with a set that
# works well on a light terminal would be awesome.
COLORS = (
    23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 41, 42, 43,
    44, 45, 47, 48, 49, 50, 51, 58, 59, 63, 64, 65, 66, 67, 68, 69, 70, 71,
    72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 94,
    95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
    110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
    130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143,
    144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157,
    158, 159, 162, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176,
    177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190,
    191, 192, 193, 194, 195, 197, 202, 203, 204, 205, 206, 207, 208, 209,
    210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223,
    224, 225, 226, 227, 228
)

# Seasonal greetings by Shibe.
# Keys for this dictionary are tuples with start and end dates for the holiday.
# Tuple for every single date is in (month, day) format (year is discarded).
# Doge checks if current date falls in between these dates and show wow
# congratulations, so do whatever complex math you need to make sure Shibe
# celebrates with you!
SEASONS = {
    ((12, 14), (12, 26)): {
        'pic': 'static/doge-xmas.txt',
        'words': (
            'christmas', 'xmas', 'candles', 'santa', 'merry', 'reindeers',
            'gifts', 'jul', 'vacation', 'carol',
        )
    },

    # To be continued...
}
