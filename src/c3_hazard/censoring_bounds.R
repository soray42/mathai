# Robustness appendix: relax the non-informative-censoring assumption.
#
# depCensoring provides copula-based dependent-censoring estimators with
# set-identification bounds, and its cure = TRUE option handles the
# never-adopted subgroup at the same time. This is a frontier feature, so
# it backs up the main flexsurvcure fit rather than replacing it.

library(depCensoring)

bounds_under_dependence <- function(surv_data) {
  # TODO: report the identified set, not a single point estimate
  stop("not implemented")
}
