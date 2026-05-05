def run(context):
    logger = context["logger"]
    config = context["config_manager"]
    counter = config.read_json("executavel_state.json", {"execucoes": 0})
    counter["execucoes"] = counter.get("execucoes", 0) + 1
    config.write_json("executavel_state.json", counter)
    logger.info(f"Executável de exemplo chamado {counter['execucoes']} vez(es).")
    return {
        "status": "ok",
        "message": "Script executavel.py concluído.",
        "execucoes": counter["execucoes"],
    }
