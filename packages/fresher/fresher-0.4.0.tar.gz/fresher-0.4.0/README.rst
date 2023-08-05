Fresher
=======

Fresher is a fork of Freshen. As of Fall of 2013, Freshen appeared to
no longer being maintained, so I decided to fork and make some much
needed changes.

Differences from Freshen:

* Fresher is tested against Python 3.3, Python 2.7 and Python 2.6. (It
  seems Freshen was tested against whatever Python happened to be
  around. It definitely did not work on Python 3.)

* The file to get Fresher to ignore a directory is ``.fresherignore``.

* All arguments that are specific to Fresher begins with ``--fresher-`` so:

  - ``--tags`` is now ``--fresher-tags``
  - ``--language`` is now ``--fresher-language``
  - ``--list-undefined`` is now ``--fresher-list-undefined``

  This change allows using fresher and freshen together in the same
  installation, and reduces the chances of conflicts with other nose
  plugins in the future.

* Undefined steps are fatal errors unless you pass --fresher-allow-undefined.

* Freshen would load steps files under fake module names. Fresher
  loads the whole shebang under ``freshen.steps``.

.. warning:: Do not have a steps module loaded by Fresher also be
             loaded by no-step modules.  (A no-step module is one which
             does not implement steps). Here's a scenario where you
             could run into trouble: module A ``features/steps`` loads
             module B ``features/util`` (a nostep module) which loads
             module C ``features/nested/steps`` which is also a steps
             module for another set of features. We could call this an
             S-N-S scenario (steps, no-step, steps). If you do this
             then module C will be loaded twice: once because module B
             imports it and a second time when fresher finds it is
             needed for some features in the ``nested``
             subdirectory. It will be loaded as *two different
             modules*. If the duplicated module maintains no state,
             you'll only incur the cost of loading the same module
             twice. However, if it does maintain state, then good
             luck.

             Note that Freshen 0.2 also suffers from this problem due
             to the fake module names it uses. I believe behave 1.2.3
             also suffers from this problem. It uses ``exec`` to load
             step definition files. In an S-N-S case like the one
             above, module A will be exec'ed, and module B will import
             module C so module C will show as an actual Python
             module. Then when behave determines that C is needed for
             step definitions, it will exec it, thereby loading it
             again.

             It is completely fine if a steps module or package loads
             a non-steps module or package. It is highly recommended
             to separate step definitions from broader logic.

* Fresher allows duplicate function names for steps.

* Fresher associates with a package the steps defined by all the
  **modules** that are its **immediate** children. Imagine the
  following structure::

    steps/
          __init__.py
          caret.py
          selection.py
          nested/
               __init__.py
               log.py
               data.py

  When this ``steps`` package is loaded by Fresher, all of the steps
  found in ``caret.py`` and ``selection.py`` will be immediately
  accessible. **There is no need to refer to these modules
  individually or to add anything to the ``steps/__init__.py``
  file. However, what is in the **subpackage** named ``steps.nested``
  will not be accessible until ``steps.nested`` is itself loaded by
  Fresher.

  With Freshen ``steps/__init__.py`` would require::

    from .caret import *
    from .selection import *

  but this is *not* required when using Fresher.

* Generally speaking, the ``from ... import *`` method of making steps
  accessible in another module, which worked fine in Freshen, does not
  work in Fresher. It worked in Freshen because Freshen would
  determine the steps defined in a module by scanning the module's
  *global symbols*. This cannot work with Fresher because it allows
  duplicate function names. (If ``@given('a')`` and ``@given('b')``
  both decorate ``foo()`` the symbol ``foo`` is still present only
  once.)

  You have to use ``fresher.stepregistry.import_steps()`` to import
  the steps from another module. For instance::

    from freshen.stepregistry import import_steps

    import_steps(".defs")

  Or if you want to import steps from a more remote location (actual
  case in the test suite)::

    from freshen.stepregistry import import_steps

    import_steps("..nested.steps")

The old documentation follows. Keep in mind the differences
above. Eventually, this will all be rewritten for Fresher.

Freshen
=======

- Freshen is an acceptance testing framework for Python.
- It is built as a plugin for Nose_.
- It uses the (mostly) same syntax as Cucumber_.

What's New in Version 0.2?
--------------------------

- Freshen now supports Backgrounds_ for a feature.
- Freshen now supports the **But** keyword for steps of Scenarios_.
- Freshen now supports the simple case of `Step Argument Transforms`_.
- The parser now supports several natural language aliases for a keyword.
- If a natural language translation is not found for a keyword, English will be used.
- "@After" hooks are now run in the *opposite* order of which they are registered.
- Improved error handling and reporting.

There are also some modifications that are incompatible with Cucumber.

