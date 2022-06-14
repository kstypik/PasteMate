# Generated by Django 4.0.5 on 2022-06-14 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0018_alter_folder_options_alter_folder_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='paste',
            name='filesize',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paste',
            name='syntax',
            field=models.CharField(choices=[('text', 'Text only'), ('Popular languages', (('bash', 'Bash'), ('c', 'C'), ('csharp', 'C#'), ('cpp', 'C++'), ('css', 'CSS'), ('html', 'HTML'), ('json', 'JSON'), ('java', 'Java'), ('javascript', 'JavaScript'), ('lua', 'Lua'), ('markdown', 'Markdown'), ('objective-c', 'Objective C'), ('php', 'PHP'), ('python', 'Python'), ('ruby', 'Ruby'))), ('All languages', [('abap', 'ABAP'), ('amdgpu', 'AMDGPU'), ('apl', 'APL'), ('abnf', 'ABNF'), ('actionscript3', 'ActionScript 3'), ('actionscript', 'ActionScript'), ('ada', 'Ada'), ('adl', 'ADL'), ('agda', 'Agda'), ('aheui', 'Aheui'), ('alloy', 'Alloy'), ('ambienttalk', 'AmbientTalk'), ('ampl', 'Ampl'), ('html+ng2', 'HTML + Angular2'), ('ng2', 'Angular2'), ('antlr-actionscript', 'ANTLR With ActionScript Target'), ('antlr-csharp', 'ANTLR With C# Target'), ('antlr-cpp', 'ANTLR With CPP Target'), ('antlr-java', 'ANTLR With Java Target'), ('antlr', 'ANTLR'), ('antlr-objc', 'ANTLR With ObjectiveC Target'), ('antlr-perl', 'ANTLR With Perl Target'), ('antlr-python', 'ANTLR With Python Target'), ('antlr-ruby', 'ANTLR With Ruby Target'), ('apacheconf', 'ApacheConf'), ('applescript', 'AppleScript'), ('arduino', 'Arduino'), ('arrow', 'Arrow'), ('asc', 'ASCII armored'), ('aspectj', 'AspectJ'), ('asymptote', 'Asymptote'), ('augeas', 'Augeas'), ('autoit', 'AutoIt'), ('autohotkey', 'autohotkey'), ('awk', 'Awk'), ('bbcbasic', 'BBC Basic'), ('bbcode', 'BBCode'), ('bc', 'BC'), ('bst', 'BST'), ('bare', 'BARE'), ('basemake', 'Base Makefile'), ('bash', 'Bash'), ('console', 'Bash Session'), ('batch', 'Batchfile'), ('bdd', 'Bdd'), ('befunge', 'Befunge'), ('berry', 'Berry'), ('bibtex', 'BibTeX'), ('blitzbasic', 'BlitzBasic'), ('blitzmax', 'BlitzMax'), ('bnf', 'BNF'), ('boa', 'Boa'), ('boo', 'Boo'), ('boogie', 'Boogie'), ('brainfuck', 'Brainfuck'), ('bugs', 'BUGS'), ('camkes', 'CAmkES'), ('c', 'C'), ('cmake', 'CMake'), ('c-objdump', 'c-objdump'), ('cpsa', 'CPSA'), ('css+ul4', 'CSS+UL4'), ('aspx-cs', 'aspx-cs'), ('csharp', 'C#'), ('ca65', 'ca65 assembler'), ('cadl', 'cADL'), ('capdl', 'CapDL'), ('capnp', "Cap'n Proto"), ('cbmbas', 'CBM BASIC V2'), ('cddl', 'CDDL'), ('ceylon', 'Ceylon'), ('cfengine3', 'CFEngine3'), ('chaiscript', 'ChaiScript'), ('chapel', 'Chapel'), ('charmci', 'Charmci'), ('html+cheetah', 'HTML+Cheetah'), ('javascript+cheetah', 'JavaScript+Cheetah'), ('cheetah', 'Cheetah'), ('xml+cheetah', 'XML+Cheetah'), ('cirru', 'Cirru'), ('clay', 'Clay'), ('clean', 'Clean'), ('clojure', 'Clojure'), ('clojurescript', 'ClojureScript'), ('cobolfree', 'COBOLFree'), ('cobol', 'COBOL'), ('coffeescript', 'CoffeeScript'), ('cfc', 'Coldfusion CFC'), ('cfm', 'Coldfusion HTML'), ('cfs', 'cfstatement'), ('common-lisp', 'Common Lisp'), ('componentpascal', 'Component Pascal'), ('coq', 'Coq'), ('cplint', 'cplint'), ('cpp', 'C++'), ('cpp-objdump', 'cpp-objdump'), ('crmsh', 'Crmsh'), ('croc', 'Croc'), ('cryptol', 'Cryptol'), ('cr', 'Crystal'), ('csound-document', 'Csound Document'), ('csound', 'Csound Orchestra'), ('csound-score', 'Csound Score'), ('css+django', 'CSS+Django/Jinja'), ('css+ruby', 'CSS+Ruby'), ('css+genshitext', 'CSS+Genshi Text'), ('css', 'CSS'), ('css+php', 'CSS+PHP'), ('css+smarty', 'CSS+Smarty'), ('cuda', 'CUDA'), ('cypher', 'Cypher'), ('cython', 'Cython'), ('d', 'D'), ('d-objdump', 'd-objdump'), ('dpatch', 'Darcs Patch'), ('dart', 'Dart'), ('dasm16', 'DASM16'), ('debcontrol', 'Debian Control file'), ('delphi', 'Delphi'), ('devicetree', 'Devicetree'), ('dg', 'dg'), ('diff', 'Diff'), ('django', 'Django/Jinja'), ('docker', 'Docker'), ('dtd', 'DTD'), ('duel', 'Duel'), ('dylan-console', 'Dylan session'), ('dylan', 'Dylan'), ('dylan-lid', 'DylanLID'), ('ecl', 'ECL'), ('ec', 'eC'), ('earl-grey', 'Earl Grey'), ('easytrieve', 'Easytrieve'), ('ebnf', 'EBNF'), ('eiffel', 'Eiffel'), ('iex', 'Elixir iex session'), ('elixir', 'Elixir'), ('elm', 'Elm'), ('elpi', 'Elpi'), ('emacs-lisp', 'EmacsLisp'), ('email', 'E-mail'), ('erb', 'ERB'), ('erlang', 'Erlang'), ('erl', 'Erlang erl session'), ('html+evoque', 'HTML+Evoque'), ('evoque', 'Evoque'), ('xml+evoque', 'XML+Evoque'), ('execline', 'execline'), ('ezhil', 'Ezhil'), ('fsharp', 'F#'), ('fstar', 'FStar'), ('factor', 'Factor'), ('fancy', 'Fancy'), ('fan', 'Fantom'), ('felix', 'Felix'), ('fennel', 'Fennel'), ('fish', 'Fish'), ('flatline', 'Flatline'), ('floscript', 'FloScript'), ('forth', 'Forth'), ('fortranfixed', 'FortranFixed'), ('fortran', 'Fortran'), ('foxpro', 'FoxPro'), ('freefem', 'Freefem'), ('futhark', 'Futhark'), ('gap', 'GAP'), ('gdscript', 'GDScript'), ('glsl', 'GLSL'), ('gsql', 'GSQL'), ('gas', 'GAS'), ('gcode', 'g-code'), ('genshi', 'Genshi'), ('genshitext', 'Genshi Text'), ('pot', 'Gettext Catalog'), ('gherkin', 'Gherkin'), ('gnuplot', 'Gnuplot'), ('go', 'Go'), ('golo', 'Golo'), ('gooddata-cl', 'GoodData-CL'), ('gosu', 'Gosu'), ('gst', 'Gosu Template'), ('graphviz', 'Graphviz'), ('groff', 'Groff'), ('groovy', 'Groovy'), ('hlsl', 'HLSL'), ('html+ul4', 'HTML+UL4'), ('haml', 'Haml'), ('html+handlebars', 'HTML+Handlebars'), ('handlebars', 'Handlebars'), ('haskell', 'Haskell'), ('haxe', 'Haxe'), ('hexdump', 'Hexdump'), ('hsail', 'HSAIL'), ('hspec', 'Hspec'), ('html+django', 'HTML+Django/Jinja'), ('html+genshi', 'HTML+Genshi'), ('html', 'HTML'), ('html+php', 'HTML+PHP'), ('html+smarty', 'HTML+Smarty'), ('http', 'HTTP'), ('haxeml', 'Hxml'), ('hylang', 'Hy'), ('hybris', 'Hybris'), ('idl', 'IDL'), ('icon', 'Icon'), ('idris', 'Idris'), ('igor', 'Igor'), ('inform6', 'Inform 6'), ('i6t', 'Inform 6 template'), ('inform7', 'Inform 7'), ('ini', 'INI'), ('io', 'Io'), ('ioke', 'Ioke'), ('irc', 'IRC logs'), ('isabelle', 'Isabelle'), ('j', 'J'), ('jslt', 'JSLT'), ('jags', 'JAGS'), ('jasmin', 'Jasmin'), ('java', 'Java'), ('javascript+django', 'JavaScript+Django/Jinja'), ('javascript+ruby', 'JavaScript+Ruby'), ('js+genshitext', 'JavaScript+Genshi Text'), ('javascript', 'JavaScript'), ('javascript+php', 'JavaScript+PHP'), ('javascript+smarty', 'JavaScript+Smarty'), ('js+ul4', 'Javascript+UL4'), ('jcl', 'JCL'), ('jsgf', 'JSGF'), ('jsonld', 'JSON-LD'), ('json', 'JSON'), ('jsp', 'Java Server Page'), ('jlcon', 'Julia console'), ('julia', 'Julia'), ('juttle', 'Juttle'), ('k', 'K'), ('kal', 'Kal'), ('kconfig', 'Kconfig'), ('kmsg', 'Kernel log'), ('koka', 'Koka'), ('kotlin', 'Kotlin'), ('kuin', 'Kuin'), ('lsl', 'LSL'), ('css+lasso', 'CSS+Lasso'), ('html+lasso', 'HTML+Lasso'), ('javascript+lasso', 'JavaScript+Lasso'), ('lasso', 'Lasso'), ('xml+lasso', 'XML+Lasso'), ('lean', 'Lean'), ('less', 'LessCss'), ('lighttpd', 'Lighttpd configuration file'), ('lilypond', 'LilyPond'), ('limbo', 'Limbo'), ('liquid', 'liquid'), ('literate-agda', 'Literate Agda'), ('literate-cryptol', 'Literate Cryptol'), ('literate-haskell', 'Literate Haskell'), ('literate-idris', 'Literate Idris'), ('livescript', 'LiveScript'), ('llvm', 'LLVM'), ('llvm-mir-body', 'LLVM-MIR Body'), ('llvm-mir', 'LLVM-MIR'), ('logos', 'Logos'), ('logtalk', 'Logtalk'), ('lua', 'Lua'), ('mcfunction', 'MCFunction'), ('mime', 'MIME'), ('moocode', 'MOOCode'), ('doscon', 'MSDOS Session'), ('macaulay2', 'Macaulay2'), ('make', 'Makefile'), ('css+mako', 'CSS+Mako'), ('html+mako', 'HTML+Mako'), ('javascript+mako', 'JavaScript+Mako'), ('mako', 'Mako'), ('xml+mako', 'XML+Mako'), ('maql', 'MAQL'), ('markdown', 'Markdown'), ('mask', 'Mask'), ('mason', 'Mason'), ('mathematica', 'Mathematica'), ('matlab', 'Matlab'), ('matlabsession', 'Matlab session'), ('maxima', 'Maxima'), ('meson', 'Meson'), ('minid', 'MiniD'), ('miniscript', 'MiniScript'), ('modelica', 'Modelica'), ('modula2', 'Modula-2'), ('trac-wiki', 'MoinMoin/Trac Wiki markup'), ('monkey', 'Monkey'), ('monte', 'Monte'), ('moonscript', 'MoonScript'), ('mosel', 'Mosel'), ('css+mozpreproc', 'CSS+mozpreproc'), ('mozhashpreproc', 'mozhashpreproc'), ('javascript+mozpreproc', 'Javascript+mozpreproc'), ('mozpercentpreproc', 'mozpercentpreproc'), ('xul+mozpreproc', 'XUL+mozpreproc'), ('mql', 'MQL'), ('mscgen', 'Mscgen'), ('mupad', 'MuPAD'), ('mxml', 'MXML'), ('mysql', 'MySQL'), ('css+myghty', 'CSS+Myghty'), ('html+myghty', 'HTML+Myghty'), ('javascript+myghty', 'JavaScript+Myghty'), ('myghty', 'Myghty'), ('xml+myghty', 'XML+Myghty'), ('ncl', 'NCL'), ('nsis', 'NSIS'), ('nasm', 'NASM'), ('objdump-nasm', 'objdump-nasm'), ('nemerle', 'Nemerle'), ('nesc', 'nesC'), ('nestedtext', 'NestedText'), ('newlisp', 'NewLisp'), ('newspeak', 'Newspeak'), ('nginx', 'Nginx configuration file'), ('nimrod', 'Nimrod'), ('nit', 'Nit'), ('nixos', 'Nix'), ('nodejsrepl', 'Node.js REPL console session'), ('notmuch', 'Notmuch'), ('nusmv', 'NuSMV'), ('numpy', 'NumPy'), ('objdump', 'objdump'), ('objective-c', 'Objective-C'), ('objective-c++', 'Objective-C++'), ('objective-j', 'Objective-J'), ('ocaml', 'OCaml'), ('octave', 'Octave'), ('odin', 'ODIN'), ('omg-idl', 'OMG Interface Definition Language'), ('ooc', 'Ooc'), ('opa', 'Opa'), ('openedge', 'OpenEdge ABL'), ('output', 'Text output'), ('pacmanconf', 'PacmanConf'), ('pan', 'Pan'), ('parasail', 'ParaSail'), ('pawn', 'Pawn'), ('peg', 'PEG'), ('perl6', 'Perl6'), ('perl', 'Perl'), ('php', 'PHP'), ('pig', 'Pig'), ('pike', 'Pike'), ('pkgconfig', 'PkgConfig'), ('plpgsql', 'PL/pgSQL'), ('pointless', 'Pointless'), ('pony', 'Pony'), ('postscript', 'PostScript'), ('psql', 'PostgreSQL console (psql)'), ('postgresql', 'PostgreSQL SQL dialect'), ('pov', 'POVRay'), ('powershell', 'PowerShell'), ('pwsh-session', 'PowerShell Session'), ('praat', 'Praat'), ('procfile', 'Procfile'), ('prolog', 'Prolog'), ('promql', 'PromQL'), ('properties', 'Properties'), ('protobuf', 'Protocol Buffer'), ('psysh', 'PsySH console session for PHP'), ('pug', 'Pug'), ('puppet', 'Puppet'), ('pypylog', 'PyPy Log'), ('python2', 'Python 2.x'), ('py2tb', 'Python 2.x Traceback'), ('pycon', 'Python console session'), ('python', 'Python'), ('pytb', 'Python Traceback'), ('py+ul4', 'Python+UL4'), ('qbasic', 'QBasic'), ('q', 'Q'), ('qvto', 'QVTO'), ('qlik', 'Qlik'), ('qml', 'QML'), ('rconsole', 'RConsole'), ('rng-compact', 'Relax-NG Compact'), ('spec', 'RPMSpec'), ('racket', 'Racket'), ('ragel-c', 'Ragel in C Host'), ('ragel-cpp', 'Ragel in CPP Host'), ('ragel-d', 'Ragel in D Host'), ('ragel-em', 'Embedded Ragel'), ('ragel-java', 'Ragel in Java Host'), ('ragel', 'Ragel'), ('ragel-objc', 'Ragel in Objective C Host'), ('ragel-ruby', 'Ragel in Ruby Host'), ('rd', 'Rd'), ('reasonml', 'ReasonML'), ('rebol', 'REBOL'), ('red', 'Red'), ('redcode', 'Redcode'), ('registry', 'reg'), ('resourcebundle', 'ResourceBundle'), ('rexx', 'Rexx'), ('rhtml', 'RHTML'), ('ride', 'Ride'), ('rita', 'Rita'), ('roboconf-graph', 'Roboconf Graph'), ('roboconf-instances', 'Roboconf Instances'), ('robotframework', 'RobotFramework'), ('rql', 'RQL'), ('rsl', 'RSL'), ('restructuredtext', 'reStructuredText'), ('trafficscript', 'TrafficScript'), ('rbcon', 'Ruby irb session'), ('ruby', 'Ruby'), ('rust', 'Rust'), ('sas', 'SAS'), ('splus', 'S'), ('sml', 'Standard ML'), ('snbt', 'SNBT'), ('sarl', 'SARL'), ('sass', 'Sass'), ('savi', 'Savi'), ('scala', 'Scala'), ('scaml', 'Scaml'), ('scdoc', 'scdoc'), ('scheme', 'Scheme'), ('scilab', 'Scilab'), ('scss', 'SCSS'), ('sed', 'Sed'), ('shexc', 'ShExC'), ('shen', 'Shen'), ('sieve', 'Sieve'), ('silver', 'Silver'), ('singularity', 'Singularity'), ('slash', 'Slash'), ('slim', 'Slim'), ('slurm', 'Slurm'), ('smali', 'Smali'), ('smalltalk', 'Smalltalk'), ('sgf', 'SmartGameFormat'), ('smarty', 'Smarty'), ('smithy', 'Smithy'), ('snobol', 'Snobol'), ('snowball', 'Snowball'), ('solidity', 'Solidity'), ('sophia', 'Sophia'), ('sp', 'SourcePawn'), ('debsources', 'Debian Sourcelist'), ('sparql', 'SPARQL'), ('spice', 'Spice'), ('sql', 'SQL'), ('sqlite3', 'sqlite3con'), ('squidconf', 'SquidConf'), ('srcinfo', 'Srcinfo'), ('ssp', 'Scalate Server Page'), ('stan', 'Stan'), ('stata', 'Stata'), ('supercollider', 'SuperCollider'), ('swift', 'Swift'), ('swig', 'SWIG'), ('systemverilog', 'systemverilog'), ('tap', 'TAP'), ('tnt', 'Typographic Number Theory'), ('toml', 'TOML'), ('tads3', 'TADS 3'), ('tal', 'Tal'), ('tasm', 'TASM'), ('tcl', 'Tcl'), ('tcsh', 'Tcsh'), ('tcshcon', 'Tcsh Session'), ('tea', 'Tea'), ('teal', 'teal'), ('teratermmacro', 'Tera Term macro'), ('termcap', 'Termcap'), ('terminfo', 'Terminfo'), ('terraform', 'Terraform'), ('tex', 'TeX'), ('ti', 'ThingsDB'), ('thrift', 'Thrift'), ('tid', 'tiddler'), ('todotxt', 'Todotxt'), ('tsql', 'Transact-SQL'), ('treetop', 'Treetop'), ('turtle', 'Turtle'), ('html+twig', 'HTML+Twig'), ('twig', 'Twig'), ('typescript', 'TypeScript'), ('typoscriptcssdata', 'TypoScriptCssData'), ('typoscripthtmldata', 'TypoScriptHtmlData'), ('typoscript', 'TypoScript'), ('ul4', 'UL4'), ('ucode', 'ucode'), ('unicon', 'Unicon'), ('unixconfig', 'Unix/Linux config files'), ('urbiscript', 'UrbiScript'), ('usd', 'USD'), ('vbscript', 'VBScript'), ('vcl', 'VCL'), ('vclsnippets', 'VCLSnippets'), ('vctreestatus', 'VCTreeStatus'), ('vgl', 'VGL'), ('vala', 'Vala'), ('aspx-vb', 'aspx-vb'), ('vb.net', 'VB.net'), ('html+velocity', 'HTML+Velocity'), ('velocity', 'Velocity'), ('xml+velocity', 'XML+Velocity'), ('verilog', 'verilog'), ('vhdl', 'vhdl'), ('vim', 'VimL'), ('wdiff', 'WDiff'), ('wast', 'WebAssembly'), ('webidl', 'Web IDL'), ('whiley', 'Whiley'), ('x10', 'X10'), ('xml+ul4', 'XML+UL4'), ('xquery', 'XQuery'), ('xml+django', 'XML+Django/Jinja'), ('xml+ruby', 'XML+Ruby'), ('xml', 'XML'), ('xml+php', 'XML+PHP'), ('xml+smarty', 'XML+Smarty'), ('xorg.conf', 'Xorg'), ('xslt', 'XSLT'), ('xtend', 'Xtend'), ('extempore', 'xtlang'), ('yaml+jinja', 'YAML+Jinja'), ('yaml', 'YAML'), ('yang', 'YANG'), ('zeek', 'Zeek'), ('zephir', 'Zephir'), ('zig', 'Zig'), ('ansys', 'ANSYS parametric design language')])], default='text', max_length=50),
        ),
    ]
