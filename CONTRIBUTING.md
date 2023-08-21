# Contributing Guide

First off, thanks for taking the time to contribute! ❤️

We welcome your contributions and participation. If you aren't sure what to
expect, here are some norms for our project so you feel more comfortable with
how things will go.

Please make sure to read all the sections before making your contribution. It
will make it a lot easier for us maintainers, and smooth out the experience for
all involved. The community looks forward to your contributions. 🎉

If this is your first contribution to FontBakery, we have a [tutorial] that walks
you through setting up your developer environment, making a change, and testing it.

[tutorial]: https://font-bakery.readthedocs.io/en/latest/developer/source-contrib-guide.html

## Google CLA

Contributions to this project must be accompanied by a Contributor License Agreement.
You (or your employer) retain the copyright to your contribution;  this simply gives
us permission to use and redistribute your contributions as part of the project.
Head over to <https://cla.developers.google.com/> to see your current agreements
on file or to sign a new one.

You generally only need to submit a CLA once, so if you've already submitted one
(even if it was for a different project), you probably don't need to do it again.

## Our mission

FontBakery is a community project. Consequently, it is wholly dependent on its
community to provide a productive, friendly and collaborative environment.

The first and foremost goal of the Font Bakery community is to discover and
document all possible problems that a font project can have, and then use that
knowledge to provide `fontbakery`, a tool that simplifies the process
of performing quality assurance on font files.

The second and equally important goal is to create and maintain a community of
developers that foster easy and agile development of such tool.

This document is intended to be a living one that evolves as the community
matures, via the same pull request (PR) and code review processes that shape
the rest of the project.


## Find an issue

Use the [Issues] page to find a `good first issue` for new contributors and
`help wanted` issues for our other contributors.

If you have been contributing for a while, take a look at issues labeled
`backlog` and consider their priority level.

When you create your first pull request, add your name to our
[Contributors] list. Thank you for making FontBakery better! 🙇‍♀️

[Issues]: https://github.com/fonttools/fontbakery/issues
[Contributors]: ./CONTRIBUTORS.txt


## Coding conventions

We use [Black] to format the codebase. The maximum line length is 88 characters.
That's probably all you need to know to stay out of trouble. If there's
something ambiguous that you need clarification on, just ask. 😉

Always write clear log message for your commits. One-line messages are fine
for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    >
    > A paragraph describing what changed and its impact."

If there's an issue describing the problem fixed or feature implemented, be sure to
unclude a reference to it in the log message: `(issue #123)`

Make sure you don't include `@mentions` in your commit messages.

This is collaboratively developed free software. Consider the people who will read
your code, and make it look nice for them. 😍

[Black]: https://github.com/psf/black


## Which branch to use

Unless the issue specifically mentions a branch, please create your own branch
from the **main** branch.

Prefix the branch's name with your GitHub handler, followed by a forward slash `/`.
This way we know who created the branch, and all your branches will be grouped
together.

## When to open a pull request

It's OK to submit a PR directly for problems such as misspellings or other
things where the motivation/problem is unambiguous.

If there isn't an issue for your PR, please start a [discussion] first and explain the
problem or motivation for the change you are proposing. When the solution isn't
straightforward, for example, "Implement missing command X", then also outline
your proposed solution. Your PR will go smoother if the solution is agreed upon
before you've spent a lot of time implementing it.

[discussion]: https://github.com/fonttools/fontbakery/discussions


## Submitting a pull request

Include a list of all the noteworthy changes you've done. Elaborate on any
decisions you had to make, and include links and/or screenshots, if applicable.

If you're committing new code, we expect you to include tests that provide
coverage for it as well.

When you make a PR for small change (such as fixing a typo, style change, or
grammar fix), please squash your commits so that we can maintain a cleaner git
history.

If the PR will **completely** fix a specific issue, include `Fixes #123` in the
PR body (where 123 is the specific issue number the PR will fix). This will
automatically close the issue when the PR is merged.


## Code review

As a community we believe in the value of code review for all contributions.
Code review increases both the quality and readability of our codebase, which
in turn produces high quality software.

There are two aspects of code review: giving and receiving.

To make your PR go smooth, keep in mind that the reviewers expect you to:

