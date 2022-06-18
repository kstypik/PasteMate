from pygments import lexers

PUBLIC = "PU", "Public"
UNLISTED = "UN", "Unlisted"
PRIVATE = "PR", "Private"

NEVER = ""
NO_CHANGE = "PRE"
TEN_MINUTES = "10M"
ONE_HOUR = "1H"
ONE_DAY = "1D"
ONE_WEEK = "1W"
TWO_WEEKS = "2W"
ONE_MONTH = "1m"
SIX_MONTHS = "6M"
ONE_YEAR = "1Y"

SYNTAX_HIGHLITHING_CHOICES = (
    ("text", "Text only"),
    (
        "Popular languages",
        (
            ("bash", "Bash"),
            ("c", "C"),
            ("csharp", "C#"),
            ("cpp", "C++"),
            ("css", "CSS"),
            ("html", "HTML"),
            ("json", "JSON"),
            ("java", "Java"),
            ("javascript", "JavaScript"),
            ("lua", "Lua"),
            ("markdown", "Markdown"),
            ("objective-c", "Objective C"),
            ("php", "PHP"),
            ("python", "Python"),
            ("ruby", "Ruby"),
        ),
    ),
    (
        "All languages",
        [
            (lexer[1][0], lexer[0])
            for lexer in lexers.get_all_lexers()
            if lexer[1] and lexer[0] != "Text only"
        ],
    ),
)
