# 1. Introduction

Font quality is a daily concern of font publishers, foundries and type designers. Every foundry has their own set of tools to ensure that the fonts they publish are in good shape. The “Font Bakery” project is a new and unique initiative to publicly, openly and collaboratively gather knowledge on font issues - and whisk that knowledge into software tools that check font files. Checks can be made on OpenType, UFO, GlyphsApp, and TruFont files, and exist at 3 levels: As standardized format profiles, as distributor requirements, or as individuals’ custom checks.

Font Bakery began in 2013 as a small and simple Python program written as a side-project by Dave Crossland to accelerate the onboarding process for Google Fonts. In 2017, he commissioned Felipe Sanches and Lasse Fister to take it to the next level by rewriting it into a modern and modular architecture. It now has an active community of contributors from foundries around the world, and is now suitable for both individual designers and all large font distributors to use via command-line interfaces and a web dashboard.

# 2. How does the Font Bakery project improve font production?

The Font Bakery software architecture follows the software engineering concept of Test Driven Development, which is a development process with a higher chance of leading to better software products. The key idea is that people can never avoid committing unintended mistakes when writing computer programs, so they should have fully automatic processes that constantly validate the output of their programs to ensure that they always work as expected. With such automation in place, errors can be detected at the moment they are introduced, and developers can fix their oversights as soon as possible. In fact, before starting to write a program itself, a developer should devise the automatic validation tests first; while these will initially fail, as the program begins to take shape then they will begin to pass. After that milestone, care can be taken to prevent the program from regressing and the tests falling into a failed state. 

Font Bakery applies these best practices to font development. It contains an ever growing collection of “checks” that when run against a font project can detect typical mistakes made by font developers. While it is possible to use the tool only once in a font project &mdash; as a final step before publishing a font family &mdash; it is better to use it as a daily and integral part of the font development process. That is inherently incremental and iterative, so Font Bakery can be used as soon as a binary OpenType font is exported or generated, and each and every time after that.

![Screenshot of a typical Font Bakery command-line output in the Terminal app.](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure2.1.png "Figure 2.1")

Font Bakery is primarily available for use on your own computer as a command-line tool. Throughout 2017 and 2018, the development team has focused on the core features - creating the actual font checking routines. 

For designers using version control systems such as Git or Mercurial, the command-line tool can be integrated into continuous integration pipelines (such as travis-ci.org) so that it is run every time any font files are changed. The command line tool will, by default, display check results as they happen, with live progress indications and use of color, and a few fun ‘easter egg’ surprises for certain check results.

Current there is no official graphical user interface application; however an unofficial one has been started by Eli Heuer (at github.com/eliheuer/fontbakery-desktop)

![Screenshot of the build status of the Font Bakery software project on Travis, a ‘Continuous Integration’ system. Font Bakery enables a similar ‘CI’ approach for font projects hosted on GitHub or similar version control repository systems, that can be public or private.](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure2.2.png "Figure 2.2")

Google Fonts uses a public GitHub repository for managing the onboarding of fonts into the catalog. Each addition of a new family or update to an existing one goes through a "Pull Request" workflow, in which a proposal is made to update the fonts in a way that is fully documented and can be commented on. Today, Font Bakery reports are posted on these GitHub Pull Request pages to describe the technical quality of the fonts affected by the proposed modifications. 

GitHub uses the Markdown markup to apply basic typographic formatting to the Pull Request document and comments (Figure 2.3) and Font Bakery is capable of outputting its check results in this format. Unusually for Markdown, it also uses HTML5 ‘expandable tree’ lists to structure the bulky information; these allow users to ‘drill down’ to get additional contextual information on the check results they are most interested in, while hiding all other details.

![Screenshot of a check report formatted with Markdown, with one family and one check expanded to ‘drill down’ into the details. Adding a new font family to Google Fonts requires evaluating its quality by running Font Bakery in this way.](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure2.3.png "Figure 2.3")

# 3. How does the Font Bakery Dashboard project improve font publishing workflows?

There are now more than 900 families in the Google Fonts catalog, and over 2,000 font files; with over 100 checks, this means 100,000s of check results can be generated. To interrogate, monitor, and manage such a large collection of font families and quality metadata, an official sister project was started: Font Bakery Dashboard. 

