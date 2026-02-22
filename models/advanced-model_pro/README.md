---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- dense
- generated_from_trainer
- dataset_size:18600
- loss:CosineSimilarityLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: '

    Professional Summary:

    Experienced AI Engineer with strong background in software development.


    Skills:

    TensorFlow, Azure, Kubernetes, Flask, JavaScript, Pandas


    Experience:

    Worked on multiple projects using TensorFlow, Azure, Kubernetes, Flask.


    Projects:

    Developed real applications using TensorFlow, Azure, Kubernetes, Flask.


    Education:

    Bachelor degree in computer science.


    Additional experience in communication and teamwork.'
  sentences:
  - '

    We are hiring a DevOps Engineer.


    Required skills:

    NLP, Flask, AWS, Azure


    Nice to have:

    JavaScript


    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a Data Scientist.


    Required skills:

    Kubernetes, MySQL, Deep Learning


    Nice to have:

    MongoDB


    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a AI Engineer.


    Required skills:

    PostgreSQL, MySQL, Angular, Docker, Kubernetes


    Nice to have:

    NLP


    Responsibilities:

    Develop and maintain software systems.

    '
- source_sentence: '

    Professional Summary:

    Experienced Frontend Developer with strong background in software development.


    Skills:

    Flask, Kubernetes, Django, NLP, Java, Flask, MySQL


    Experience:

    Worked on multiple projects using Flask, Kubernetes, Django, NLP, Java.


    Projects:

    Developed real applications using Flask, Kubernetes, Django, NLP, Java.


    Education:

    Bachelor degree in computer science.

    '
  sentences:
  - '

    We are hiring a Backend Developer.


    Required skills:

    Deep Learning, Django, C++, Spring


    Nice to have:



    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a Frontend Developer.


    Required skills:

    Kubernetes, NLP, Django


    Nice to have:



    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a Software Engineer.


    Required skills:

    TensorFlow, Azure


    Nice to have:



    Responsibilities:

    Develop and maintain software systems.

    '
- source_sentence: '

    Professional Summary:

    Experienced DevOps Engineer with strong background in software development.


    Skills:

    Azure, Java, TensorFlow, Node.js, AWS, Spring, C++


    Experience:

    Worked on multiple projects using Azure, Java, TensorFlow, Node.js, AWS, Spring.


    Projects:

    Developed real applications using Azure, Java, TensorFlow, Node.js, AWS, Spring.


    Education:

    Bachelor degree in computer science.

    '
  sentences:
  - '

    We are hiring a Software Engineer.


    Required skills:

    Docker, Java, NLP, Pandas


    Nice to have:

    Django, Node.js


    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a Backend Developer.


    Required skills:

    Node.js, PostgreSQL, Machine Learning


    Nice to have:

    Python, Docker


    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a DevOps Engineer.


    Required skills:

    Python, TensorFlow, React, Docker, C++


    Nice to have:

    Kubernetes, JavaScript


    Responsibilities:

    Develop and maintain software systems.

    '
- source_sentence: '

    Professional Summary:

    Experienced Data Scientist with strong background in software development.


    Skills:

    Spring, MongoDB, MySQL, Angular, Machine Learning, JavaScript, SQL, React


    Experience:

    Worked on multiple projects using Spring, MongoDB, MySQL, Angular, Machine Learning.


    Projects:

    Developed real applications using Spring, MongoDB, MySQL, Angular, Machine Learning.


    Education:

    Bachelor degree in computer science.

    '
  sentences:
  - '

    We are hiring a AI Engineer.


    Required skills:

    MySQL, Django, Docker, Deep Learning


    Nice to have:



    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a Software Engineer.


    Required skills:

    Java, NumPy


    Nice to have:



    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a Data Scientist.


    Required skills:

    Spring, Machine Learning, Angular, MongoDB


    Nice to have:

    Azure


    Responsibilities:

    Develop and maintain software systems.

    '
