import os
import re
import pathlib
from .globals import record, experience
from . import MMLU
from .embed_problems import embed_file
from .mmlu_paths import mmlu_data_dir, mmlu_generations_dir
import glob

# from globals import record, experience
# import MMLU
# from embed_problems import embed_file
# from mmlu_paths import mmlu_data_dir, mmlu_generations_dir

patients=5
model_name = "gpt-4-1106-preview"


def get_json_files(directory, dataset_name):
    # Regular expression pattern to match the desired file names
    pattern = re.compile(rf'mmlu_{dataset_name}_train_\d+\.json$')
    
    # Get all files in the directory
    files = os.listdir(directory)
    
    # Filter files that match the pattern
    json_files = [f for f in files if pattern.match(f)]

    json_files = sorted(json_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    return json_files

def get_json_files_without_gz(directory, dataset_name):
    # Regular expression pattern to match the desired .json and .json.gz file names
    pattern_json = re.compile(rf'mmlu_{dataset_name}_train_\d+\.json$')
    pattern_gz = re.compile(rf'mmlu_{dataset_name}_train_\d+\.json\.gz$')
    
    # Get all files in the directory
    files = os.listdir(directory)
    
    # Filter .json and .json.gz files
    json_files = {f for f in files if pattern_json.match(f)}
    gz_files = {f for f in files if pattern_gz.match(f)}
    
    # Convert .json.gz filenames to match corresponding .json filenames
    gz_files_matching = {f.replace('.json.gz', '.json') for f in gz_files}
    
    # Find .json files without a corresponding .json.gz
    json_without_gz = json_files - gz_files_matching

    # Sort the result naturally
    json_without_gz = sorted(json_without_gz, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    return json_without_gz


def generate_single(backend, scenario_id, save_path):
    save_path = os.path.normpath(save_path)  # Normalize the path (removes extra slashes)
    save_path =  os.path.basename(save_path)
    # dev_problem = f"mmlu_{dataset_name}_val"
    # train_problem = f"mmlu_{dataset_name}_train_{i}"
    json_file = f"{os.path.basename(save_path)}_{scenario_id}.json"
    train_problem = os.path.basename(json_file).split('.')[0]
    # patient_index = train_problem.split("_")[-1]
    # print(f"\n\n ########################### PROCESSING PATIENT {patient_index} ########################### \n\n")

    # print(train_problem)

  # if not os.path.exists(str(mmlu_data_dir / dev_problem) + ".json.gz"):
  #     embed_file(str(mmlu_data_dir / dev_problem) + ".json")

  ################CHANGED CODE STARTS HERE##################
  #@amrin: We only look at one patient at a time so the test problem has only one question at a time. We need to make this a loop to receive queries in real time and generate responses in real time.
    # if not os.path.exists(str(mmlu_data_dir / "train" / train_problem) + f"_{record+experience}" + ".json.gz"):
    #   embed_file(str(mmlu_data_dir / "train" / train_problem) + f"_{record+experience}" + ".json")

  # check if there are enough records and experience to retrieve examples
    # experience_pattern = os.path.join(mmlu_generations_dir, "expt", "train", save_path, "*", "experience.json.gz")
    # experience_paths = glob.glob(experience_pattern)
    # experience_paths_without_extension = [path.removesuffix(".json.gz") for path in experience_paths]

    # result_pattern = os.path.join(mmlu_generations_dir, "expt", "train", save_path, "*", "result.json.gz")
    # result_paths = glob.glob(result_pattern)
    # result_paths_without_extension = [path.removesuffix(".json.gz") for path in result_paths]

    # record_num = len(result_paths_without_extension)
    # experience_num = len(experience_paths_without_extension)

    # print(f"############################# RECORD: {record_num} | EXP: {experience_num} #############################")
    
    # if record_num < 3 and experience_num < 3:
    if True:
      # print("Not enough records and experience")
      MMLU.generate_solutions_without_rank(
      train_problem, run_name=f"train/{save_path}/{scenario_id}", model=model_name, backend=backend
      )
    elif record_num >= 3 and experience_num < 3:
      MMLU.run_cot_without_rank(
          train_problem,
          run_name=f"train/cot/{scenario_id}",
          examples=result_paths_without_extension,
          mode="knn",
          num_examples=3,
          num_repeat=15,
          max_thread=50,
          model=model_name,
          backend=backend
      )
    elif record_num < 3 and experience_num >= 3:
      MMLU.run_cot_without_rank(
          train_problem,
          run_name=f"train/cot/{scenario_id}",
          examples=experience_paths_without_extension,
          mode="knn",
          num_examples=3,
          num_repeat=15,
          max_thread=50,
          model=model_name,
          backend=backend
      )
    elif record_num >= 3 and experience_num < 3:
      MMLU.run_cot_without_rank(
          train_problem,
          run_name=f"train/cot/{scenario_id}",
          examples=result_paths_without_extension,
          mode="knn",
          num_examples=3,
          num_repeat=15,
          max_thread=50,
          model=model_name,
          backend=backend
      )
    else:
      paths_without_extension = experience_paths_without_extension + result_paths_without_extension

      MMLU.run_cot_without_rank(
          train_problem,
          run_name=f"train/cot/{scenario_id}",
          examples=paths_without_extension,
          mode="knn",
          num_examples=3,
          num_repeat=15,
          max_thread=50,
          model=model_name,
          backend=backend
      )
    # MMLU.run_cot_without_rank(
    #     test_problem,
    #     run_name=f"{test_problem}/cot_via_knn",
    #     mode="knn",
    #     num_examples=5,
    #     num_repeat=15,
    #     max_thread=50,
    #     model=model_name,
    # )

     ########EXAMPLES NEED TO COME FROM COMMON MEDICAL RECORD LIBRARY BASED ON K WHERE K IS THE NUMBER OF CASES IN THE LIBRARY########

    if False:
        # Logprobs not currently available in OpenAI API
        MMLU.run_logprobs(
            test_problem,
            run_name=f"{test_problem}/logprobs5",
            num_examples=5,
            num_repeat=10,
            max_thread=50,
            model=model_name,
        )


def generate(dataset_name: str):
    json_files = get_json_files(f"{mmlu_data_dir}/train/", dataset_name)
    print(len(json_files))
    # for i in range(1,patients):
    for i in range(len(json_files)):
    # dev_problem = f"mmlu_{dataset_name}_val"
      # train_problem = f"mmlu_{dataset_name}_train_{i}"
      train_problem = os.path.basename(json_files[i]).split('.')[0]
      patient_index = train_problem.split("_")[-1]
      print(f"\n\n ########################### PROCESSING PATIENT {patient_index} ########################### \n\n")

      print(train_problem)

    # if not os.path.exists(str(mmlu_data_dir / dev_problem) + ".json.gz"):
    #     embed_file(str(mmlu_data_dir / dev_problem) + ".json")

    ################CHANGED CODE STARTS HERE##################
    #@amrin: We only look at one patient at a time so the test problem has only one question at a time. We need to make this a loop to receive queries in real time and generate responses in real time.
      if not os.path.exists(str(mmlu_data_dir / "train" / train_problem) + ".json.gz"):
        embed_file(str(mmlu_data_dir / "train" / train_problem) + ".json")

    # check if there are enough records and experience to retrieve examples
      if record < 3 and experience < 3:
        print("Not enough records and experience")
        MMLU.generate_solutions_without_rank(
        train_problem, run_name="train/cot", model=model_name
        )
      elif record < 3 and experience >= 3:
        MMLU.run_cot_without_rank(
            train_problem,
            run_name="train/cot_knn",
            examples=str(
                mmlu_generations_dir / f"expt" / "train" / "cot_knn" / "experience"
            ),
            mode="knn",
            num_examples=3,
            num_repeat=15,
            max_thread=50,
            model=model_name,
        )
      elif record >= 3 and experience < 3:
        MMLU.run_cot_without_rank(
            train_problem,
            run_name="train/cot_knn",
            examples=str(
                mmlu_generations_dir / f"expt" / "train" / "cot_knn" / "result"
            ),
            mode="knn",
            num_examples=3,
            num_repeat=15,
            max_thread=50,
            model=model_name,
        )
      else:
        MMLU.run_cot_without_rank(
            train_problem,
            run_name="train/cot_knn",
            examples=[str(
                mmlu_generations_dir / f"expt" / f"train" / "cot_knn" / "result"),
             str(mmlu_generations_dir / f"expt" / "train" / "cot_knn" / "experience")],
            mode="knn",
            num_examples=3,
            num_repeat=15,
            max_thread=50,
            model=model_name,
        )
    # MMLU.run_cot_without_rank(
    #     test_problem,
    #     run_name=f"{test_problem}/cot_via_knn",
    #     mode="knn",
    #     num_examples=5,
    #     num_repeat=15,
    #     max_thread=50,
    #     model=model_name,
    # )

     ########EXAMPLES NEED TO COME FROM COMMON MEDICAL RECORD LIBRARY BASED ON K WHERE K IS THE NUMBER OF CASES IN THE LIBRARY########

    if False:
        # Logprobs not currently available in OpenAI API
        MMLU.run_logprobs(
            test_problem,
            run_name=f"{test_problem}/logprobs5",
            num_examples=5,
            num_repeat=10,
            max_thread=50,
            model=model_name,
        )


def generate_file(json_path: str):
  test_problem = os.path.basename(json_path).split('.')[0]
  print(test_problem)

################CHANGED CODE STARTS HERE##################
#@amrin: We only look at one patient at a time so the test problem has only one question at a time. We need to make this a loop to receive queries in real time and generate responses in real time.
  if not os.path.exists(json_path.split('.')[-2] + ".json.gz"):
    embed_file(json_path.split('.')[-2] + ".json")

# check if there are enough records and experience to retrieve examples
  # if record < 3 and experience < 3:
  #   print("Not enough records and experience")
  # MMLU.generate_solutions_without_rank(
  # test_problem, run_name="train/cot", model=model_name, subset_type="test"
  # )
  # elif record < 3 and experience >= 3:
  #   MMLU.run_cot_without_rank(
  #       test_problem,
  #       run_name="train/cot_knn",
  #       examples=str(
  #           mmlu_generations_dir / f"expt" / "train" / "cot_knn" / "experience"
  #       ),
  #       mode="knn",
  #       num_examples=3,
  #       num_repeat=15,
  #       max_thread=50,
  #       model=model_name,
  #   )
  # elif record >= 3 and experience < 3:
  #   MMLU.run_cot_without_rank(
  #       test_problem,
  #       run_name="train/cot_knn",
  #       examples=str(
  #           mmlu_generations_dir / f"expt" / "train" / "cot_knn" / "result"
  #       ),
  #       mode="knn",
  #       num_examples=3,
  #       num_repeat=15,
  #       max_thread=50,
  #       model=model_name,
  #   )
  # else:
  MMLU.run_cot_without_rank(
      test_problem,
      run_name="train/cot_knn",
      examples=[str(
          mmlu_generations_dir / f"expt" / f"train" / "cot_knn" / "result"),
        str(mmlu_generations_dir / f"expt" / "train" / "cot_knn" / "experience")],
      mode="knn",
      num_examples=3,
      num_repeat=15,
      max_thread=50,
      model=model_name,
      subset_type="test"
  )
  # MMLU.run_cot_without_rank(
  #     test_problem,
  #     run_name=f"{test_problem}/cot_via_knn",
  #     mode="knn",
  #     num_examples=5,
  #     num_repeat=15,
  #     max_thread=50,
  #     model=model_name,
  #     subset_type="test"
  # )

    ########EXAMPLES NEED TO COME FROM COMMON MEDICAL RECORD LIBRARY BASED ON K WHERE K IS THE NUMBER OF CASES IN THE LIBRARY########

  if False:
      # Logprobs not currently available in OpenAI API
      MMLU.run_logprobs(
          test_problem,
          run_name=f"{test_problem}/logprobs5",
          num_examples=5,
          num_repeat=10,
          max_thread=50,
          model=model_name,
      )