- Only the step definition module named "steps" is used by default.
- Users can override this behavior with the "Use step definitions from" keyword.
- Freshen distinguishes "Given" steps from "When" steps and "Then" steps.

----------------------------------------------------------------------

Freshen Documentation
=====================

Most of the information shown here can also be found on the `Cucumber wiki`_, but here it is anyway:

Freshen tests are composed of two parts: `feature outlines`_ and `step definitions`_.


Feature outlines
----------------

Feature outlines are text files with a ``.feature`` extension. The purpose of this file is to
describe a feature in plain text understandable by a non-technical person such as a product manager
or user. However, these files are specially formatted and are parsed by Freshen in order to execute
real tests.

You can put your feature files anywhere you want in the source tree of your project, but it is
recommended to place them in a dedicated "features" directory.

A feature file contains (in this order):

- the step definition modules to use (*optional*, see `specifying step definition modules`_);
- the feature name with a free-form text description;
- a background (*optional*, see `backgrounds`_);
- one or more `scenarios`_ or `scenario outlines`_.


Scenarios
---------

A scenario is an example of an interaction a user would have as part of the feature. It is comprised
of a series of *steps*. Each step has to start with a keyword: **Given**, **When**, **Then**, **But** or **And**.
Here's an example for a calculator application (this example is included in the `source code`_)::

    Scenario: Divide regular numbers
      Given I have entered 3 into the calculator
      And I have entered 2 into the calculator
      When I press divide
      Then the result should be 1.5 on the screen


Scenario Outlines
-----------------

Sometimes it is useful to parametrize a scenario and run it multiple times, substituting values. For
this purpose, use *scenario outlines*. The format is the same as a scenario, except you can indicate
places where a value should be substituted using angle brackets: < and >. You specify the values
to be substituted using an "Examples" section that follows the scenario outline::

    Scenario Outline: Add two numbers
      Given I have entered <input_1> into the calculator
      And I have entered <input_2> into the calculator
      When I press <button>
      Then the result should be <output> on the screen

    Examples:
      | input_1 | input_2 | button | output |
      | 20      | 30      | add    | 50     |
      | 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |

In this case, the scenario will be executed once for each row in the table (except the first row,
which indicates which variable to substitute for).


Backgrounds
-----------

A feature may contain a background. It allows you to *add some context to the scenarios*
in the current feature. A Background is much like a scenario containing a number of steps.
The difference is when it is run.
*The background is run before each of your scenarios but after any of your "@Before" hooks.*

Here is an example::

    Feature: Befriending
      In order to have some friends
      As a Facebook user
      I want to be able to manage my list of friends

      Background:
        Given I am the user Ken
        And I have friends Barbie, Cloe

      Scenario: Adding a new friend
        When I add a new friend named Jade
        Then I should have friends Barbie, Cloe, Jade

      Scenario: Removing a friend
        When I remove my friend Cloe
        Then I should have friends Barbie

*Note that background should be added in a feature only if it has a value for the client.*
Otherwise, you can use tagged hooks (see Tags_ and Hooks_).


Step Definitions
----------------

When presented with a feature file, Freshen will execute each scenario. This involves iterating
over each step in turn and executing its *step definition*. Step definitions are python functions
adorned with a special decorator. Freshen knows which step definition function to execute by
matching the step's text against a regular expression associated with the definition. Here's an
example of a step definition file, which hopefully illustrates this point::

    from freshen import *

    import calculator

    @Before
    def before(sc):
        scc.calc = calculator.Calculator()
        scc.result = None

    @Given("I have entered (\d+) into the calculator")
    def enter(num):
        scc.calc.push(int(num))

    @When("I press (\w+)")
    def press(button):
        op = getattr(scc.calc, button)
        scc.result = op()

    @Then("the result should be (.*) on the screen")
    def check_result(value):
        assert_equal(str(scc.result), value)

In this example, you see a few step definitions, as well as a hook. Any captures (bits inside the
parentheses) from the regular expression are passed to the step definition function as arguments.


Specifying Step Definition Modules
-----------------------------------

Step definitions are defined in python modules. By default, Freshen will try to load
a module named "steps" from the same directory as the ``.feature`` file. If that is not the
desired behavior, you can also explicitly specify which step definition modules to use
for a feature. To do this, use the keyword ``Using step definitions from``
(or its abbreviation: ``Using steps``) and specify which step definition modules you
want to use. Each module name must be a quoted string and must be relative to the
location of the feature file. You can specify one or more module names (they must be
separated by commas).

Here is an example::

    Using step definitions from: 'steps', 'step/page_steps'

    Feature: Destroy a document
      In order to take out one's anger on a document
      As an unsatisfied reader
      I want to be able to rip off the pages of the document

      Scenario: Rip off a page
        Given a document of 5 pages
        And the page is 3
        When I rip off the current page
        Then the page is 3
        But the document has 4 pages

