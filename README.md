# Resume curator

This repository sets out to make resume curation easier.

## Data ingestion (input)

### Candidate data

The candidate's experiences will be populated in the `candidate_data/` directory as JSON files.

There are 4 such files:

- `candidate_data/experiences.json` (candidate's work experience)
- `candidate_data/education.json` (candidate's education)
- `candidate_data/projects.json` (candidate's personal projects)
- `candidate_data/metadata.json` (candidate's name, other personal data, extracurriculars)

### Job description

Job descriptions to create cvs for are located in the `job_descriptions/` directory.

There are "parsed" job descriptions that are json format, and raw job descriptions (`.txt`). Parsed jsons are located in `job_descriptions/parsed` and raw descriptions are in `job_descriptions/raw`.

The example `meta_engineer.json` can be edited (including the filename) to adhere to the candidates desired output cv. The filename will dictate the output filename of the generated cv.

## Output

The program will parse the data sources in order to generate a `n` page resume (default is 1 page) in the desired output format (defualt is `LateX`).

## Usage

The binary takes a set of optional positional arguments that can be found using the `--help` flag.

After running the curator, the output csvs will be found in the `resumes` directory.
