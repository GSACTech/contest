# Repository for [Global Software Analysis Competition](https://gsac.tech/)

This project automatically tests and compares all participants' static analysis tools.

* To participate in this contest, users should develop a software analyzer using the
  provided [template](./example-analyzer)
* They should accept the [assignment](https://classroom.github.com/a/S_09sdh2) and submit as a
  GitHub repository which will be visible only to admins

### To get all the requirements run the following script

```shell
sudo /path/to/contest/install_required_packages.sh
```

## Usage

* To run this tool and get corresponding rates on our test suites
  users must create a JSON formatted file, containing a list of URLs of static analyzers and their
  owners and run the following python script

```shell
python3 /path/to/evaluate.py --test-suites PATH_TO_TESTS --tools PATH_TO_JSON_FILE
```
* PATH_TO_TESTS shows the directory path containing test suites
* PATH_TO_JSON_FILE is the path of JSON formatted file which must be in the following format
```json
{
  "GitHub username of owner": "URL of GitHub repository to clone and test"
}
```
## Results

* A special result directory will be created after running `result_dir_%Y_%m_%d_%H_%M_%S`
* In that directory you can find
    * all tools with their results `result_dir/analyzer_dir/result_sarif_files`
    * the evaluated scores on test suites in JSON and Excel formatted files
