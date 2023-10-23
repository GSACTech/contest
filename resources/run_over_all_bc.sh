# this is a very simple runner to iterate over all bitcode files,
# run the tool on each of them and rename reports by their input name

function check_args() {
  [ -d "$BC_DIR" ] || { echo "bitcode files directory not found: $BC_DIR"; exit 1; }
  rm -rf "$RESULTS_DIR"
  mkdir "$RESULTS_DIR"
}

function run_over_all_bc() {
  PAR_DIR="$(dirname $BC_DIR)"
  find "$PAR_DIR" -type f -name "run.sh" -print0 | while read -r -d $'\0' RUNNER; do
    find "$BC_DIR" -type f -name "*.bc" -print0 | while read -r -d $'\0' FILE; do
      bash "$RUNNER" "$FILE"
      REPORT="$(basename "$FILE").sarif"
      mv "report.sarif" "$RESULTS_DIR/$(basename "$FILE").sarif" || echo "failed to run on $FILE"
    done
  done
}

function main() {
  BC_DIR="$(realpath "$1")" || { echo "BC_DIR must be passed as 1st argument"; exit 1; }
  RESULTS_DIR="$(realpath "$2")" || { echo "RESULTS_DIR must be passed as 2nd argument"; exit 1; }
  check_args || exit 1
  run_over_all_bc
}

main "$@"
