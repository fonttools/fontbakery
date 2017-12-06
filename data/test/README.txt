The data in this folder should ideally be immutable. These font families may contain issues and it is important that we do not fix the issues in them. That's because several of the fontbakery code tests rely on these families being broken in order to validate the FAIL code-paths of the fontbakery checks.

There are only 2 exceptions to this rule here:

1) The data/test/regression folder may be updated whenever there's a deployment of a family into fonts.google.com. The rationale is that the families in this folder are used exclusively for the regression checks and they must be kept in sync with the data offered by the Google Fonts API. We keep them separate in this specific-purpose folder so that we avoid the potential future conflict of updating them and breaking several other code test implementations.

2) This data/test folder started with a handful of families and later we started implementing code tests that rely on a few of them. There may be families here never really used on code tests. So we may want to delete some of those and that would be OK.

Felipe Sanches
FontBakery maintainer
August 1st, 2017
