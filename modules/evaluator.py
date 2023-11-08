import pandas as pd
import subprocess
import datetime
import hashlib
import json
import os

from parsers.source_parser import SourceParser
from parsers.source_parser import Function
from parsers.result_parser import Report, ResultParser


class Accuracy:
    def __init__(self, true_reports_num: int, received_reports_num: int,
                 bad_functions_num: int, good_functions_num: int) -> None:
        self.__tp_num = true_reports_num
        self.__fp_num = received_reports_num - self.__tp_num
        self.__tn_num = good_functions_num - self.__fp_num
        self.__fn_num = bad_functions_num - self.__tp_num
        self.__set_zero_if_neg()

    def true_positive_num(self) -> int:
        return self.__tp_num

    def false_positive_num(self) -> int:
        return self.__fp_num

    def true_negative_num(self) -> int:
        return self.__tn_num

    def false_negative_num(self) -> int:
        return self.__fn_num

    def true_positive_rate(self) -> float:
        return 100 * self.__tp_num / (self.__tp_num + self.__fn_num)

    def false_positive_rate(self) -> float:
        return 100 * self.__fp_num / (self.__fp_num + self.__tn_num)

    def true_negative_rate(self) -> float:
        return 100 * self.__tn_num / (self.__tn_num + self.__fp_num)

    def false_negative_rate(self) -> float:
        return 100 * self.__fn_num / (self.__fn_num + self.__tp_num)

    def f1_score(self) -> float:
        return self.__tp_num / (self.__tp_num + (self.__fp_num + self.__fn_num) / 2)

    def __set_zero_if_neg(self) -> None:
        if self.__tp_num < 0:
            self.__tp_num = 0
        if self.__tn_num < 0:
            self._tn_count = 0
        if self.__fp_num < 0:
            self.__fp_num = 0
        if self.__fn_num < 0:
            self.__fn_num = 0


# we expect that in sources each function may contain only less than one error
class Evaluator:
    def __init__(self, true_reports: list, received_reports: list,
                 src_functions: list) -> None:
        self.__true_reports = true_reports
        self.__received_reports = received_reports
        self.__src_functions = src_functions
        self.__bad_functions = []
        self.__good_functions = []

        self.__evaluated = False
        self.__accuracy = None
        self.__weighted_score = -1

    def accuracy(self) -> Accuracy:
        self.__evaluate()
        return self.__accuracy

    def average_score(self) -> float:
        self.__evaluate()
        self.__evaluate_weighted_score()
        return round(self.__weighted_score, 4)

    @staticmethod
    def get_intersection(first: list, second: list) -> list:
        intersection = []
        for cur_el in first:
            if cur_el in second:
                intersection.append(cur_el)

        return intersection

    def __evaluate(self) -> None:
        if self.__evaluated:
            return

        self.__tp_results = Evaluator.get_intersection(self.__true_reports, self.__received_reports)
        self.__collect_bad_functions()
        self.__collect_good_functions()
        self.__accuracy = Accuracy(true_reports_num=len(self.__tp_results),
                                   received_reports_num=len(self.__received_reports),
                                   bad_functions_num=len(self.__bad_functions),
                                   good_functions_num=len(self.__good_functions))

        self.__evaluated = True

    def __collect_bad_functions(self) -> None:
        for report in self.__true_reports:
            for location in report.locations():
                file_path = SourceParser.get_path_from_uri(location.uri())
                function = SourceParser.get_parent_function(
                    src_functions=self.__src_functions, file_path=file_path,
                    line=location.start_line())

                SourceParser.add_in_list(function=function, src_functions=self.__bad_functions)

    def __collect_good_functions(self) -> None:
        for function in self.__src_functions:
            if function not in self.__bad_functions:
                SourceParser.add_in_list(function=function, src_functions=self.__good_functions)

    def __evaluate_weighted_score(self) -> None:
        if self.__weighted_score != -1:
            return

        src_to_true = Report.get_dict_by_source_name(self.__true_reports)
        src_to_received = Report.get_dict_by_source_name(self.__received_reports)
        src_to_bad = Function.get_dict_by_source_name(self.__bad_functions)
        src_to_good = Function.get_dict_by_source_name(self.__good_functions)
        self.__weighted_score = 0

        for src_name, true_reports in src_to_true.items():
            received_reports = src_to_received[src_name] if src_name in src_to_received else []

            true_rep_num = len(Evaluator.get_intersection(true_reports, received_reports))
            bad_func_num = len(src_to_bad[src_name]) if src_name in src_to_bad else 0
            good_func_num = len(src_to_good[src_name]) if src_name in src_to_good else 0
            tmp_accuracy = (
                Accuracy(true_reports_num=true_rep_num, received_reports_num=len(received_reports),
                         bad_functions_num=bad_func_num, good_functions_num=good_func_num))

            tmp_score = tmp_accuracy.f1_score() * Evaluator.__get_weight(src_name)
            self.__weighted_score += tmp_score

    @staticmethod
    def __get_weight(src_name: str) -> int:
        coefficient_dict = {"EASY": 1, "MEDIUM": 2, "HARD": 3}
        key_val = (src_name.split('_')[-1]).split('0')[0]
        if key_val in coefficient_dict:
            return coefficient_dict[key_val]

        return 1