Although you have the opportunity to explicitly specify the step definition modules to use in Freshen,
this is not a reason to fall into the `Feature-Coupled Steps Antipattern`_!

A step definition module can import other step definition modules. When doing this,
the actual step definition functions must be at the top level. For example::

    from other_step_module import *

A step definition module can be a python package, as long as all the relevant functions are imported
into ``__init__.py``.

The python path will automatically include the current working directory and the
directory of the ``.feature`` file.


Hooks
-----

It is often useful to do some work before each step or each scenario is executed. For this purpose,
you can make use of *hooks*. Identify them for Freshen by adorning them with "@Before", "@After"
(run before or after each scenario), or "@AfterStep" which is run after each step.


Context storage
---------------

Since the execution of each scenario is broken up between multiple step functions, it is often
necessary to share information between steps. It is possible to do this using global variables in
the step definition modules but, if you dislike that approach, Freshen provides three global
storage areas which can be imported from the `freshen` module. They are:

- ``glc``: Global context, never cleared - same as using a global variable
- ``ftc``: Feature context, cleared at the start of each feature
- ``scc``: Scenario context, cleared at the start of each scenario

These objects are built to mimic a JavaScript/Lua-like table, where fields can be accessed with
either the square bracket notation, or the attribute notation. They do not complain when a key
is missing::

    glc.stuff == gcc['stuff']  => True
    glc.doesnotexist           => None

Running steps from within step definitions
------------------------------------------

You can call out to a step definition from within another step using the same notation used in
feature files. To do this, use the ``run_steps`` function::

    @Given('I do thing A')
    def do_a():
        #Do something useful.
        pass

    @Given('I have B')
    def having_b():
        #Do something useful.
        pass

    @Given('I do something that use both')
    def use_both():
        run_steps("""
                  Given I do thing A
                  And I have B
                  """)


Multi-line arguments
--------------------

