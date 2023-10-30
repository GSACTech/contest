# Repository for [Global Software Analysis Competition](https://gsac.tech/)

This project automatically tests and compares all participants' static analysis tools.

* The participants should develop a software analyzer using the
  provided [template](./example-analyzer).
* They should accept the [assignment](https://classroom.github.com/a/S_09sdh2) and submit as a
  GitHub repository which will be visible only to admins.

### To get all the requirements run the following script

```shell
sudo /path/to/contest/install_required_packages.sh
```

## Usage

* To evaluate their analyzers on our [test suites](./resources/test_suites/testcases)
    * Create a JSON-formatted file, which contains list of {owner, URL} pairs.
    * Run the following python script

```shell
python3 /path/to/evaluate.py --test-suites PATH_TO_TESTS --tools PATH_TO_JSON_FILE
```

* PATH_TO_TESTS shows the directory path containing test suites.
* PATH_TO_JSON_FILE is the path of JSON-formatted file which must be in the following format

```json
{
  "owner": "URL of GitHub repository"
}
```

## Results

* The evaluation score for each analyzer is calculating in the following way
    * There are three categories of test cases: memory leak, buffer overflow and use after free.
    * Each category has three groups of test cases: easy, medium and hard.
    * For each group there's a corresponding weight: 1 for easy, 2 for medium and 3 for hard ones.
    * The evaluator calculates [F1 score](https://en.wikipedia.org/wiki/F-score) for each test case.
    * It then multiplies the F1 score by the weight of its test group and adds the result to the
      final score.

* In special results directory the following files will be stored
    * All analyzers with their results `result_dir/analyzer_dir/result_sarif_files`.
    * The evaluated scores on test suites in JSON and Excel formatted files.
