---
name: New check proposal
about: Describe a font problem that you wished FontBakery could detect
title: 'New check: subject'
labels: 'New check proposal'
assignees: ''

---

## What needs to be checked?

(Provide a short, one line sentence, describing what needs to be checked)


## Detailed description of the problem 

(Describe which applications, operating systems and/or text rendering engines are affected by the problem. This description will likely be reused for the check's rationale text)


## Resources and steps needed to reproduce the problem

(Provide the steps and files for reproducing the problem. We will need them for developing the proposed check and for including them in tests that validate the codebase)


## Suggested profile

Suggest which profile the check should be added to. The most common are:

- [ ] Vendor-specific: Google Fonts
- [ ] Vendor-specific: Adobe Fonts
- [ ] OpenType (requirements imposed by the OpenType specification)
- [ ] Universal (broadly accepted best practices on the type design community)
- [ ] Other:

## Suggested result

Which log result level should the check have:

- [ ] 🔥 **FAIL** (An issue that must be corrected for the font to function properly)
- [ ] ⚠️ **WARN** (A potential issues that may need to be addressed)

## Severity assessment

(Classify the problem on a scale of 1 (minor) to 5 (major). How "buggy" would the font be considered if it had the problem described?)