- source_sentence: '

    Professional Summary:

    Experienced AI Engineer with strong background in software development.


    Skills:

    PyTorch, Docker, MongoDB, AWS, Deep Learning, C++, Pandas, Python, MongoDB


    Experience:

    Worked on multiple projects using PyTorch, Docker, MongoDB, AWS, Deep Learning,
    C++.


    Projects:

    Developed real applications using PyTorch, Docker, MongoDB, AWS, Deep Learning,
    C++.


    Education:

    Bachelor degree in computer science.

    '
  sentences:
  - '

    We are hiring a AI Engineer.


    Required skills:

    AWS, PyTorch, MongoDB


    Nice to have:

    NLP, PyTorch


    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a Frontend Developer.


    Required skills:

    NumPy, SQL, AWS, Node.js, C++


    Nice to have:



    Responsibilities:

    Develop and maintain software systems.

    '
  - '

    We are hiring a DevOps Engineer.


    Required skills:

    C++, Spring, Java, Docker, AWS


    Nice to have:

    C++, Spring


    Responsibilities:

    Develop and maintain software systems.

    '
pipeline_tag: sentence-similarity
library_name: sentence-transformers
metrics:
- pearson_cosine
- spearman_cosine
model-index:
- name: SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2
  results:
  - task:
      type: semantic-similarity
      name: Semantic Similarity
    dataset:
      name: validation
      type: validation
    metrics:
    - type: pearson_cosine
      value: 0.8753479606152781
      name: Pearson Cosine
    - type: spearman_cosine
      value: 0.8517546363133711
      name: Spearman Cosine
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 256, 'do_lower_case': False, 'architecture': 'BertModel'})
  (1): Pooling({'word_embedding_dimension': 384, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
  (2): Normalize()
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    '\nProfessional Summary:\nExperienced AI Engineer with strong background in software development.\n\nSkills:\nPyTorch, Docker, MongoDB, AWS, Deep Learning, C++, Pandas, Python, MongoDB\n\nExperience:\nWorked on multiple projects using PyTorch, Docker, MongoDB, AWS, Deep Learning, C++.\n\nProjects:\nDeveloped real applications using PyTorch, Docker, MongoDB, AWS, Deep Learning, C++.\n\nEducation:\nBachelor degree in computer science.\n',
    '\nWe are hiring a AI Engineer.\n\nRequired skills:\nAWS, PyTorch, MongoDB\n\nNice to have:\nNLP, PyTorch\n\nResponsibilities:\nDevelop and maintain software systems.\n',
    '\nWe are hiring a Frontend Developer.\n\nRequired skills:\nNumPy, SQL, AWS, Node.js, C++\n\nNice to have:\n\n\nResponsibilities:\nDevelop and maintain software systems.\n',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.7633, 0.1784],
#         [0.7633, 1.0000, 0.1210],
#         [0.1784, 0.1210, 1.0000]])
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Semantic Similarity

* Dataset: `validation`
* Evaluated with [<code>EmbeddingSimilarityEvaluator</code>](https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html#sentence_transformers.evaluation.EmbeddingSimilarityEvaluator)

| Metric              | Value      |
|:--------------------|:-----------|
| pearson_cosine      | 0.8753     |
| **spearman_cosine** | **0.8518** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 18,600 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                           | sentence_1                                                                         | label                                                          |
  |:--------|:-------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                               | string                                                                             | float                                                          |
  | details | <ul><li>min: 69 tokens</li><li>mean: 101.98 tokens</li><li>max: 149 tokens</li></ul> | <ul><li>min: 27 tokens</li><li>mean: 37.35 tokens</li><li>max: 57 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.49</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | sentence_1                                                                                                                                                                                                                    | label            |
  |:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code><br>Professional Summary:<br>Experienced Data Scientist with strong background in software development.<br><br>Skills:<br>NLP, Angular, MongoDB, C++, Node.js, NLP, PyTorch<br><br>Experience:<br>Worked on multiple projects using NLP, Angular, MongoDB, C++.<br><br>Projects:<br>Developed real applications using NLP, Angular, MongoDB, C++.<br><br>Education:<br>Bachelor degree in computer science.<br><br>Additional experience in communication and teamwork.</code>                                                                 | <code><br>We are hiring a Data Scientist.<br><br>Required skills:<br>Angular, MongoDB<br><br>Nice to have:<br>Node.js<br><br>Responsibilities:<br>Develop and maintain software systems.<br></code>                           | <code>1.0</code> |
  | <code><br>Professional Summary:<br>Experienced AI Engineer with strong background in software development.<br><br>Skills:<br>Node.js, Pandas, Python, MongoDB, JavaScript, C++, NumPy, Java, Python<br><br>Experience:<br>Worked on multiple projects using Node.js, Pandas, Python, MongoDB, JavaScript, C++.<br><br>Projects:<br>Developed real applications using Node.js, Pandas, Python, MongoDB, JavaScript, C++.<br><br>Education:<br>Bachelor degree in computer science.<br><br>Additional experience in communication and teamwork.</code> | <code><br>We are hiring a AI Engineer.<br><br>Required skills:<br>Node.js, Machine Learning, Pandas, Python, AWS<br><br>Nice to have:<br>Python<br><br>Responsibilities:<br>Develop and maintain software systems.<br></code> | <code>0.0</code> |
  | <code><br>Professional Summary:<br>Experienced Backend Developer with strong background in software development.<br><br>Skills:<br>NumPy, Node.js, MongoDB, Angular, Kubernetes, Deep Learning, Kubernetes, Java, Angular<br><br>Experience:<br>Worked on multiple projects using NumPy, Node.js, MongoDB, Angular, Kubernetes, Deep Learning.<br><br>Projects:<br>Developed real applications using NumPy, Node.js, MongoDB, Angular, Kubernetes, Deep Learning.<br><br>Education:<br>Bachelor degree in computer science.<br></code>               | <code><br>We are hiring a Backend Developer.<br><br>Required skills:<br>Node.js, NumPy<br><br>Nice to have:<br>C++<br><br>Responsibilities:<br>Develop and maintain software systems.<br></code>                              | <code>1.0</code> |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `eval_strategy`: steps
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `num_train_epochs`: 5
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `do_predict`: False
- `eval_strategy`: steps
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 5
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_ratio`: None
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `enable_jit_checkpoint`: False
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `use_cpu`: False
- `seed`: 42
- `data_seed`: None
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: -1
- `ddp_backend`: None
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `group_by_length`: False
- `length_column_name`: length
- `project`: huggingface
- `trackio_space_id`: trackio
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `auto_find_batch_size`: False
- `full_determinism`: False
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_num_input_tokens_seen`: no
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: True
- `use_cache`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss | validation_spearman_cosine |
|:------:|:----:|:-------------:|:--------------------------:|
| 0.4299 | 500  | 0.1086        | 0.8435                     |
| 0.8598 | 1000 | 0.0878        | 0.8424                     |
| 1.0    | 1163 | -             | 0.8483                     |
| 1.2898 | 1500 | 0.0852        | 0.8488                     |
| 1.7197 | 2000 | 0.0823        | 0.8493                     |
| 2.0    | 2326 | -             | 0.8497                     |
| 2.1496 | 2500 | 0.0790        | 0.8497                     |
| 2.5795 | 3000 | 0.0775        | 0.8495                     |
| 3.0    | 3489 | -             | 0.8505                     |
| 3.0095 | 3500 | 0.0788        | 0.8493                     |
| 3.4394 | 4000 | 0.0742        | 0.8505                     |
| 3.8693 | 4500 | 0.0765        | 0.8518                     |


### Framework Versions
- Python: 3.12.12
- Sentence Transformers: 5.2.3
- Transformers: 5.0.0
- PyTorch: 2.10.0+cu128
- Accelerate: 1.12.0
- Datasets: 4.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->