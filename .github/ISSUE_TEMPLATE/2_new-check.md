---
name: New check proposal
about: Describe a font problem that FontBakery should detect
title: 'New check: subject'
labels: 'New check proposal'
assignees: ''

---

## What needs to be checked?

(Provide a short, one line sentence, describing what needs to be checked)


## Detailed description of the problem 

(Describe which programs, operating systems and/or text rendering engines are affected by the problem. This description would likely be reused for the check rationale text.)


## Optional fix

(Please provide instructions on how to fix the problem on at least one font editor or binary hot-fixing script)


## Resources and exact process needed to replicate

(Please provide files that can be used to replicate the problem. We would use it during development of the proposed check and possibly also as a test file for our code-tests.)


## Expected Profile

Please suggest in which profile should it be included. (You could inspect the Profiles's list at https://font-bakery.readthedocs.io/en/stable/fontbakery/profiles/index.html). Most common are:

- [ ] Vendor-specific: Google Fonts
- [ ] Vendor-specific: Adobe Fonts
- [ ] OpenType (requirements imposed by the OpenType specification)
- [ ] Universal (broadly accepted best practices on the type design community)
- [ ] Other:

## Expected Result

Which log result level should it have:

- [ ] 🔥 **FAIL** (Something that must be addressed for the propper functioning of the font)
- [ ] ⚠️ **WARN** (Highlights potential issues that are suggested to address)

## Severity assessment

(On a 1 to 5 level, how "buggy" would the font be considered if not including the aspect checked? Where 1 is something ideal to include but that would not affect the behavior of the font, and 5 is something that could lead to bad performance.)
