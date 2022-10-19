---
name: New check proposal
about: Describe a font problem that FontBakery should detect
title: 'New check: subject'
labels: 'New check proposal'
assignees: ''

---

**Short (one line) sentence describing what needs to be checked:**


**Detailed description of the problem. It would likely be reused for the check rationale text.**

(Please mention which programs, operating systems and/or text rendering engines are affected by the problem)


**Instructions on how to fix the problem on at least one font editor (or binary hot-fixing script).**


**Resources and exact process needed to replicate**

(Sample files that can be used to replicate the problem. We would use it during development of the proposed check and possibly also as a test file for our code-tests.)


**Please suggest in which profile should it be included**

(You could inspect the Profiles's list at https://font-bakery.readthedocs.io/en/stable/fontbakery/profiles/index.html). Most common:

- [ ] vendor-specific: Google Fonts
- [ ] vendor-specific: Adobe Fonts
- [ ] OpenType (requirements imposed by the OpenType specification)
- [ ] Universal (broadly accepted best practices on the type design community)
- [ ] Other:

**Which log result level should it have:**

- [ ] **FAIL** (Something that must be addressed for the propper functioning of the font)
- [ ] **WARN** (Highlights potential issues that are suggested to address)

**A severity assessment:**

(On a 0 to 5 level how "buggy" would the font be considered if not including the aspect checked?)