Steps can have two types of multi-line arguments: multi-line strings and tables. Multi-line strings
look like Python docstrings, starting and terminating with three double quotes: ``"""``.

Tables look like the ones in the example section in scenario outlines. They are comprised of a
header and one or more rows. Fields are delimited using a pipe: ``|``.

Both tables and multi-line strings should be placed on the line following the step.

They will be passed to the step definition as the first argument. Strings are presented as regular
Python strings, whereas tables come across as a ``Table`` object. To get the rows, call
``table.iterrows()``.


Tags
----

A feature or scenario can be adorned with one or more tags. This helps classify features and
scenarios to the reader. Freshen makes use of tags in two ways. The first is by allowing selective
execution via the command line - this is described below. The second is by allowing `hooks`_ to be
executed selectively. A partial example::

    >> feature:

    @needs_tmp_file
    Scenario: A scenario that needs a temporary file
        Given ...
        When ...

    >> step definition:

    @Before("@needs_tmp_file")
    def needs_tmp_file(sc):
        make_tmp_file()


Step Argument Transforms
------------------------

Step definitions are specified as regular expressions. Freshen will pass any
captured sub-expressions (i.e. the parts in parentheses) to the step definition
function as a string. However, it is often necessary to convert those strings
into another type of object. For example, in the step::

    Then user bob should be friends with user adelaide

we may need to convert "user bob" to the the object User(name='bob') and
"user adelaide" to User(name="adelaide"). To do this repeatedly would break
the "Do Not Repeat Yourself (DRY)" principle of good software development. Step
Argument Transforms allow you to specify an automatic transformation for
arguments if they match a certain regular expression. These transforms are
created in the step definition file. For example::

    @Transform(r"^user (\w+)$")
    def transform_user(name):
        return User.objects.find(name)

    @Then(r"^(user \w+) should be friends with (user \w+)")
    def check_friends(user1, user2):
        # Here the arguments will already be User objects
        assert user1.is_friends_with(user2)

The two arguments to the "Then" step will be matched in the transform above
and converted into a User object before being passed to the step definition.

Named Step Argument Transformation
----------------------------------

Another imperfection of step definitions from the DRY perspective is
that they require repeated regular expressions to read "the same
thing". By keeping expressions extremely simple the damage can be
minimized, but sometimes it can be useful to centralize the pattern
specifications for certain argument types. Named Step Argument
Transforms allow the use of a unique name a substitution point for the
regular expression associated with a transform. For example, for the
step::

  Then these users should be friends: "bob, adelaide, samantha"

The following definitions can be used::

 from itertools import combinations

  @NamedTransform( '{user list}', r'("[\w\, ]+")', r'^"([\w\, ]+)"$' )
  def transform_user_list( slist ):
     return [ User.objects.find( name )
              for name.strip() in slist.split( ',' ) ]

  @Then(r"these users should be friends: {user list}" )
  def check_all_friends( user_list ):
      for user1, user2 in combinations( user_list, 2 ):
          assert user1.is_friends_with( user2 )

The arguments to `NamedTransform` are `name`, `in_pattern` and
`out_pattern`, respectively. `NamedTranform` is equivalent to having
`in_pattern` substituted for all occurrences of `name` in step
specifications, and defining a standard `Transform` with
`out_pattern` as its pattern.

The distinction between `in_pattern` and `out_pattern` is that the
`in_pattern` can be used to match surrounding context to uniquely
identify parameters, while the `out_pattern` searches within the text
recognized by the `in_pattern` to pull out the semantically relevant
parts. When this distinction is not relevant, specify only one
pattern, and it will be used for both in and out patterns.

Ignoring directories
--------------------

If a directory contains files with the extension ``.feature`` but you'd like Freshen to skip over
it, simply place a file with the name ".freshenignore" in that directory.


Using with Django
-----------------

Django_ is a popular framework for web applications. Freshen can work in conjunction with the
`django-sane-testing`_ library to initialize the Django environment and databases before running
tests. This feature is enabled by using the ``--with-django`` option from django-sane-testing. You
can also use ``--with-djangoliveserver`` or ``--with-cherrypyliveserver`` to start a web server
before the tests run for use with a UI testing tool such as `Selenium`_.


Using with Selenium
-------------------

Selenium is not supported until plugin support is implemented. If you need to use Selenium, try
version 0.1.


Running
-------

Freshen runs as part of the nose framework, so all options are part of the ``nosetests`` command-
line tool.

Some useful flags for ``nosetests``:

- ``--with-freshen``: Enables Freshen
- ``-v``: Verbose mode will display each feature and scenario name as they are executed
- ``--tags``: Only run the features and scenarios with the given tags. Tags should follow this
  option as a comma-separated list. A tag may be prefixed with a tilde (``~``) to negate it and only
  execute features and scenarios which do *not* have the given tag.
- ``--language``: Run the tests using the designated language. See the
  ``Internationalization`` section for more details

You should be able to use all the other Nose features, like coverage or profiling for "free". You
can also run all your unit, doctests, and Freshen tests in one go. Please consult the `Nose manual`_
for more details.

Internationalization
--------------------

Freshen now supports 30 languages, exactly the same as cucumber, since the
"language" file was borrowed from the cucumber project. As long as your
``.feature`` files respect the syntax, the person in charge of writing the
acceptance tests may write it down in his/her mother tongue. The only exception is
the new keyword for `specifying step definition modules`_ since it is not available
in Cucumber_. For the moment, this keyword is available only in English, French,
and Portuguese. If you use another language, you must use the English keyword for this
particular keyword (or translate it and add it to the ``languages.yml`` file).

The 'examples' directory contains a French sample. It's a simple translation of
the English 'calc'. If you want to check the example, go to the 'calc_fr'
directory, and run::

    $ nosetests --with-freshen --language=fr

The default language is English.


Additional notes
----------------

**Why copy Cucumber?** - Because it works and lots of people use it. Life is short, so why spend it
on coming up with new syntax for something that already exists?

**Why use Nose?** - Because it works and lots of people use it and it already does many useful
things. Life is short, so why spend it re-implementing coverage, profiling, test discovery, and
command like processing again?

**Can I contribute?** - Yes, please! While the tool is currently a copy of Cucumber's syntax,
there's no law that says it has to be that forever. If you have any ideas or suggestions (or bugs!),
please feel free to let me know, or simply clone the repository and play around.

.. _`Source code`: http://github.com/rlisagor/freshen
.. _`Nose`: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/
.. _`Nose manual`: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html
.. _`Cucumber`: http://cukes.info
.. _`Cucumber wiki`: http://wiki.github.com/aslakhellesoy/cucumber/
.. _`Feature-Coupled Steps Antipattern`: http://wiki.github.com/aslakhellesoy/cucumber/feature-coupled-steps-antipattern
.. _`Selenium`: http://seleniumhq.org/
.. _`Django`: http://www.djangoproject.com/
.. _`django-sane-testing`: http://devel.almad.net/trac/django-sane-testing/

..  LocalWords:  py init subpackage stepregistry defs Cloe sc scc num
..  LocalWords:  calc getattr str Antipattern AfterStep glc ftc Lua
..  LocalWords:  gcc doesnotexist Multi multi docstrings iterrows UI
..  LocalWords:  adelaide samantha itertools NamedTransform slist
..  LocalWords:  NamedTranform freshenignore Django django nosetests
..  LocalWords:  djangoliveserver cherrypyliveserver doctests
