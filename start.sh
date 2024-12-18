#!/bin/sh -eu

# Start both FastAPI applications in the background
maybe_install () {
  if [ ! -d .venv ] || [ \( Pipfile -nt .venv \) ] || [ \( Pipfile.lock -nt .venv \) ]; then
    set -x
    pipenv sync --dev
    set +x
  fi
}

print_help () {
  echo "Helper script to manage the FastAPI apps and code formatting."
  echo ""
  echo "EXAMPLES:"
  echo "To start both FastAPI apps:"
  echo "    $0 start"
  echo "To check formatting:"
  echo "    $0 lint"
  echo "To reformat code:"
  echo "    $0 reformat"
  echo ""
}

if [ $# -eq 0 ]; then
  print_help
  exit 0
fi

while [ $# -gt 0 ]; do
  case "$1" in
    start )  ## Start both FastAPI apps
      maybe_install
      pipenv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
      pipenv run uvicorn mail.main:app --host 0.0.0.0 --port 8001 --reload &
      wait
      shift
      ;;
    lint )  ## Check the formatting of the code
      maybe_install
      set -x
      pipenv run black --check .
      set +x
      shift
      ;;
    reformat )  ## Automatically fix code issues where possible
      maybe_install
      set -x
      pipenv run black .
      set +x
      shift
      ;;
    help )  ## Describe the commands available in this script
      print_help
      shift
      ;;
    * )
      echo "Unrecognized argument: $1"
      exit 1
      ;;
  esac
done
