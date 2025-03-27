# Medical promptbase using MIMIC-Ext Abdomen Data

`promptbase` is an evolving collection of resources, best practices, and example scripts for eliciting the best performance from foundation models like `GPT-4`. We currently host scripts demonstrating the [`Medprompt` methodology](https://arxiv.org/abs/2311.16452), including examples of how we further extended this collection of prompting techniques ("`Medprompt+`") into non-medical domains: 

## Running Scripts

First, clone the repo and install the promptbase package:

```bash
cd src
pip install -e .
```
Before running the tests, you will need to download the datasets from the original sources (s3://hyperpod-input-datasets/AROA6GBMFKRI2VWQAUGYI:Amrin.Kareem@mbzuai.ac.ae/fil/mmlu_train_test.zip), rename it as mmlu and place it in the `src/promptbase/datasets` directory, so that the file structure is:  \

-src  
|--promptbase  
     |----datasets   
          |------mmlu  
               |--------train  
               |--------test

After downloading datasets and installing the promptbase package, you can run a test with:
 - Run with `python -m promptbase mmlu --subject <SUBJECT>` where `<SUBJECT>` is abdom, our new dataset.
`python -m promptbase dataset_name`


`python -m promptbase mmlu --subject abdom`

You will also need to set the following environment variables:
      - `OPENAI_API_KEY`