This is currently under development (at github.com/googlefonts/fontbakery-dashboard) and has two parts. The first is a ‘back end’ web server application, that orchestrates 10s or 1,000s of “Font Bakery Worker” virtual machines using the Kubernetes system (Figure 3.1) 

![Diagram of the Font Bakery Dashboard system architecture. Source: https://github.com/googlefonts/fontbakery-dashboard/blob/182a109cd8c12655b1cab6d98ecf3abfcdd7b857/docs/nodes%20diagram%20v1.pdf](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure3.1.png "Figure 3.1")

The Linux kernel “container” technology pioneered by Docker Inc is widely supported on many computing infrastructure providers such as Google Cloud Platform, Amazon Web Services, Microsoft Azure, Digital Ocean, or your own server hardware. It can even run on your laptop, using the Minikube system. The benefit of using Kubernetes is that it can run as many copies of Font Bakery in parallel as needed. 

The deluge of check results from such parallel runs are all stored in a database, and the second part is a 'front end’ web page application which provides a graphical user interface to that database. This itself has two parts. 

The first is a front page dashboard table, highlighting the overall status of the whole catalog at each stage of publication (Figure 3.2) With this global view of the check results, a person managing the catalog can better grasp the overall state, decide where to focus improvement efforts, and see progression of an update from a foundry through each stage to the final publication on production API servers that are seen by end-users.

![Screenshot of the front page table of the Font Bakery Dashboard.](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure3.2.png "Figure 3.2")

The second are all the unique check results pages, that contain all details. While the Markdown report format is a simple expanding tree, the Font Bakery Dashboard Report Page template (Figure 3.3) offers a much more sophisticated interface for filtering results by check status or font file.

![Screenshot of a Check Results page on the Font Bakery Dashboard.](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure3.3.png "Figure 3.3")

In addition to checking font projects at each stage of publication, a secondary feature, the Font Bakery Dashboard offers font developers a simply way to get started using Font Bakery to check their projects; users can upload font project files using a simple drag and drop interface and run the checks at a click of a button, with no need to install any Font Bakery software themselves. This is available today at fontbakery.com 

# 4. What is the opportunity for designers and foundries to collaborate on font quality assurance?

The Font Bakery project has 3 core product values:

1. **Simple.** Code is easy to read, and running checks is easy and pleasant.
2. **Reliable.** You can trust each check, because its code is constantly verified with self-tests.
3. **Understandable.** Each check is documented, so you know why it is important.

The first value, simplicity, was important from the earliest days of the project. Font Bakery began as a single-file Python script. It was short, simple, and self-contained, so it could be shared between type designers by attaching it to an e-mail or included inside each font project’s working files. But as the number of checks grew, covering a larger and larger set of issues, that single-file approach became more and more difficult to manage. The boundaries between the routines for each specific check were not clear, and if one check encountered an error in the code itself (not a failure of the file being checked) then the entire program halted. This is obviously unpleasant, and we strive to make using the program comfortable.

In order to reduce the growing code complexity, the program was split into a logical set of files, with smaller chunks of Python code. This means users can not share the scripts by e-mail anymore, but instead Font Bakery is now a mature cross-platform Python package that can  be easily installed through the Python Package Index (at pypi.org/project/fontbakery) using the simple command ‘pip install fontbakery.’

Having the source code for checks organized into small chunks of code also has a very important purpose: It makes the code easier to grasp by people who are not necessarily professional software developers, but who may benefit from the transparency of the codebase. Type designers are nowadays gradually getting more comfortable with the Python language as an auxiliary tool for their craft. We believe that the ability to actually see the algorithms of font checking routines is instrumental to spreading the knowledge of font quality issues among the global type design community. 

![Simplicity is a core product value, and the implementation of a check should be as straightforward as possible. This shows a real example of a check included in Font Bakery today. Source: github.com/googlefonts/fontbakery/blob/28427a87ae9a3b963997dd6562a877bed3d8e166/Lib/fontbakery/specifications/post.py#L21-L34](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure4.1.png "Figure 4.1")

The second value, reliability, comes down to trust. Just as we'd expect seat-belts and parachutes to have strict quality controls on their design and manufacturing, a checking system is useless if the results can not be trusted. That's why Font Bakery has ‘code tests.’ This may sound like a statement coming right out of the movie Inception, but we do indeed have Python code to test the Python code that checks the quality of the font files!

In addition to these proofs of correct functionality, we also gather examples of good and bad fonts that cause each check to pass and to fail. With those tests and examples, the tool is continuously exercised to assure no bad behaviour is introduced by programming errors. 

![Example of a ‘code test’ included in Font Bakery to ensure that a font check (for consistent underline thickness values in a family) works correctly.](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure4.2.png "Figure 4.2")

Even though Test Driven Development (TDD) is a common practice of contemporary professional software development, we are aware of only one font quality assurance tool that extensively employ automated code-tests in their respective codebases; the OpenType Sanitizer, available from github.com/khaledhosny/ots, and original created by the Google Chrome team to prevent malicious web fonts from harming users through security exploits. 

So this, in conjunction with the other 2 product values described in this article, makes Font Bakery a unique and robust tool in its field: A tool we can trust, because we continuously test it.

The third value is understandability. Having the checks implemented correctly and in an easy-to-read fashion is important, of course, but it is almost pointless if users do not understand why a failing check is actually a problem. We believe Font Bakery is more than just a set of checks for fonts. It is actually a collaborative project for gathering knowledge about font quality. Perhaps even more critical than the checking routines themselves are the rationale descriptions for each check (Figure 4.3.)

![The detailed rationale description for the check shown in Figure 4.1. Users will not only know that there's an issue with a font, but also why is that check is relevant.](https://raw.githubusercontent.com/googlefonts/fontbakery/main/docs/source/product/images/figure4.3.png "Figure 4.3")

This is an on-going effort, with checks and rationales being regularly reviewed and updated by the community of type designers using the tool, so that we can all have a detailed understanding of the relevance of each check. The rationales are stored as metadata in the code, so that can be accessed from other tools built with Font Bakery (like the Dashboard) that can display this information when relevant for users. 

# 5. Why contribute publicly? Common goals with shared costs

Good quality is a common goal for all designers and foundries, not only those working on libre fonts. Developing good tools to ensure quality is expensive, time consuming, and requires deep expertise. Working in a public participatory fashion, ‘in the open,’ can be a cost-effective business strategy for type designers and font publishers because the costs are shared, and the benefits are mutual. The synergies of public discussion that occur during public development can help the type community as a whole to improve, in ways that no private team or consortium could possibly do in an isolated fashion.

It is important to stress that collaboration in an open and public project like Font Bakery is not limited to the people writing code, but also involves any person with some knowledge and experience of font quality; even typographers not involved in the day-to-day activity of making fonts have many good ideas about the details that are important to get right.

So, if you are not a programmer but want to participate, there is a safe and welcoming path for you. The easiest way to participate is by ‘opening an issue’ on Font Bakery's issue tracker (at github.com/googlefonts/fontbakery/issues) describing the font problems you'd wish to have checks for. From that initial description, a conversation typically emerges among the project programmers and other type designers to determine the best way to implement it.

# 6. Conclusion: Font Bakery's "Secret Master Plan"

To recap, these are our three guiding product values:

1. **Simple.** Code is easy to read, and running checks is easy and pleasant.
2. **Reliable.** You can trust each check, because its code is constantly verified with self-tests.
3. **Understandable.** Each check is documented, so you know why it is important.

The (not so) secret part of the plan is our aspiration to make Font Bakery the ultimate font checking tool. In addition to our own checks, Font Bakery also ‘wraps’ most all other font checking tools, so that check reports are as comprehensive as possible. Long term, we expect to replicate their useful checks and augment them with code tests and rationale descriptions. Having an ultimate tool is surely yet another good reason to collaborate publicly.

Font Bakery is developed on GitHub (at github.com/googlefonts/fontbakery) and we love to review code contributions (via Pull Requests) as well as to discuss bug reports and feature requests in our issue tracker. We hope you’ll join us.
