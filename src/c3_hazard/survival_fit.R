# Fit the adoption-hazard model with a mixture cure fraction.
#
# Some mathematics is never consumed, so a plain Kaplan-Meier or Cox fit
# would be mis-specified. flexsurvcure carries an explicit cure fraction
# for the "never adopted" subgroup; the KM curve is kept as a
# non-parametric cross-check.

library(flexsurv)
library(flexsurvcure)

fit_cure_model <- function(surv_data, covariate_formula, dist = "weibull") {
  # TODO: flexsurvcure(Surv(time, event) ~ ., mixture = TRUE, link = "logistic")
  stop("not implemented")
}

crosscheck_km <- function(surv_data) {
  # TODO: survfit(Surv(time, event) ~ cohort), compare qualitatively
  stop("not implemented")
}