class Sensitivities:
    def __init__(self, context: bool, field: bool,
                 flow: bool, path: bool) -> None:
        self.__context = self.__bool_to_str(context)
        self.__field = self.__bool_to_str(field)
        self.__flow = self.__bool_to_str(flow)
        self.__path = self.__bool_to_str(path)

    @staticmethod
    def __bool_to_str(b: bool) -> str:
        if b:
            return "Yes"
        return "No"

    def update(self, other) -> None:
        if isinstance(other, Sensitivities):
            self.__context = self.__context and other.__context
            self.__field = self.__field and other.__field
            self.__flow = self.__flow and other.__flow
            self.__path = self.__path and other.__path

    def to_dict(self):
        return {
            "context": self.__context,
            "field": self.__field,
            "flow": self.__flow,
            "path": self.__path
        }


class EvaluatorRunner:
    EXP_REPORT_NAME = "expected_reports.sarif"
    INNER_RES_NAME = "result_sarif_files"
    BC_FILES_NAME = "bitcode_files"
    SCORE_KEY = "score"
    CONTEXT_KEY = "context"
    FIELD_KEY = "field"
    FLOW_KEY = "flow"
    PATH_KEY = "path"
    C_ENGINE = "podman"
    PARTICIPANT_KEY = "participant"
    SENSITIVITIES_KEY = "sensitivities"
    RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
    BC_GEN_SCRIPT = os.path.join(RESOURCES_DIR, "get_all_bitcode_files.sh")
    RUNNER_NAME = "run_over_all_bc.sh"
    C_WD = "/root"
    RUNNER = os.path.join(RESOURCES_DIR, RUNNER_NAME)

    def __init__(self, test_suites_dir: str) -> None:
        self.__test_suites_dir = test_suites_dir

        self.__all_results_dir = "result_dir_" + self.__get_time_str()
        self.__scores = {}
        self.__sensitivities = {}
        self.__owner_to_results_dict = {}

    @staticmethod
    def __get_time_str() -> str:
        now = datetime.datetime.now()
        return now.strftime("%Y_%m_%d_%H_%M_%S")

    def run_all(self, owner_to_url_dict: dict) -> None:
        self.__save_results(owner_to_url_dict)
        self.__evaluate_scores()
        self.__evaluate_sensitivities()

    def __save_results(self, owner_to_url_dict: dict) -> None:
        bc_dir = os.path.join(self.__all_results_dir, self.BC_FILES_NAME)
        os.makedirs(bc_dir)
        self.__run("bash " + self.BC_GEN_SCRIPT + " " + self.__test_suites_dir + " " + bc_dir)

        cont_image_list = []
        for owner, url in owner_to_url_dict.items():
            cloned_repo_name = os.path.splitext(os.path.basename(url))[0]
            unique_name = self.__get_hash(url) + self.__get_time_str()
            cont_image_list.append(unique_name)
            try:
                c_wd = unique_name + ":" + self.C_WD
                self.__run("export GIT_TERMINAL_PROMPT=0")
                self.__run(cmd="git clone " + url, cwd=self.__all_results_dir)
                path_to_repo = os.path.join(self.__all_results_dir, cloned_repo_name)
                self.__run(self.C_ENGINE + " build -t " + unique_name + " " + path_to_repo)
                self.__run(self.C_ENGINE + " run --name " + unique_name + " -di " + unique_name)
                self.__run(self.C_ENGINE + " cp " + self.RUNNER + " " + c_wd)
                self.__run(self.C_ENGINE + " cp " + bc_dir + " " + c_wd)

                runner_in_c = os.path.join(self.C_WD, self.RUNNER_NAME)
                bc_dir_in_c = os.path.join(self.C_WD, self.BC_FILES_NAME)
                res_in_c = os.path.join(self.C_WD, self.INNER_RES_NAME)

                self.__run(self.C_ENGINE + " exec " + unique_name + " bash -c \'bash "
                           + runner_in_c + " " + bc_dir_in_c + " " + res_in_c + "\'")
                self.__run(
                    self.C_ENGINE + " cp " + unique_name + ":" + res_in_c + " " + path_to_repo)

                res_path = os.path.join(path_to_repo, self.INNER_RES_NAME)
                self.__owner_to_results_dict[owner] = res_path
            except subprocess.CalledProcessError:
                print(f"error occurred when trying to get results of {owner}")

        self.__clean_cont_images(cont_image_list)

    @staticmethod
    def __run(cmd: str, cwd: str = None) -> None:
        subprocess.run(args=cmd, shell=True, check=True, cwd=cwd)

    @staticmethod
    def __clean_cont_images(cont_image_list: list) -> None:
        for tmp_name in cont_image_list:
            try:
                EvaluatorRunner.__run(EvaluatorRunner.C_ENGINE + " rm -f " + tmp_name)
                EvaluatorRunner.__run(EvaluatorRunner.C_ENGINE + " image rm -f " + tmp_name)
            except subprocess.CalledProcessError:
                pass

    @staticmethod
    def __get_hash(url: str) -> str:
        h_obj = hashlib.sha256()
        h_obj.update(url.encode("utf-8"))
        return str(h_obj.hexdigest())[:16]

    def __evaluate_scores(self) -> None:
        subname = "testcases"
        source_dir = os.path.join(self.__test_suites_dir, subname)
        source_parser = SourceParser(source_dir)
        src_functions = source_parser.functions()

        exp_res_parser = ResultParser(
            res_path=os.path.join(source_dir, self.EXP_REPORT_NAME),
            prefix_in_report_name="")
        exp_reports = exp_res_parser.get_all_reports()

        for owner, res_dir in self.__owner_to_results_dict.items():
            try:
                received_res_parser = ResultParser(res_path=res_dir, prefix_in_report_name=subname)

                received_reports = received_res_parser.get_all_reports()
                evaluator = Evaluator(true_reports=exp_reports, received_reports=received_reports,
                                      src_functions=src_functions)

                self.__scores[owner] = evaluator.average_score()

            except (ValueError, FileNotFoundError) as error:
                print(type(error).__name__, ": ", error)

    def __evaluate_sensitivities(self) -> None:
        subname = "sensitivities"
        source_dir = os.path.join(self.__test_suites_dir, subname)

        exp_res_parser = ResultParser(
            res_path=os.path.join(source_dir, self.EXP_REPORT_NAME),
            prefix_in_report_name="")
        exp_reports_dict = exp_res_parser.get_all_reports_dict()

        for owner, res_dir in self.__owner_to_results_dict.items():
            try:
                received_res_parser = ResultParser(res_path=res_dir, prefix_in_report_name=subname)
                received_reports_dict = received_res_parser.get_all_reports_dict()

                for report_type, exp_reports in exp_reports_dict.items():
                    rec_reports = []
                    if report_type in received_reports_dict:
                        rec_reports = received_reports_dict[report_type]

                    tmp_sensitivities = self.__get_sensitivities(
                        exp_reports=self.__get_dict_by_name(exp_reports),
                        rec_reports=self.__get_dict_by_name(rec_reports))

                    if owner in self.__sensitivities:
                        self.__sensitivities[owner].update(tmp_sensitivities)
                    else:
                        self.__sensitivities[owner] = tmp_sensitivities

            except (ValueError, FileNotFoundError) as error:
                print(type(error).__name__, ": ", error)

    @staticmethod
    def __get_sensitivities(exp_reports: dict, rec_reports: dict) -> Sensitivities:
        context_sensitive = False
        field_sensitive = False
        flow_sensitive = False
        path_sensitive = False

        for src_name, exp_report in exp_reports.items():
            rec_report = []
            if src_name in rec_reports:
                rec_report = rec_reports[src_name]

            tmp_sensitivity = EvaluatorRunner.__is_same_report_list(rec_report, exp_report)

            if "ContextSensitive" in src_name:
                context_sensitive = tmp_sensitivity
            elif "FieldSensitive" in src_name:
                field_sensitive = tmp_sensitivity
            elif "FlowSensitive" in src_name:
                flow_sensitive = tmp_sensitivity
            elif "PathSensitive" in src_name:
                path_sensitive = tmp_sensitivity

        return Sensitivities(context=context_sensitive, field=field_sensitive,
                             flow=flow_sensitive, path=path_sensitive)

    @staticmethod
    def __is_same_report_list(rep_list_1: list, rep_list_2: list) -> bool:
        if len(rep_list_1) != len(rep_list_2):
            return False

        for report in rep_list_1:
            if report not in rep_list_2:
                return False

        return True

    @staticmethod
    def __get_dict_by_name(reports_list: list) -> dict:
        reports = {}
        for report in reports_list:
            src_name = report.source_name()
            if src_name not in reports:
                reports[src_name] = [report]
            else:
                reports[src_name].append(report)

        return reports

    def save(self, save_sensitivities: bool) -> None:
        filename = os.path.join(self.__all_results_dir, "ratings")
        rates = self.__get_rates_list()
        if rates:
            self.__write_in_json(filename, rates, save_sensitivities)
            self.__write_in_excel(filename, rates, save_sensitivities)

        print(f"All results are stored in {self.__all_results_dir}")

    @staticmethod
    def __get_dict_only_scores(rates: list) -> dict:
        rates_dict = {}
        for rate in rates:
            rates_dict[rate[EvaluatorRunner.PARTICIPANT_KEY]] = rate[EvaluatorRunner.SCORE_KEY]

        return rates_dict

    def __get_rates_list(self) -> list:
        rates = []
        for owner, res_dir in self.__owner_to_results_dict.items():
            score = self.__scores.get(owner)
            sensitivities = (self.__sensitivities.get(owner)).to_dict()
            tool = {self.PARTICIPANT_KEY: owner, self.SCORE_KEY: score,
                    self.SENSITIVITIES_KEY: sensitivities}
            rates.append(tool)

        return rates

    def __write_in_excel(self, filename: str, rates: list, save_sensitivities: bool) -> None:
        names = []
        scores = []
        context_sensitivities = []
        field_sensitivities = []
        flow_sensitivities = []
        path_sensitivities = []

        self.__fill_lists(names=names, scores=scores, context_sensitivities=context_sensitivities,
                          field_sensitivities=field_sensitivities,
                          flow_sensitivities=flow_sensitivities,
                          path_sensitivities=path_sensitivities, rates=rates)
        filename = filename + ".xlsx"
        data_to_save = {"participant": names, "score": scores}
        if save_sensitivities:
            data_to_save["context sensitivity"] = context_sensitivities
            data_to_save["field sensitivity"] = field_sensitivities
            data_to_save["flow sensitivity"] = flow_sensitivities
            data_to_save["path sensitivity"] = path_sensitivities

        rates_df = pd.DataFrame(data_to_save)
        rates_df.to_excel(filename, index=False)

    def __fill_lists(self, names: list, scores: list, context_sensitivities: list,
                     field_sensitivities: list, flow_sensitivities: list,
                     path_sensitivities: list, rates: list) -> None:
        for rate in rates:
            names.append(rate[self.PARTICIPANT_KEY])
            scores.append((rate[self.SCORE_KEY]))

            sensitivities = rate[self.SENSITIVITIES_KEY]
            context_sensitivities.append(sensitivities[self.CONTEXT_KEY])
            field_sensitivities.append(sensitivities[self.FIELD_KEY])
            flow_sensitivities.append(sensitivities[self.FLOW_KEY])
            path_sensitivities.append(sensitivities[self.PATH_KEY])

    def __write_in_json(self, filename: str, rates: list, save_sensitivities: bool) -> None:
        if not save_sensitivities:
            rates = self.__get_dict_only_scores(rates)

        filename = filename + ".json"
        with open(filename, "w") as file_json:
            json.dump(rates, file_json, indent=4)
