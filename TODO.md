# What needs to be done

## CLI Interface

Create a cli interface for the program, so that the user can run either

`python3 job_description_parser.py --raw-file "job_descriptions/raw/name_of_job.txt"` that fills the corresponding file in `job_descriptions/parsed/name_of_job.json`.

Or

`python3 resume_curator.py --job-description "job_descriptions/parsed/name_of_job.json --ouptut-format latex --page-limit 1` that can parse various arguments for creating the corresponding resume from the parsed json.

## Job description parser

1. Decide on a "parsed" model for job descriptions (json) that divides the relevant information from the `.txt` into categories.

2. Using an LLM or smarter method, parse the non-parsed txt files into the parsed model defined by the previous step.

3. Outputs the relevant information into the `job_descriptions/parsed` directory.

4. (Optional) Sanity checks the json and warns on missing items that are common/important to be extracted. Also warns on hallucinated data from the parser (whatever is in the json must be found in the text file to some degree). Maybe include a "guesses" field for the json, if we want the LLM to do a web search on what is commonly desired from a company or whatever is on glassdoor etc.

## Resume parser

1. Create models for everything under `candidate_data` that the jsons should adhere to. Make sure the program can parse these files appropriately.

2. Create an output model (json?) for the resume, that will be the intermediary data structure before it gets parsed into its relevant file type (e.g LateX). Consider saving it as a json to `resumes/json/` or similar.

3. Implement a parser that parses the intemediary datatype for the resume into the desired file format. Start with a comfortable output format (ideally latex, but maybe to start use `.md` or `.txt`) and extract the relevant information.
