from typing import List

import pytest
import ray

import aphrodite
from aphrodite.lora.request import LoRARequest

from .conftest import cleanup

MODEL_PATH = "meta-llama/Llama-2-7b-hf"


def do_sample(llm: aphrodite.LLM, lora_path: str, lora_id: int) -> List[str]:
    prompts = [
        "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_74 (icao VARCHAR, airport VARCHAR)\n\n question: Name the ICAO for lilongwe international airport [/user] [assistant]",  # noqa: E501
        "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_11 (nationality VARCHAR, elector VARCHAR)\n\n question: When Anchero Pantaleone was the elector what is under nationality? [/user] [assistant]",  # noqa: E501
        "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_95 (one_mora VARCHAR, gloss VARCHAR, accented_mora VARCHAR)\n\n question: What is the one mora for a low tone mora with a gloss of /˩okiru/ [òkìɽɯ́]? [/user] [assistant]",  # noqa: E501
        "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE candidate (people_id VARCHAR, unsure_rate INTEGER); CREATE TABLE people (sex VARCHAR, people_id VARCHAR)\n\n question: which gender got the highest average uncertain ratio. [/user] [assistant]",  # noqa: E501
        "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_60 (pick INTEGER, former_wnba_team VARCHAR)\n\n question: What pick was a player that previously played for the Minnesota Lynx? [/user] [assistant]",  # noqa: E501
        "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_28138035_4 (womens_doubles VARCHAR, mens_singles VARCHAR)\n\n question: Name the women's doubles for werner schlager [/user] [assistant]"  # noqa: E501
    ]
    sampling_params = aphrodite.SamplingParams(temperature=0,
                                          max_tokens=256,
                                          stop=["[/assistant]"])
    outputs = llm.generate(
        prompts,
        sampling_params,
        lora_request=LoRARequest(str(lora_id), lora_id, lora_path)
        if lora_id else None)
    # Print the outputs.
    generated_texts: List[str] = []
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        generated_texts.append(generated_text)
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
    return generated_texts


@pytest.mark.parametrize("tp_size", [1, 2, 4])
def test_llama_lora(sql_lora_files, tp_size, num_gpus_available):
    if num_gpus_available < tp_size:
        pytest.skip(f"Not enough GPUs for tensor parallelism {tp_size}")

    llm = aphrodite.LLM(MODEL_PATH,
                   enable_lora=True,
                   max_num_seqs=16,
                   max_loras=4,
                   tensor_parallel_size=tp_size)

    expected_no_lora_output = [
        "\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_75 (icao VARCHAR, airport VARCHAR)\n\n question: Name the ICAO for lilongwe international airport [/user] [assistant]\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_76 (icao VARCHAR, airport VARCHAR)\n\n question: Name the ICAO for lilongwe international airport [/user] [assistant]\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_77 (icao VARCHAR, airport VARCHAR)\n\n question: Name the ICAO for lilongwe international airport [/user] [assistant]\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_78 (icao VARCHAR, airport VARCHAR)\n\n question: Name the ICAO for lilongwe international airport [/user]",  # noqa: E501
        " Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_11 (nationality VARCHAR, elector VARCHAR)\n\n question: When Anchero Pantaleone was the elector what is under nationality? ",  # noqa: E501
        "\n\n answer: 1\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_96 (one_mora VARCHAR, gloss VARCHAR, accented_mora VARCHAR)\n\n question: What is the one mora for a high tone mora with a gloss of /˧kot/ [kòt]? [/user] [assistant]\n\n answer: 2\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_97 (one_mora VARCHAR, gloss VARCHAR, accented_mora VARCHAR)\n\n question: What is the one mora for a high tone mora with a gloss of /˧kot/ [kòt]? [/user] [assistant]\n\n answer: 2\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_98 (one_mora VARCHAR, gloss VARCHAR, accented_mora VARCHAR)\n\n question: What is the one m",  # noqa: E501
        " Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE candidate (people_id VARCHAR, unsure_rate INTEGER); CREATE TABLE people (sex VARCHAR, people_id VARCHAR)\n\n question: which gender got the highest average uncertain ratio. ",  # noqa: E501
        " Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_60 (pick INTEGER, former_wnba_team VARCHAR)\n\n question: What pick was a player that previously played for the Minnesota Lynx? ",  # noqa: E501
        "\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_28138035_4 (womens_doubles VARCHAR, mens_singles VARCHAR)\n\n question: Name the women's doubles for werner schlager [/user] [assistant]\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_28138035_4 (womens_doubles VARCHAR, mens_singles VARCHAR)\n\n question: Name the women's doubles for werner schlager [/user] [assistant]\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_28138035_4 (womens_doubles VARCHAR, mens_singles VARCHAR)\n\n question: Name the women's doubles for werner schlager [/user] [assistant]\n\n [user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE",  # noqa: E501
    ]
    expected_lora_output = [
        "  SELECT icao FROM table_name_74 WHERE airport = 'lilongwe international airport' ",  # noqa: E501
        "  SELECT nationality FROM table_name_11 WHERE elector = 'anchero pantaleone' ",  # noqa: E501
        "  SELECT one_mora FROM table_name_95 WHERE gloss = 'low tone mora with a gloss of /˩okiru/' [òkìɽɯ́] AND accented_mora = 'low tone mora with a gloss of /˩okiru/' [òkìɽɯ́] ",  # noqa: E501
        "  SELECT sex FROM people WHERE people_id IN (SELECT people_id FROM candidate GROUP BY sex ORDER BY COUNT(people_id) DESC LIMIT 1) ",  # noqa: E501
        "  SELECT pick FROM table_name_60 WHERE former_wnba_team = 'Minnesota Lynx' ",  # noqa: E501
        "  SELECT womens_doubles FROM table_28138035_4 WHERE mens_singles = 'Werner Schlager' "  # noqa: E501
    ]

    print("lora adapter created")
    assert do_sample(llm, sql_lora_files, lora_id=0) == expected_no_lora_output

    print("lora 1")
    assert do_sample(llm, sql_lora_files, lora_id=1) == expected_lora_output

    print("no lora")
    assert do_sample(llm, sql_lora_files, lora_id=0) == expected_no_lora_output

    print("lora 2")
    assert do_sample(llm, sql_lora_files, lora_id=2) == expected_lora_output

    print("removing lora")


