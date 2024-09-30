# kdevops rdstcp suite

kdevops can run several RDS-TCP tests.

Run `make menuconfig` and select:

  Target workflows -> Dedicated target Linux test workflow ->rdstcp

Then configure the test parameters by going to:

  Target workflows -> Configure and run the rdstcp suite

Choose the location of the repo that contains the version of rds-tools
you want to use for the test, and which tests you would like to run.

Then, run:

  * `make`
  * `make bringup`
  * `make rdstcp`
  * `make rdstcp-baseline`