* Follow the project's [coding conventions](#coding-conventions)
* Write [good commit messages](https://chris.beams.io/posts/git-commit/)
* Break large changes into a logical series of smaller patches which individually
  make easily understandable changes, and in aggregate solve a broader issue


## Expectations of reviewers
### Review comments

Reviewers play a crucial role as the initial interface with new members of the
FontBakery community, since they can have a substantial impact on their first
impressions. Consequently, reviewers hold significant importance in shaping
the overall well-being of the community.

Reviewers are expected to not only abide by the [code of conduct](#code-of-conduct),
but also strongly encouraged to go above and beyond the code of conduct to
promote a collaborative, respectful FontBakery community.

### Review latency

Reviewers are expected to respond in a timely fashion to PRs that are assigned to
them. If reviewers fail to respond, those PRs may be assigned to other reviewers.

If reviewers are unavailable to review for some time, they are expected to set their
[user status](https://help.github.com/en/articles/personalizing-your-profile#setting-a-status)
to "busy".


## How to get your pull request reviewed

🚧 If you aren't done with the changes yet, mark your pull request as a Draft
so that reviewers wait for you to finish before commenting.

1️⃣ Limit your pull request to a single task. Don't tackle multiple unrelated
things, especially refactoring. If you need large refactoring for your change,
chat with a maintainer first, then do it in a separate PR first without any
functionality changes.

👀 Group related changes into separate commits to make it easier to review.

😅 If we request changes, make them in new commits. Please don't amend or rebase
commits that we have reviewed already. When your pull request is ready to merge,
you can rebase your commits yourself, or we can squash when we merge. Just let
us know what you are more comfortable with.

🚀 We encourage [follow-on PRs](#follow-on-pr) and a reviewer may let you know in
their comment if it is okay for their suggestion to be done in a follow-on PR.
You can decide to make the change in the current PR immediately, or agree to
tackle it in a reasonable amount of time in a subsequent pull request. If you
can't get to it soon, please create an issue and link to it from the pull
request comment so that we don't collectively forget.

### Follow-on PR

A follow-on PR is a pull request that finishes up suggestions from another pull
request.

When the core of your changes are good, and it won't hurt to do more of the
changes later, our preference is to merge early, and keep working on it in a
subsequent. This allows us to start testing out the changes, and more
importantly enables other developers to immediately start building their work
on top of yours.

This helps us avoid pull requests to rely on other pull requests. It also avoids
pull requests that last for months, and in general we try not to let "perfect be
the enemy of the good". It's no fun to watch your work get stale, and it
kills contributor momentum.


## The life of a pull request

1. You create a Draft pull request. Reviewers will ignore it mostly
   unless you mention someone and ask for help. Feel free to open one and use
   the pull request to see if the CI passes. Once you are ready for a review,
   click "Ready for Review" and leave a comment that it's ready for review.

   If you create a regular pull request, a reviewer won't wait to review it.
1. A reviewer will assign themselves to the pull request. If you don't see
   anyone assigned after 3 business days, you can leave a comment asking for a
   review. Sometimes we have busy days, sick days, weekends and vacations, so
   a little patience is appreciated! 🙇‍♀️
1. The reviewer will leave feedback.
    * `nit` (for nitpick): These are suggestions that you may decide to
      incorporate into your pull request or not without further comment.
    * It can help to put a 👍 on comments that you have implemented so that we
      can keep track.
    * It is okay to clarify if you are being told to make a change or if it is a
      suggestion.
1. After you have made the changes (**in new commits please!**), leave a comment.
   If 3 business days go by with no review, it is okay to bump.
1. When a pull request has been approved, the reviewer will merge
   your commits. If you prefer to squash your own commits, at any time leave a
   comment on the pull request to let them know that.

After your first pull request is merged, you will be invited to the
Collaborators team which you may choose to accept (or not). Joining the team lets
you have issues in GitHub assigned to you.


## Breaking Changes

Some changes may break our compatibility with previous versions of FontBakery.
When that happens, we need to release that change with a new major version number
to indicate to users that it contains breaking changes.
When you realize that you may need to make a breaking change, discuss it with
a maintainer on the issue or pull request and we'll come up with a plan for how
it should be released.


## Code of Conduct

The FontBakery project is governed by our [Code of Conduct](./CODE_OF_CONDUCT.md).


## Legal Notice

Thank you for considering contributing to this open-source project ("the Project"). By submitting contributions to this Project, you agree to comply with the following guidelines:

1. You confirm that each of your contributions was created by you or that you have the necessary rights to submit it under the terms of the Apache 2.0 license.

2. You grant the Project and its users a perpetual, worldwide, non-exclusive, royalty-free, irrevocable, transferable license to use, modify, display, distribute, and sublicense your contributions under the Apache 2.0 license.

3. You acknowledge that your contributions may be publicly available, and you waive any privacy or publicity rights with respect to your contributions.

4. You agree to follow the Project's code of conduct, which ensures a respectful and inclusive environment for all contributors.

5. You understand that your contributions are provided "as is," and the Project and its contributors disclaim any warranties or liabilities associated with your contributions.


## License

By contributing to this Project, you agree that your contributions will be licensed under the terms of the Apache 2.0 license. You can find a copy of the license in the [LICENSE file](./LICENSE.txt).


## Contact

If you have any questions or concerns regarding these guidelines or the Project, please contact us via the issue tracker or send an email to Felipe Sanches at juca@members.fsf.org