def test_llama_tensor_parallel_equality(sql_lora_files, num_gpus_available):
    if num_gpus_available < 4:
        pytest.skip("Not enough GPUs for tensor parallelism 4")

    llm_tp1 = aphrodite.LLM(MODEL_PATH,
                       enable_lora=True,
                       max_num_seqs=16,
                       max_loras=4,
                       tensor_parallel_size=1)
    output_tp1 = do_sample(llm_tp1, sql_lora_files, lora_id=1)

    del llm_tp1
    cleanup()

    llm_tp2 = aphrodite.LLM(MODEL_PATH,
                       enable_lora=True,
                       max_num_seqs=16,
                       max_loras=4,
                       tensor_parallel_size=2)
    output_tp2 = do_sample(llm_tp2, sql_lora_files, lora_id=1)

    del llm_tp2
    cleanup()

    assert output_tp1 == output_tp2

    llm_tp4 = aphrodite.LLM(MODEL_PATH,
                       enable_lora=True,
                       max_num_seqs=16,
                       max_loras=4,
                       tensor_parallel_size=4)
    output_tp4 = do_sample(llm_tp4, sql_lora_files, lora_id=1)

    del llm_tp4
    cleanup()

    assert output_tp1 == output_tp4


def test_llama_lora_warmup(sql_lora_files):
    """Test that the LLM initialization works with a warmup LORA path and
    is more conservative"""

    @ray.remote(num_gpus=1)
    def get_num_gpu_blocks_lora():
        llm = aphrodite.LLM(MODEL_PATH, enable_lora=True, max_num_seqs=16)
        num_gpu_blocks_lora_warmup = llm.llm_engine.cache_config.num_gpu_blocks
        return num_gpu_blocks_lora_warmup

    @ray.remote(num_gpus=1)
    def get_num_gpu_blocks_no_lora():
        llm = aphrodite.LLM(MODEL_PATH, max_num_seqs=16)
        num_gpu_blocks_no_lora_warmup = (
            llm.llm_engine.cache_config.num_gpu_blocks)
        return num_gpu_blocks_no_lora_warmup

    num_gpu_blocks_lora_warmup = ray.get(get_num_gpu_blocks_lora.remote())
    num_gpu_blocks_no_lora_warmup = ray.get(
        get_num_gpu_blocks_no_lora.remote())
    assert num_gpu_blocks_lora_warmup < num_gpu_blocks_no_lora_warmup, (
        "The warmup with lora should be more "
        "conservative than without lora, therefore the number of "
        "memory blocks for the KV cache should be "
        "less when using lora than when not using lora")
