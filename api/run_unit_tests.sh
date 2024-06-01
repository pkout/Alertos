#!/bin/bash

##############################################################################
# Runs tests.
#
# Usage: ./test.sh [path]
#
# The optional `path` argument can contain a path to the specific test
# package or module to run tests on skipping tests of other parts of the
# software.
#
# Arguments:
#
#   -v, --verbose: Verbose output.
#   -c, --coverage: Generate coverage report.
#
# Example: ./run_unit_tests.sh test_package_a.test_module_a
#
##############################################################################

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export PYTHONPATH=${PYTHONPATH}:${SCRIPT_DIR}/src
export PYTHONPATH=${PYTHONPATH}:${SCRIPT_DIR}/tests

TEST_UNIT=${1}
VERBOSE=-v
COVERAGE=NO

# while [[ $# -gt 0 ]]; do
#   case ${1} in
#     -c|--coverage)
#       COVERAGE=YES
#       shift
#       ;;
#     -v|--verbose)
#       VERBOSE=-v
#       shift
#       ;;
#     *)
#       TEST_UNIT=${1}
#       shift
#       ;;
#   esac
# done

IS_MODULE_PATH=YES

if [[ ! -z ${TEST_UNIT} ]]; then
  if [[ ${TEST_UNIT} =~ [A-Z] ]]; then
    IS_MODULE_PATH=NO
  fi
fi

if [[ -z ${TEST_UNIT} ]]; then
  python3 -m unittest discover -s tests ${VERBOSE}
else
  if [[ ${IS_MODULE_PATH} == YES ]]; then
    python3 -m unittest discover -s ${TEST_UNIT} ${VERBOSE}
  else
    python3 -m unittest ${TEST_UNIT}
  fi
fi

if [[ ${COVERAGE} == YES ]]; then
  echo "Generating coverage report..."
  if [[ -z ${TEST_UNIT} ]]; then
    TEST_UNIT=tests
    coverage run -m unittest discover -s ${TEST_UNIT} ${VERBOSE}
  fi
  coverage report
fi